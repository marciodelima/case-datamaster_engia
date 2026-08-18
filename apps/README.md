# Serviços FastAPI

A estrutura inicial separa responsabilidades:

- `agents/back-agent-*/agent.py`: lógica de cada ferramenta.
- `mcp/app.py`: MCP único com reasoner ReAct limitado e registro de ferramentas.
- `gateway/app.py`: guardrail de entrada, chamada do MCP e guardrail de saída.
- `backend/app.py`: API de negócio inicial.
- `backend/dataconnector/models.py`: contratos Pydantic compartilhados.

## Executar

### Docker Compose

Dentro do diretório `apps/`:

```bash
cd apps
docker compose up --build
```

Após a subida:

- Frontend: `http://localhost:8501`
- Gateway: `http://localhost:8100/docs`
- Backend e MCP ficam disponíveis apenas na rede interna do Compose.

Para executar em segundo plano:

```bash
cd apps
docker compose up --build -d
docker compose ps
docker compose logs -f gateway
docker compose down
```

### Execução local sem Docker

Na raiz `apps/`, usando o ambiente virtual do projeto:

```bash
uvicorn backend.app:app --reload --port 8000
uvicorn gateway.app:app --reload --port 8100
uvicorn mcp.app:app --reload --port 8101
```

O gateway aceita `POST /v1/agent/run` com:

```json
{
  "client_id": "Marcio",
  "message": "Mostre o preço e as notícias da PETR4",
  "ticker": "PETR4.SA",
  "parameters": {"period": "6mo"}
}
```

O reasoner do MCP seleciona até três ferramentas por requisição e devolve um contexto consolidado. O gateway chama o MCP em `MCP_URL` (padrão `http://localhost:8100/v1/context`); em execução local, configure `MCP_URL=http://localhost:8101/v1/context` para não conflitar com a porta do gateway.

### LLM do MCP

O MCP usa `gpt-4o-mini` como padrão por oferecer boa qualidade em português, baixa latência e custo adequado para planejamento e síntese. O acesso é OpenAI-compatible e configurável sem segredo no código:

```bash
export OPENAI_API_KEY="..."
export LLM_MODEL="gpt-4o-mini"
export JUDGE_MODEL="gpt-4.1-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
docker compose up --build
```

O LLM recebe apenas a pergunta e o contexto das ferramentas. Ele não chama a internet diretamente, não escolhe ferramentas fora da allowlist e não executa código. O planner retorna JSON validado, limitado a três ferramentas. Sem `OPENAI_API_KEY`, o MCP usa o planner determinístico e uma resposta de fallback.

Depois da síntese, um juiz independente (`gpt-4.1-mini`) avalia groundedness, presença de fontes, segurança e clareza. O limiar mínimo é `0.75`; respostas reprovadas são retidas e substituídas por uma mensagem segura. Se o juiz estiver indisponível, o retorno registra explicitamente o fallback em `judge.issues`.

## Segurança inicial

- Contratos Pydantic rejeitam campos inválidos.
- Tickers aceitos seguem o padrão B3 `.SA`.
- O gateway aplica guardrail de entrada contra prompt injection/jailbreak e limite de tamanho.
- O gateway valida o status, formato e observações do contexto antes de devolver a resposta.
- O MCP usa allowlist de ferramentas, seleção por regras explícitas e máximo de três ferramentas.
- Timeout de 10 segundos evita chamadas externas penduradas.
- Não há segredos hardcoded.

Autenticação, autorização por cliente, rate limiting, TLS e observabilidade devem ser adicionados na borda/API antes de exposição pública.
