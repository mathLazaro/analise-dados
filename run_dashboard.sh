#!/bin/bash

# Script para executar o Dashboard Ambiental
echo "🌍 Iniciando Dashboard Ambiental..."

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual e verificar se streamlit está instalado
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

# Verificar se os dados existem
if [ ! -d "tratado" ]; then
    echo "❌ Erro: Pasta 'tratado' com os dados não encontrada!"
    echo "Por favor, certifique-se de que a pasta 'tratado' com os dados está no diretório atual."
    exit 1
fi

echo "✅ Ambiente configurado com sucesso!"
echo "🚀 Iniciando dashboard em http://localhost:8501"
echo "📝 Para parar o dashboard, pressione Ctrl+C"
echo ""

# Executar o dashboard
streamlit run dashboard_ambiental.py 