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

O reasoner do MCP seleciona até três ferramentas por requisição e devolve um contexto consolidado. O gateway é o cliente MCP e chama o servidor pelo transporte Streamable HTTP em `MCP_URL` (padrão `http://localhost:8101/mcp`).

### LLM do MCP

O MCP usa `gpt-4o-mini` como padrão por oferecer boa qualidade em português, baixa latência e custo adequado para planejamento e síntese. O acesso é OpenAI-compatible e configurável sem segredo no código:

```bash
export OPENAI_API_KEY="..."
export LLM_MODEL="gpt-4o-mini"
export JUDGE_MODEL="gpt-4.1-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export MCP_SERVICE_TOKEN="gere-um-token-forte"
docker compose up --build
```

O LLM recebe apenas a pergunta e o contexto das ferramentas. Ele não chama a internet diretamente, não escolhe ferramentas fora da allowlist e não executa código. O planner retorna JSON validado, limitado a três ferramentas. Sem `OPENAI_API_KEY`, o MCP usa o planner determinístico e uma resposta de fallback.

Depois da síntese, um juiz independente (`gpt-4.1-mini`) avalia groundedness, presença de fontes, segurança e clareza. O limiar mínimo é `0.75`; respostas reprovadas são retidas e substituídas por uma mensagem segura. Se o juiz estiver indisponível, o retorno registra explicitamente o fallback em `judge.issues`.

### Autorização Gateway -> MCP

O MCP aceita somente requisições Streamable HTTP com:

```text
Authorization: Bearer <MCP_SERVICE_TOKEN>
```

O gateway injeta esse header usando `create_mcp_http_client`. O frontend nunca recebe esse token e a porta do MCP não é publicada pelo Compose, apenas exposta na rede interna `services`. Em produção, substitua o valor local por um segredo do Key Vault/secret manager e use um token forte, rotacionável e exclusivo por ambiente.

### Memória de chat

O Gateway é o único dono da memória de curto prazo. Cada requisição recebe `client_id` e `session_id`, e o Gateway mantém uma memória separada pela chave composta `(client_id, session_id)`. A memória possui no máximo 20 mensagens e TTL de 120 minutos.

O MCP é stateless: não armazena mensagens. Ele recebe somente o snapshot limitado e autorizado pelo Gateway, usa esse contexto durante a execução e o descarta ao finalizar a requisição. Isso evita estado duplicado, divergência e mistura de conversas.

O gateway devolve o `session_id` na resposta. A aplicação deve guardar esse valor durante a conversa e enviá-lo nas próximas chamadas do mesmo chat. Para um novo chat, gere um novo `session_id`.

## Segurança inicial

- Contratos Pydantic rejeitam campos inválidos.
- Tickers aceitos seguem o padrão B3 `.SA`.
- O gateway aplica guardrail de entrada contra prompt injection/jailbreak e limite de tamanho.
- O gateway valida o status, formato e observações do contexto antes de devolver a resposta.
- O MCP usa allowlist de ferramentas, seleção por regras explícitas e máximo de três ferramentas.
- Timeout de 10 segundos evita chamadas externas penduradas.
- Não há segredos hardcoded.

Autenticação, autorização por cliente, rate limiting, TLS e observabilidade devem ser adicionados na borda/API antes de exposição pública.
