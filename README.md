# VEGA — Copiloto de Vendas com IA

Assistente de vendas especializado em loja gamer. Apoia o vendedor humano com análise de perfil, scripts de pitch, quebra de objeções, cross-sell e estratégia de ancoragem — tudo gerado por IA em tempo real.

## Arquitetura

```
frontend/   Vue 3 + Vite (interface do vendedor)
backend/    FastAPI + Groq (motor de IA)
```

## Setup rápido

### Backend

```bash
cd backend
cp .env.example .env
# Coloque sua GROQ_API_KEY no .env
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse em `http://localhost:5173`.

## Prompts prontos disponíveis

| Preset | Descrição |
|---|---|
| Atendimento Padrão | Análise completa: perfil, oferta, cross-sell e ancoragem |
| Quebrar Objeção de Preço | Cliente achou caro — foco em valor e custo-benefício |
| Quebrar Objeção de Necessidade | Cliente não sabe se precisa — diagnóstico de uso |
| Pitch Rápido | Script de 3 frases para cliente de passagem |
| Pai comprando para filho | Abordagem sem jargão técnico, foco em curadoria |
| Gamer Pro | Linguagem técnica, benchmarks, upgrade de setup |
| Primeiro PC Gamer | Alta chance de pacote completo |
| Follow-up | Cliente sumiu após visita — script de retomada |
| Fechamento | Cliente quase decidido — cruzar a linha |

## Estrutura da resposta da IA

```json
{
  "leitura_interesse": "...",
  "diagnostico_oportunidade": "ALTA | MÉDIA | BAIXA ...",
  "perguntas_qualificacao": ["...", "..."],
  "oferta_principal": { "produto": "...", "argumento": "...", "ponto_chave": "..." },
  "cross_sell": { "produto": "...", "gancho": "..." },
  "ancoragem": {
    "opcao_premium": { "produto": "...", "preco_estimado": "...", "diferencial": "..." },
    "opcao_recomendada": { "produto": "...", "preco_estimado": "...", "diferencial": "..." }
  },
  "script_abertura": "...",
  "quebra_objecao": "...",
  "gatilhos_ativos": ["URGENCIA_REAL", "COMPARADOR"],
  "alerta_vendedor": "..."
}
```

## Guardrails do sistema

- Responde apenas dentro do escopo gamer/tech
- Nunca inventa especificações técnicas
- Nunca usa linguagem manipulativa
- Idioma fixo: português brasileiro
- Retorna `{"erro": "..."}` para inputs inválidos ou fora de escopo

## Variáveis de contexto

| Campo | Valores aceitos |
|---|---|
| `persona` | cauteloso, entusiasta, pai_comprando_para_filho, gamer_pro, primeiro_pc, orcamento_apertado, indeciso, comparador |
| `mode` | padrao, objecao, pitch_rapido, followup, fechamento |
| `budget` | número em reais (opcional) |
| `objection` | texto livre (opcional) |
