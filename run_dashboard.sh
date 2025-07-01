#!/bin/bash

# Script para executar o Dashboard Ambiental
# Automatiza a ativação do ambiente virtual e execução do Streamlit

echo "🌍 Dashboard Ambiental - Inicializando..."
echo "=============================================="

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
pip install -r requirements.txt > /dev/null 2>&1

# Executar testes rápidos (opcional)
read -p "🧪 Executar testes antes de iniciar? (s/N): " run_tests
if [[ $run_tests =~ ^[Ss]$ ]]; then
    echo "🔍 Executando testes..."
    python test_dashboard.py
    if [ $? -ne 0 ]; then
        echo "❌ Testes falharam. Verifique os problemas acima."
        exit 1
    fi
    echo "✅ Todos os testes passaram!"
fi

# Verificar estrutura de dados
echo "📁 Verificando estrutura de dados..."
if [ ! -d "tratado" ]; then
    echo "⚠️ ATENÇÃO: Pasta 'tratado' não encontrada!"
    echo "   Certifique-se de que os dados estão na estrutura:"
    echo "   tratado/"
    echo "   ├── dados agricultura/"
    echo "   ├── desmatamento/"
    echo "   └── dados industria/"
    echo ""
    read -p "Continuar mesmo assim? (s/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Ss]$ ]]; then
        echo "❌ Execução cancelada. Configure os dados e tente novamente."
        exit 1
    fi
fi

# Iniciar o dashboard
echo "🚀 Iniciando Dashboard Ambiental..."
echo "📊 O dashboard será aberto automaticamente no navegador"
echo "🔗 URL: http://localhost:8501"
echo ""
echo "⏹️  Para parar o dashboard, pressione Ctrl+C"
echo "=============================================="

# Executar Streamlit
streamlit run dashboard_ambiental.py

echo ""
echo "👋 Dashboard finalizado. Até a próxima!" 