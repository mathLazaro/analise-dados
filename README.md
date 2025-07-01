# 🌍 Dashboard Ambiental: Setores Econômicos e Degradação

Interface interativa desenvolvida em Python para análise dos impactos ambientais por setor econômico no Brasil, com base em dados de desmatamento, emissões de gases de efeito estufa e atividade agropecuária/industrial.

## 📋 Funcionalidades

O dashboard responde a 5 perguntas principais sobre degradação ambiental:

### 1. 🏭 Setores Econômicos que Mais Degradam o Meio Ambiente
- **Visualização:** Treemap interativo
- **Dados:** Emissões de GEE por setor (SEEG)
- **Insight:** Identifica proporcionalmente quais setores têm maior impacto ambiental

### 2. 📊 Relação entre Tipos de Setores e Intensidade de Degradação
- **Visualização:** Gráfico Radar (Spider Chart)
- **Dados:** Eficiência ambiental por setor industrial
- **Insight:** Compara múltiplas dimensões de performance ambiental

### 3. 💡 Eficiência Ambiental: Produção vs Impacto
- **Visualização:** Gráfico de linha temporal
- **KPI:** Receita Total ÷ Emissões do Setor
- **Insight:** Evolução da eficiência ambiental ao longo do tempo

### 4. ⚠️ Fatores Relacionados à Falta de Responsabilidade Ambiental
- **Visualização:** Heatmap temporal
- **Dados:** Desmatamento por estado na Amazônia Legal (PRODES)
- **Insight:** Identifica padrões regionais e temporais de risco ambiental

### 5. 🌱 Agricultura Familiar e Sustentabilidade
- **Visualização:** Violin Plot + Sunburst
- **Dados:** Distribuição de estabelecimentos por tipo e tamanho
- **Insight:** Relação entre agricultura familiar e sustentabilidade

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- Dados na pasta `tratado/` (estrutura conforme especificada)

### Instalação

#### Opção 1: Instalação Manual
```bash
# Clone/baixe o projeto
# Navegue até o diretório do projeto

# Crie um ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

#### Opção 2: Script Automatizado
```bash
# Execute o script que configura tudo automaticamente
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Execução
```bash
# Ative o ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Execute o dashboard
streamlit run dashboard_ambiental.py
```

O dashboard será aberto automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura de Dados Esperada

```
tratado/
├── dados agricultura/
│   ├── dados-agricultura-2017.csv
│   └── dados-agricultura-2006.csv
├── dados industria/
│   └── dados-industriais.csv
└── desmatamento/
    ├── taxa_prodes_1988_2024-tratado.csv
    └── seeg/
        ├── emissões_brutas.csv
        └── emissões_liquidas.csv
```

## 🎮 Controles Interativos

### Sidebar - Controles do Dashboard
- **Ano para Análise de Emissões:** Seleção do ano para análise setorial
- **Período de Desmatamento:** Anos inicial e final para heatmap
- **Anos para Análise Industrial:** Seleção múltipla para análise radar

### Interatividade Mínima
- Filtros temporais por período
- Seleção de anos específicos
- Controles de visualização por setor

## 📊 Técnicas de Visualização Utilizadas

### Visualizações Principais (diferentes das restritas)
1. **Treemap** - Proporção de emissões por setor
2. **Gráfico Radar/Spider** - Eficiência multidimensional
3. **Heatmap** - Intensidade temporal-espacial
4. **Violin Plot** - Distribuição estatística
5. **Sunburst** - Hierarquia categórica

### Visualizações de Apoio
- Gráficos de linha para tendências temporais
- Métricas (KPIs) dinâmicas
- Cards informativos

## 📈 Indicadores Calculados

### KPIs Principais
- **Total de Emissões:** Soma das emissões por setor/ano
- **Maior Emissor:** Setor com maior contribuição percentual
- **Eficiência Ambiental:** Receita ÷ Emissões
- **Participação Agricultura Familiar:** % do total de estabelecimentos

### Métricas Regionais
- **Estado com Maior Desmatamento:** Identificação automática
- **Variação Anual:** Crescimento/decrescimento percentual
- **Total Amazônia Legal:** Consolidação regional

## 🔍 Insights e Conclusões

### Principais Descobertas
- Mudança de Uso da Terra é o maior emissor de GEE
- Agricultura familiar representa a maioria dos estabelecimentos
- Estados amazônicos concentram maior desmatamento
- Eficiência ambiental varia significativamente entre setores

### Recomendações
- Foco em tecnologias sustentáveis para grandes propriedades
- Incentivos específicos para agricultura familiar
- Monitoramento intensivo em estados críticos
- Políticas setoriais diferenciadas por impacto

## 🛡️ Tratamento de Erros

O dashboard inclui:
- Validação de arquivos de dados
- Tratamento de dados ausentes
- Mensagens de erro informativas
- Fallbacks para dados incompletos

## 🔧 Customização

### Adicionando Novos Dados
1. Mantenha a estrutura de pastas esperada
2. Formatos CSV com encoding UTF-8
3. Colunas conforme especificações originais

### Modificando Visualizações
- Funções modulares para fácil customização
- Parâmetros configuráveis via sidebar
- Esquemas de cores ajustáveis

## 📋 Dependências

- **streamlit:** Framework web interativo
- **pandas:** Manipulação de dados
- **plotly:** Visualizações interativas
- **numpy:** Computação numérica
- **seaborn/matplotlib:** Visualizações estatísticas

## 🤝 Contribuição

Para melhorias:
1. Mantenha a responsividade às 5 perguntas principais
2. Use técnicas de visualização não listadas nas restrições
3. Preserve a interatividade mínima especificada
4. Documente alterações no README

---

**Desenvolvido para análise de impactos ambientais setoriais no Brasil** 🇧🇷 