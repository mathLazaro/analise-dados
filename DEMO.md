# 🚀 Demo Rápido - Dashboard Ambiental

## Execução Rápida

### Opção 1: Script Automático (Recomendado)
```bash
./run_dashboard.sh
```

### Opção 2: Manual
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar dashboard
streamlit run dashboard_ambiental.py
```

## 📊 O que você verá

### 1. Setores que Mais Degradam 🏭
- **Treemap** mostrando proporção de emissões por setor
- **KPIs** com total de emissões e maior emissor
- **Controle:** Seleção de ano para análise

### 2. Relação Setores vs Intensidade 📊
- **Gráfico Radar** comparando eficiência ambiental
- **Métricas:** Receita, eficiência, número de empresas
- **Controle:** Seleção múltipla de anos

### 3. Eficiência Ambiental 💡
- **Gráfico de Linha** com evolução temporal
- **KPI:** Receita Total ÷ Emissões
- **Insight:** Setores mais eficientes ambientalmente

### 4. Fatores de Irresponsabilidade ⚠️
- **Heatmap** de desmatamento por estado/tempo
- **Métricas:** Estado crítico, total Amazônia, variação
- **Controle:** Período inicial e final

### 5. Agricultura Familiar 🌱
- **Violin Plot** distribuição por região
- **Sunburst** hierarquia por tamanho de propriedade
- **Comparação:** Familiar vs Não Familiar

## 🎮 Controles Interativos

**Sidebar esquerda:**
- 📅 Ano para Emissões
- 📅 Período Desmatamento (início/fim)
- 📅 Anos para Análise Industrial (múltipla seleção)

## 🔍 Insights Esperados

- **Mudança de Uso da Terra** = maior emissor
- **Agricultura familiar** = maioria dos estabelecimentos
- **Estados amazônicos** = maior desmatamento
- **Eficiência varia** significativamente entre setores

## 📱 Acesso

Após executar, acesse: **http://localhost:8501**

---
*Dashboard desenvolvido para análise de impactos ambientais setoriais no Brasil* 🇧🇷 