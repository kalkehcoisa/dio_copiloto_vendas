import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from prompt import PRESET_PROMPTS, build_messages
from pydantic import BaseModel

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI(title="Copiloto de Vendas VEGA", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatPayload(BaseModel):
    message: str
    context: dict = {}


def extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"erro": "Resposta fora do formato esperado."}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"erro": "JSON inválido retornado pelo modelo."}


@app.get("/presets")
def get_presets():
    return PRESET_PROMPTS


@app.post("/chat")
async def chat(payload: ChatPayload):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode ser vazia.")

    messages = build_messages(payload.message, payload.context)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=2000,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro na API Groq: {str(e)}")

    raw = completion.choices[0].message.content
    parsed = extract_json(raw)

    return {
        "ok": "erro" not in parsed,
        "data": parsed,
        "model": completion.model,
        "tokens_used": completion.usage.total_tokens if completion.usage else None,
    }
