import os
import sys
import json
import pandas as pd
from unittest.mock import patch, MagicMock

# Ajusta o caminho para importar a função
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from ri_resumer.function_app import main

@patch("ri_resumer.function_app.fitz.open")
@patch("ri_resumer.function_app.AzureOpenAI")
@patch("ri_resumer.function_app.BlobServiceClient")
@patch("ri_resumer.function_app.DefaultAzureCredential")
@patch("ri_resumer.function_app.SecretClient")
def test_ri_resumer_success(
    mock_secret_client_class,
    mock_default_cred,
    mock_blob_service_class,
    mock_openai_class,
    mock_fitz_open
):
    # Simula PDF com texto extraído
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [MagicMock(get_text=lambda: "Texto do relatório")]
    mock_fitz_open.return_value = mock_doc

    # Simula retorno do SecretClient
    mock_secret_client = MagicMock()
    mock_secret_client.get_secret.side_effect = [
        MagicMock(value="fake-openai-key"),
        MagicMock(value="https://fake-endpoint.openai.azure.com")
    ]
    mock_secret_client_class.return_value = mock_secret_client

    # Simula resposta do OpenAI
    mock_openai = MagicMock()
    mock_openai.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "empresa": "PETR4",
            "trimestre": "2T25",
            "avaliacoes": {"financeiro": "bom"},
            "nota_final": 8.5
        })))
    ]
    mock_openai_class.return_value = mock_openai

    # Simula Blob Storage
    mock_blob_client = MagicMock()
    mock_blob_client.download_blob.return_value.readall.return_value = b"%PDF-1.4 fake content"
    mock_container = MagicMock()
    mock_container.list_blobs.return_value = [
        MagicMock(name="raw/ri/PETR4/PETR4-ri.pdf")
    ]
    mock_container.get_blob_client.return_value = mock_blob_client
    mock_blob_service = MagicMock()
    mock_blob_service.get_container_client.return_value = mock_container
    mock_blob_service_class.return_value = mock_blob_service

    # Executa a função
    main(None)

def test_extract_text_from_pdf():
    from ri_resumer.function_app import extract_text
    import fitz

    # cria um PDF em memória
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Texto de teste")
    pdf_bytes = doc.write()
    doc.close()

    texto = extract_text(pdf_bytes)
    assert "Texto de teste" in texto

