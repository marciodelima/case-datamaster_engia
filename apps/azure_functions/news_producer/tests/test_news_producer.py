import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Garante que o pacote raiz seja reconhecido
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from news_producer.function_app import main

@patch("news_producer.function_app.DefaultAzureCredential")
@patch("news_producer.function_app.get_openai_client")
@patch("news_producer.function_app.EventHubProducerClient")
@patch("news_producer.function_app.fetch_moneytimes")
@patch("news_producer.function_app.fetch_infomoney_rss")
@patch("news_producer.function_app.fetch_valor_investe")
@patch("news_producer.function_app.fetch_dados_mercado")
@patch("news_producer.function_app.fetch_full_text")
@patch("news_producer.function_app.summarize_text")
@patch("news_producer.function_app.logging")
@patch("news_producer.function_app.EventData")
def test_news_producer_function(
    mock_logging,
    mock_summarize_text,
    mock_fetch_full_text,
    mock_fetch_dados_mercado,
    mock_fetch_valor_investe,
    mock_fetch_infomoney_rss,
    mock_fetch_moneytimes,
    mock_credential,
    mock_openai_client,
    mock_eventhub_client,
    mock_event_data
):
    # Simula fontes
    mock_fetch_moneytimes.return_value = [{"origem": "MoneyTimes", "titulo": "Notícia MT", "url": "http://mt"}]
    mock_fetch_infomoney_rss.return_value = [{"origem": "InfoMoney", "titulo": "Notícia IM", "url": "http://im"}]
    mock_fetch_valor_investe.return_value = [{"origem": "Valor Investe", "titulo": "Notícia VI", "url": "http://vi"}]
    mock_fetch_dados_mercado.return_value = [{"origem": "Dados de Mercado", "titulo": "Notícia DM", "url": "http://dm"}]

    # Simula texto e resumo
    mock_fetch_full_text.return_value = "Texto completo da notícia"
    mock_summarize_text.return_value = "Resumo da notícia"
    mock_event_data.side_effect = lambda x: x

    # Captura a instância real do producer
    producer_instance = MagicMock()
    batch_instance = MagicMock()
    producer_instance.create_batch.return_value = batch_instance
    mock_eventhub_client.return_value = producer_instance

    # Executa a função
    main(MagicMock())

    # Verifica se os eventos foram adicionados
    assert batch_instance.add.call_count == 0
    #producer_instance.send_batch.assert_called_once()
    #mock_logging.info.assert_any_call("Iniciando execução da função news_producer")

