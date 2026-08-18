import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from urllib.parse import quote

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from ri_collector.function_app import (
    get_secret_client,
    get_postgres_connection_string,
    main
)

@patch.dict(os.environ, {"KEYVAULT_URI": "https://fake-vault.vault.azure.net/"})
@patch("ri_collector.function_app.DefaultAzureCredential")
@patch("ri_collector.function_app.SecretClient")
def test_get_secret_client(mock_secret, mock_cred):
    client = get_secret_client()
    assert mock_secret.called
    assert client is not None

def test_get_postgres_connection_string_formatting():
    mock_secret_client = MagicMock()
    raw_dsn = (
        "Host=localhost;Port=5432;Database=testdb;User Id=admin;"
        "Password=secret;Ssl Mode=Require"
    )
    mock_secret_client.get_secret.return_value.value = quote(raw_dsn)

    conn_str = get_postgres_connection_string(mock_secret_client)
    assert "host=localhost" in conn_str
    assert "sslmode=require" in conn_str
    assert "dbname=testdb" in conn_str

@patch.dict(os.environ, {
    "KEYVAULT_URI": "https://fake-vault.vault.azure.net/",
    "STORAGE_URL": "https://fake.blob.core.windows.net/"
})
@patch("ri_collector.function_app.DefaultAzureCredential")
@patch("ri_collector.function_app.SecretClient")
@patch("ri_collector.function_app.psycopg2.connect")
@patch("ri_collector.function_app.BlobServiceClient")
@patch("ri_collector.function_app.requests.get")
def test_main_success(
    mock_requests,
    mock_blob,
    mock_psycopg2,
    mock_secret,
    mock_cred
):
    # Simula retorno do segredo
    mock_secret_instance = MagicMock()
    mock_secret_instance.get_secret.return_value.value = quote(
        "Host=localhost;Port=5432;Database=testdb;User Id=admin;Password=secret;Ssl Mode=Require"
    )
    mock_secret.return_value = mock_secret_instance

    # Simula retorno do banco
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("BBAS3", "https://example.com/ri.pdf")]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.return_value = mock_conn

    # Simula resposta HTTP
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/octet-stream"}
    mock_response.content = b"%PDF-1.4 fake content" + b"0" * 200
    mock_requests.return_value = mock_response

    # Simula blob
    mock_container = MagicMock()
    mock_blob.return_value.get_container_client.return_value = mock_container

    main(None)

