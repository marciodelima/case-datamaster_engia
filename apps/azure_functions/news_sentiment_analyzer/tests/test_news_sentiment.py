import os
import sys
import json
import pandas as pd
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from news_sentiment_analyzer.function_app import analyze_news, get_openai_client, eventhub_trigger

def test_analyze_news_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"acoes": ["PETR4"], "sentimento": "positivo", "resumo": "Alta do petroleo"}'))]
    mock_client.chat.completions.create.return_value = mock_response

    result = analyze_news("Petrobras sobe", "Alta no preço do petroleo", mock_client)
    assert result["acoes"] == ["PETR4"]
    assert result["sentimento"] == "positivo"
    assert "resumo" in result

def test_analyze_news_fallback_on_error():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Erro simulado")
    result = analyze_news("Petrobras", "Texto", mock_client)
    assert result == {"acoes": ["NA"], "sentimento": "neutro", "resumo": "Sem resumo"}

@patch("news_sentiment_analyzer.function_app.get_openai_client")
@patch("news_sentiment_analyzer.function_app.BlobServiceClient")
@patch("news_sentiment_analyzer.function_app.DefaultAzureCredential")
def test_eventhub_trigger(mock_cred, mock_blob, mock_openai):
    mock_event = MagicMock()
    mock_event.get_body.return_value = '{"titulo": "Petrobras", "conteudo": "Alta no petróleo"}'.encode("utf-8")
    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content='{"acoes": ["PETR4"], "sentimento": "positivo", "resumo": "Alta do petróleo"}'))
    ]

    mock_container = MagicMock()
    mock_blob.return_value.get_container_client.return_value = mock_container

    eventhub_trigger([mock_event])

@patch("news_sentiment_analyzer.function_app.SecretClient")
@patch("news_sentiment_analyzer.function_app.DefaultAzureCredential")
@patch.dict(os.environ, {"KEYVAULT_URI": "https://fake-vault.vault.azure.net/"})
def test_get_openai_client(mock_cred, mock_secret):
    mock_secret_instance = MagicMock()
    mock_secret_instance.get_secret.side_effect = [
        MagicMock(value="fake-key"),
        MagicMock(value="https://fake-endpoint")
    ]
    mock_secret.return_value = mock_secret_instance

    client = get_openai_client()

@patch("news_sentiment_analyzer.function_app.get_openai_client")
@patch("news_sentiment_analyzer.function_app.BlobServiceClient")
@patch("news_sentiment_analyzer.function_app.DefaultAzureCredential")
def test_eventhub_trigger_empty(mock_cred, mock_blob, mock_openai):
    mock_event = MagicMock()
    mock_event.get_body.return_value = b'{}'  # sem título ou conteúdo

    mock_container = MagicMock()
    mock_blob.return_value.get_container_client.return_value = mock_container

    eventhub_trigger([mock_event])
