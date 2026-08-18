"""OpenAI-compatible planning and synthesis client for the unified MCP."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

ALLOWED_TOOLS = {"portfolio", "market", "news", "ri", "web"}
SYSTEM_PROMPT = """Você é um consultor financeiro especialista em ações brasileiras.
Planeje respostas informativas, claras e objetivas, sem prometer retorno e sem emitir ordem personalizada.
Você pode selecionar somente ferramentas da lista permitida. Nunca invente fontes ou dados. Não responsa perguntas fora do escopo. Sempre justifique suas respostas com dados disponíveis e cite fontes.
"""


def _config() -> tuple[str | None, str, str]:
    return (
        os.getenv("OPENAI_API_KEY"),
        os.getenv("LLM_MODEL", "gpt-4o-mini"),
        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _chat(messages: list[dict[str, str]], response_format: bool = False, model: str | None = None) -> str | None:
    api_key, configured_model, base_url = _config()
    model = model or configured_model
    if not api_key:
        return None
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 700,
    }
    if response_format:
        payload["response_format"] = {"type": "json_object"}
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        return None


def plan_tools(message: str, ticker: str | None, explicit_intent: str | None) -> list[str] | None:
    if explicit_intent:
        return [explicit_intent]
    prompt = {
        "role": "user",
        "content": json.dumps(
            {
                "task": "Selecione as ferramentas necessárias para responder à pergunta.",
                "question": message,
                "ticker": ticker,
                "allowed_tools": sorted(ALLOWED_TOOLS),
                "output_schema": {"tools": ["portfolio|market|news|ri|web"]},
            },
            ensure_ascii=False,
        ),
    }
    raw = _chat([{"role": "system", "content": SYSTEM_PROMPT}, prompt], response_format=True)
    if not raw:
        return None
    try:
        tools = json.loads(raw).get("tools", [])
        if not isinstance(tools, list):
            return None
        selected = [tool for tool in tools if tool in ALLOWED_TOOLS]
        return selected[:3] or None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


def synthesize(message: str, observations: list[dict[str, Any]], sources: list[str]) -> str | None:
    context = {
        "question": message,
        "observations": observations,
        "sources": sources,
        "requirements": [
            "responder em português brasileiro",
            "ser claro e objetivo",
            "justificar a avaliação com os dados disponíveis",
            "listar fontes sem inventá-las",
            "incluir que o conteúdo não constitui recomendação financeira",
        ],
    }
    return _chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False, default=str)},
        ]
    )


def judge_response(
    message: str,
    answer: str,
    observations: list[dict[str, Any]],
    sources: list[str],
) -> dict[str, Any]:
    """Evaluate the generated answer with a separate judge model."""
    generator_model = model_name()
    judge_model = os.getenv("JUDGE_MODEL", "gpt-4.1-mini")
    if judge_model == generator_model:
        judge_model = "gpt-4.1-mini" if generator_model != "gpt-4.1-mini" else "gpt-4o-mini"

    context = {
        "question": message,
        "answer": answer,
        "observations": observations,
        "sources": sources,
        "criteria": {
            "grounded": "A resposta usa somente dados presentes nas observações e fontes.",
            "sources": "As afirmações relevantes têm fontes disponíveis e não há fontes inventadas.",
            "safe": "Não há promessa de retorno, ordem personalizada ou aconselhamento regulado.",
            "clear": "A resposta é objetiva, compreensível e em português brasileiro.",
        },
        "output_schema": {
            "approved": "boolean",
            "score": "number between 0 and 1",
            "issues": ["string"],
        },
    }
    raw = _chat(
        [
            {
                "role": "system",
                "content": "Você é um juiz independente de respostas financeiras. Avalie com rigor e não reescreva a resposta.",
            },
            {"role": "user", "content": json.dumps(context, ensure_ascii=False, default=str)},
        ],
        response_format=True,
        model=judge_model,
    )
    if not raw:
        return {
            "approved": True,
            "score": 0.5,
            "issues": ["Judge indisponível; fallback local aplicado."],
            "model": "fallback",
        }
    try:
        result = json.loads(raw)
        score = max(0.0, min(float(result.get("score", 0.0)), 1.0))
        issues = result.get("issues", [])
        if not isinstance(issues, list):
            issues = [str(issues)]
        return {
            "approved": bool(result.get("approved", False)) and score >= 0.75,
            "score": score,
            "issues": [str(issue) for issue in issues[:5]],
            "model": judge_model,
        }
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return {
            "approved": False,
            "score": 0.0,
            "issues": ["Judge retornou um formato inválido."],
            "model": judge_model,
        }


def model_name() -> str:
    return _config()[1]


def judge_model_name() -> str:
    generator_model = model_name()
    configured = os.getenv("JUDGE_MODEL", "gpt-4.1-mini")
    return configured if configured != generator_model else ("gpt-4.1-mini" if generator_model != "gpt-4.1-mini" else "gpt-4o-mini")
