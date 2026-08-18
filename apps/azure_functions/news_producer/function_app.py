import os
import logging
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI
import feedparser
import azure.functions as func

def get_openai_client():
    credential = DefaultAzureCredential()
    vault_url = os.environ["KEYVAULT_URI"]
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    api_key = secret_client.get_secret("OpenAI-Key").value
    endpoint = secret_client.get_secret("OpenAI-Endpoint").value

    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version="2023-07-01-preview"
    )

def summarize_text(text, client):
    prompt = f"Resuma em uma frase simples e objetiva a seguinte notícia:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.warning(f"Erro ao resumir texto: {e}")
        return text[:100] + "..."

def fetch_moneytimes():
    html = requests.get("https://www.moneytimes.com.br/ultimas-noticias/").text
    soup = BeautifulSoup(html, "html.parser")
    return [
        {
            "origem": "MoneyTimes",
            "titulo": a.select_one("h2").text.strip(),
            "url": a.select_one("a")["href"]
        }
        for a in soup.select("article")[:5]
    ]

def fetch_infomoney_rss():
    feed = feedparser.parse("https://www.infomoney.com.br/feed/")
    return [
        {
            "origem": "InfoMoney",
            "titulo": entry.title,
            "url": entry.link
        }
        for entry in feed.entries[:5]
    ]

def fetch_valor_investe():
    html = requests.get("https://valorinveste.globo.com/ultimas-noticias/").text
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.feed-post-body")
    return [
        {
            "origem": "Valor Investe",
            "titulo": card.select_one("a").text.strip(),
            "url": card.select_one("a")["href"]
        }
        for card in cards[:5]
    ]

def fetch_dados_mercado():
    html = requests.get("https://www.dadosdemercado.com.br/ultimas-noticias").text
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div.card-body")
    return [
        {
            "origem": "Dados de Mercado",
            "titulo": item.select_one("h5").text.strip(),
            "url": item.select_one("a")["href"]
        }
        for item in items[:5]
    ]

def fetch_full_text(url):
    try:
        html = requests.get(url, timeout=10, verify=False).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.select("p")
        return "\n".join(p.text.strip() for p in paragraphs if len(p.text.strip()) > 40)
    except Exception as e:
        logging.warning(f"Erro ao extrair texto de {url}: {e}")
        return ""

app = func.FunctionApp()

@app.function_name(name="news_producer")
@app.schedule(schedule="0 */15 8-19 * * 1-5", arg_name="mytimernews", run_on_startup=True, use_monitor=True)
def main(mytimernews: func.TimerRequest) -> None:
    logging.info("Iniciando execução da função news_producer")
    try:
        credential = DefaultAzureCredential()
        client = get_openai_client()

        producer = EventHubProducerClient(
            fully_qualified_namespace=os.environ["EVENTHUB_NAMESPACE"],
            eventhub_name=os.environ["EVENTHUB_NAME"],
            credential=credential
        )

        fontes = (
            fetch_moneytimes() +
            fetch_infomoney_rss() +
            fetch_valor_investe() +
            fetch_dados_mercado()
        )

        batch = producer.create_batch()

        for item in fontes:
            texto = fetch_full_text(item["url"])
            if not texto:
                continue

            news = {
                "origem": item["origem"],
                "titulo": texto[:100] + "...",
                "conteudo": texto,
                "url": item["url"],
                "acao_relacionada": None
            }
            logging.info(json.dumps(news))
            batch.add(EventData(json.dumps(news)))

        producer.send_batch(batch)
        logging.info(f"{len(batch)} notícias enviadas ao Event Hub.")

    except Exception as e:
        logging.error(f"Erro na função news_producer: {e}")


