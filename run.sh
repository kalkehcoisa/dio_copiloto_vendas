#!/bin/bash

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV_DIR=".venv"
PYTHON_BIN="python3.12"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Erro: $PYTHON_BIN não encontrado."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Criando ambiente virtual em $VENV_DIR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "Ambiente virtual já existe."
fi

echo "Ativando ambiente virtual..."
source "$VENV_DIR/bin/activate"

if [ ! -f "$BACKEND/.env" ]; then
  cp "$BACKEND/.env.example" "$BACKEND/.env"
  echo ""
  echo "⚠️  Arquivo .env criado em backend/.env"
  echo "    Adicione sua GROQ_API_KEY antes de continuar."
  echo ""
  read -rp "Pressione Enter depois de configurar o .env..."
fi

echo ""
echo "📦 Instalando dependências do backend..."
cd "$BACKEND"
pip install -r requirements.txt -q

echo "📦 Instalando dependências do frontend..."
cd "$FRONTEND"
npm install --silent

echo ""
echo "🚀 Iniciando VEGA..."
echo "   Backend → http://localhost:8000"
echo "   Frontend → http://localhost:5173"
echo ""
echo "   Ctrl+C para encerrar tudo."
echo ""

trap 'kill 0' SIGINT SIGTERM

cd "$BACKEND" && uvicorn main:app --reload --port 8000 &
cd "$FRONTEND" && npm run dev &

wait
