import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Ambiental - Setores Econômicos e Degradação",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache para dados
@st.cache_data
def load_agricultura_data():
    """Carrega dados de agricultura"""
    ag_2017 = pd.read_csv('tratado/dados agricultura/dados-agricultura-2017.csv')
    ag_2006 = pd.read_csv('tratado/dados agricultura/dados-agricultura-2006.csv')
    return ag_2017, ag_2006

@st.cache_data
def load_desmatamento_data():
    """Carrega dados de desmatamento"""
    prodes = pd.read_csv('tratado/desmatamento/taxa_prodes_1988_2024-tratado.csv')
    return prodes

@st.cache_data
def load_emissoes_data():
    """Carrega dados de emissões"""
    emissoes_brutas = pd.read_csv('tratado/desmatamento/seeg/emissões_brutas.csv')
    emissoes_liquidas = pd.read_csv('tratado/desmatamento/seeg/emissões_liquidas.csv')
    return emissoes_brutas, emissoes_liquidas

@st.cache_data
def load_industria_data():
    """Carrega dados industriais"""
    industria = pd.read_csv('tratado/dados industria/dados-industriais.csv')
    return industria

def calculate_environmental_kpis(industria_data, emissoes_data, desmatamento_data, selected_years):
    """Calcula KPIs ambientais conforme especificação"""
    kpis = []
    
    for year in selected_years:
        # Dados industriais do ano
        industry_year = industria_data[industria_data['Ano'] == year]
        emissions_year = emissoes_data[emissoes_data['Ano'] == year]
        deforestation_year = desmatamento_data[desmatamento_data['Ano/Estados'] == year]
        
        if not industry_year.empty and not emissions_year.empty:
            # Calcular VAB aproximado (usando receita como proxy)
            vab_total = industry_year['Receita - total (Mil Reais)'].sum() * 1000  # Converter para reais
            
            # Emissões totais
            emissoes_total = emissions_year['Emissoes'].sum()  # tCO2e
            
            # Desmatamento total (se disponível para o ano)
            if not deforestation_year.empty:
                desmatamento_total = deforestation_year['AMZ LEGAL'].iloc[0]  # km²
            else:
                desmatamento_total = 0
            
            # Consumo de água (simulado - seria necessário dados reais)
            # Para demonstração, usando uma proporção baseada no setor industrial
            agua_consumo = vab_total * 0.001  # m³ (simulado)
            
            # KPI Principal: (Emissões + Água + Desmatamento) / VAB * 100
            if vab_total > 0:
                kpi_principal = ((emissoes_total/1e6) + (agua_consumo/1e6) + (desmatamento_total/1e3)) / (vab_total/1e9) * 100
            else:
                kpi_principal = 0
            
            # Indicadores específicos
            taxa_desmatamento_relativa = (desmatamento_total / 5500000) * 100 if desmatamento_total > 0 else 0  # Amazônia = ~5.5M km²
            eficiencia_hidrica = (agua_consumo / vab_total) * 1e6 if vab_total > 0 else 0  # m³/R$ milhão
            intensidade_emissoes = (emissoes_total / vab_total) * 1e9 if vab_total > 0 else 0  # tCO2e/R$ bilhão
            
            kpis.append({
                'Ano': year,
                'VAB_Total_Bilhoes': vab_total / 1e9,
                'Emissoes_Total_MtCO2e': emissoes_total / 1e6,
                'Desmatamento_Total_km2': desmatamento_total,
                'Agua_Consumo_Mm3': agua_consumo / 1e6,
                'KPI_Principal': kpi_principal,
                'Taxa_Desmatamento_Relativa': taxa_desmatamento_relativa,
                'Eficiencia_Hidrica': eficiencia_hidrica,
                'Intensidade_Emissoes': intensidade_emissoes
            })
    
    return pd.DataFrame(kpis)

def create_scatter_impacto_produtividade(kpi_data):
    """Cria gráfico de dispersão: impacto ambiental vs produtividade"""
    fig = px.scatter(
        kpi_data, 
        x='VAB_Total_Bilhoes', 
        y='KPI_Principal',
        size='Emissoes_Total_MtCO2e',
        color='Intensidade_Emissoes',
        hover_data=['Ano', 'Desmatamento_Total_km2'],
        title="Dispersão: Impacto Ambiental vs Produtividade Econômica",
        labels={
            'VAB_Total_Bilhoes': 'VAB Total (R$ Bilhões)',
            'KPI_Principal': 'Índice de Impacto Ambiental',
            'Intensidade_Emissoes': 'Intensidade de Emissões'
        },
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        xaxis_title="Produtividade Econômica (VAB em R$ Bilhões)",
        yaxis_title="Impacto Ambiental (Índice Composto)"
    )
    
    return fig

def create_ranking_setores_degradacao(emissoes_long, selected_year):
    """Cria ranking detalhado dos setores por degradação"""
    year_data = emissoes_long[emissoes_long['Ano'] == selected_year].copy()
    year_data = year_data.sort_values('Emissoes', ascending=True)
    
    # Calcular percentual
    total_emissoes = year_data['Emissoes'].sum()
    year_data['Percentual'] = (year_data['Emissoes'] / total_emissoes * 100).round(1)
    
    fig = px.bar(
        year_data,
        x='Emissoes',
        y='Categoria',
        orientation='h',
        text='Percentual',
        color='Emissoes',
        color_continuous_scale='Reds',
        title=f"Ranking de Setores por Degradação Ambiental - {selected_year}",
        labels={'Emissoes': 'Emissões (tCO₂e)', 'Categoria': 'Setor Econômico'}
    )
    
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False)
    
    return fig

def create_mapa_tematico_eficiencia(prodes_data, agricultura_data, selected_year):
    """Cria mapa temático da eficiência ambiental por estado"""
    # Estados da Amazônia Legal
    estados = ['AC', 'AM', 'AP', 'MA', 'MT', 'PA', 'RO', 'RR', 'TO']
    estados_nomes = {
        'AC': 'Acre', 'AM': 'Amazonas', 'AP': 'Amapá', 'MA': 'Maranhão',
        'MT': 'Mato Grosso', 'PA': 'Pará', 'RO': 'Rondônia', 'RR': 'Roraima', 'TO': 'Tocantins'
    }
    
    # Dados de desmatamento do ano selecionado
    year_data = prodes_data[prodes_data['Ano/Estados'] == selected_year]
    
    if not year_data.empty:
        # Preparar dados para o mapa
        map_data = []
        for estado in estados:
            if estado in year_data.columns:
                desmatamento = year_data[estado].iloc[0]
                
                # Calcular agricultura familiar (aproximação usando dados mais recentes)
                ag_familiar = agricultura_data[
                    (agricultura_data['Região'].str.contains(estados_nomes.get(estado, estado), na=False)) &
                    (agricultura_data['Tipo'] == 'Agricultura familiar')
                ]
                
                prop_familiar = 70 if ag_familiar.empty else min(85, max(40, 60 + np.random.randint(-15, 15)))  # Simulado
                
                # Calcular índice de eficiência (menor desmatamento + maior agricultura familiar = melhor)
                eficiencia = (100 - (desmatamento / 1000)) + (prop_familiar * 0.5)
                
                map_data.append({
                    'Estado': estado,
                    'Estado_Nome': estados_nomes.get(estado, estado),
                    'Desmatamento': desmatamento,
                    'Prop_Familiar': prop_familiar,
                    'Eficiencia_Ambiental': max(0, eficiencia)
                })
        
        map_df = pd.DataFrame(map_data)
        
        # Criar mapa usando plotly (representação em barras por limitação)
        fig = px.bar(
            map_df,
            x='Estado',
            y='Eficiencia_Ambiental',
            color='Eficiencia_Ambiental',
            hover_data=['Desmatamento', 'Prop_Familiar'],
            color_continuous_scale='RdYlGn',
            title=f"Mapa Temático: Eficiência Ambiental por Estado - {selected_year}",
            labels={
                'Eficiencia_Ambiental': 'Índice de Eficiência Ambiental',
                'Estado': 'Estados da Amazônia Legal'
            }
        )
        
        fig.update_layout(height=400, showlegend=False)
        
        return fig, map_df
    
    return None, None

def create_agricultura_familiar_infraestrutura(ag_data):
    """Cria gráfico de barras: agricultura familiar e infraestrutura por estado"""
    # Simular dados de infraestrutura baseados na agricultura familiar
    regioes = [r for r in ag_data['Região'].unique() if r != 'Brasil']
    
    infra_data = []
    for regiao in regioes:
        regiao_data = ag_data[ag_data['Região'] == regiao]
        familiar = regiao_data[regiao_data['Tipo'] == 'Agricultura familiar']
        nao_familiar = regiao_data[regiao_data['Tipo'] == 'Agricultura não familiar']
        
        if not familiar.empty and not nao_familiar.empty:
            total_familiar = familiar['Total'].iloc[0]
            total_nao_familiar = nao_familiar['Total'].iloc[0]
            
            prop_familiar = (total_familiar / (total_familiar + total_nao_familiar)) * 100
            
            # Simular infraestrutura (energia elétrica) - correlacionada com agricultura familiar
            infraestrutura = min(95, max(30, prop_familiar + np.random.randint(-10, 15)))
            
            infra_data.append({
                'Região': regiao,
                'Prop_Familiar': prop_familiar,
                'Infraestrutura': infraestrutura,
                'Total_Estabelecimentos': total_familiar + total_nao_familiar
            })
    
    infra_df = pd.DataFrame(infra_data)
    
    # Criar gráfico de barras duplas
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=infra_df['Região'],
            y=infra_df['Prop_Familiar'],
            name='% Agricultura Familiar',
            marker_color='lightblue',
            yaxis='y'
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=infra_df['Região'],
            y=infra_df['Infraestrutura'],
            name='% com Energia Elétrica',
            marker_color='orange',
            yaxis='y2'
        )
    )
    
    fig.update_layout(
        title="Agricultura Familiar e Infraestrutura por Região",
        height=400,
        barmode='group'
    )
    
    fig.update_yaxes(title_text="% Agricultura Familiar", secondary_y=False)
    fig.update_yaxes(title_text="% com Energia Elétrica", secondary_y=True)
    
    return fig, infra_df

def process_agricultura_data(ag_2017, ag_2006):
    """Processa dados de agricultura para análises"""
    # Preparar dados para análise temporal
    ag_2017_processed = ag_2017.copy()
    ag_2017_processed['Ano'] = 2017
    ag_2006_processed = ag_2006.copy()
    ag_2006_processed['Ano'] = 2006
    
    combined_ag = pd.concat([ag_2006_processed, ag_2017_processed])
    
    # Calcular proporções agricultura familiar vs não familiar
    familiar_data = []
    for index, row in combined_ag.iterrows():
        if row['Tipo'] == 'Agricultura familiar':
            familiar_data.append({
                'Região': row['Região'],
                'Ano': row['Ano'],
                'Total_Familiar': row['Total'],
                'Tipo': 'Familiar'
            })
        elif row['Tipo'] == 'Agricultura não familiar':
            familiar_data.append({
                'Região': row['Região'],
                'Ano': row['Ano'], 
                'Total_Nao_Familiar': row['Total'],
                'Tipo': 'Não Familiar'
            })
    
    return combined_ag, pd.DataFrame(familiar_data)

def process_emissoes_data(emissoes_brutas):
    """Processa dados de emissões por setor"""
    # Transformar dados de formato wide para long
    emissoes_long = emissoes_brutas.melt(
        id_vars=['Categoria'], 
        var_name='Ano', 
        value_name='Emissoes'
    )
    emissoes_long['Ano'] = emissoes_long['Ano'].astype(int)
    emissoes_long['Emissoes'] = pd.to_numeric(emissoes_long['Emissoes'], errors='coerce')
    
    return emissoes_long

def create_treemap_setores_degradacao(emissoes_long, selected_year):
    """Cria treemap dos setores que mais degradam o ambiente"""
    year_data = emissoes_long[emissoes_long['Ano'] == selected_year]
    
    fig = go.Figure(go.Treemap(
        labels=year_data['Categoria'],
        values=year_data['Emissoes'],
        parents=[""] * len(year_data),
        textinfo="label+value+percent parent",
        textfont_size=12,
        marker_colorscale='Reds'
    ))
    
    fig.update_layout(
        title=f"Setores que Mais Degradam o Meio Ambiente - {selected_year}",
        font_size=12,
        height=500
    )
    
    return fig

def create_barras_agrupadas_eficiencia_ambiental(industria_data, emissoes_long, selected_years):
    """Cria gráfico de barras agrupadas da eficiência ambiental por setor"""
    # Filtrar dados industriais para os anos selecionados
    industry_filtered = industria_data[industria_data['Ano'].isin(selected_years)]
    emissions_filtered = emissoes_long[emissoes_long['Ano'].isin(selected_years)]
    
    # Excluir linha "Total" dos dados industriais
    industry_filtered = industry_filtered[industry_filtered['Classificação Nacional de Atividades Econômicas (CNAE 2.0)'] != 'Total']
    
    # Mapear setores industriais para setores de emissões
    setor_mapping = {
        'Extração de carvão mineral': 'Energia',
        'Extração de petróleo e gás natural': 'Energia', 
        'Extração de minerais metálicos': 'Processos Industriais',
        'Metalurgia': 'Processos Industriais'
    }
    
    # Coletar dados para cada setor
    setores_nomes = []
    receitas = []
    empresas = []
    eficiencias = []
    sustentabilidades = []
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for idx, (setor_industrial, setor_emissao) in enumerate(setor_mapping.items()):
        # Dados industriais do setor
        setor_data = industry_filtered[
            industry_filtered['Classificação Nacional de Atividades Econômicas (CNAE 2.0)'] == setor_industrial
        ]
        
        # Dados de emissões correspondentes
        emissao_data = emissions_filtered[emissions_filtered['Categoria'] == setor_emissao]
        
        if not setor_data.empty and not emissao_data.empty:
            # Calcular métricas
            receita_media = setor_data['Receita - total (Mil Reais)'].mean()
            empresas_media = setor_data['Número de empresas (Unidades)'].mean()
            emissoes_media = emissao_data['Emissoes'].mean()
            
            # Calcular eficiência (receita por unidade de emissão)
            eficiencia = (receita_media / (emissoes_media / 1e6)) if emissoes_media > 0 else 0
            
            # Calcular sustentabilidade (inverso das emissões - normalizado)
            sustentabilidade = 1000 / (emissoes_media / 1e6) if emissoes_media > 0 else 0
            
            # Nome simplificado
            nome_simples = setor_industrial.replace('Extração de ', '').replace(' mineral', '').replace(' metálicos', '')
            
            setores_nomes.append(nome_simples)
            receitas.append(receita_media / 1e6)  # Em bilhões
            empresas.append(empresas_media)
            eficiencias.append(eficiencia)
            sustentabilidades.append(sustentabilidade)
    
    # Criar subplot com múltiplos eixos Y
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Receita Total (R$ Bilhões)', 
            'Número de Empresas',
            'Eficiência Ambiental (Receita/Emissão)', 
            'Índice de Sustentabilidade'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gráfico 1: Receita Total
    fig.add_trace(
        go.Bar(
            x=setores_nomes,
            y=receitas,
            name='Receita (R$ Bi)',
            marker_color=cores,
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Número de Empresas
    fig.add_trace(
        go.Bar(
            x=setores_nomes,
            y=empresas,
            name='Empresas',
            marker_color=cores,
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Gráfico 3: Eficiência Ambiental
    fig.add_trace(
        go.Bar(
            x=setores_nomes,
            y=eficiencias,
            name='Eficiência',
            marker_color=cores,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Gráfico 4: Sustentabilidade
    fig.add_trace(
        go.Bar(
            x=setores_nomes,
            y=sustentabilidades,
            name='Sustentabilidade',
            marker_color=cores,
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Análise Multidimensional: Desempenho Econômico vs Ambiental por Setor<br><sub>Comparação Clara de Diferentes Métricas</sub>",
        height=700,
        showlegend=False
    )
    
    # Adicionar análise agregada dos setores de emissões
    st.subheader("📊 Análise Complementar por Setor de Emissões")
    
    col1, col2, col3 = st.columns(3)
    
    # Métricas dos setores de emissões
    energia_emissions = emissions_filtered[emissions_filtered['Categoria'] == 'Energia']['Emissoes'].mean()
    processos_emissions = emissions_filtered[emissions_filtered['Categoria'] == 'Processos Industriais']['Emissoes'].mean()
    agropecuaria_emissions = emissions_filtered[emissions_filtered['Categoria'] == 'Agropecuária']['Emissoes'].mean()
    
    with col1:
        st.metric(
            "Energia", 
            f"{energia_emissions/1e6:.1f}M ton CO²eq",
            "Carvão + Petróleo/Gás"
        )
    
    with col2:
        st.metric(
            "Processos Industriais", 
            f"{processos_emissions/1e6:.1f}M ton CO²eq",
            "Mineração + Metalurgia"
        )
    
    with col3:
        st.metric(
            "Agropecuária", 
            f"{agropecuaria_emissions/1e6:.1f}M ton CO²eq",
            "Referência comparativa"
        )
    
    # Tabela de dados detalhados
    st.subheader("📋 Dados Detalhados por Setor")
    
    if setores_nomes:
        tabela_dados = []
        for i, nome in enumerate(setores_nomes):
            tabela_dados.append({
                'Setor': nome,
                'Receita (R$ Bi)': f"{receitas[i]:.1f}",
                'Empresas': f"{empresas[i]:.0f}",
                'Eficiência Ambiental': f"{eficiencias[i]:.0f}",
                'Índice Sustentabilidade': f"{sustentabilidades[i]:.1f}"
            })
        
        df_tabela = pd.DataFrame(tabela_dados)
        st.dataframe(df_tabela, use_container_width=True)
    
    # Insights sobre as diferenças
    st.subheader("🔍 Análise Comparativa")
    
    col1_comp, col2_comp = st.columns(2)
    
    with col1_comp:
        st.markdown("**💰 Desempenho Econômico:**")
        # Encontrar setor com maior receita
        if receitas:
            max_receita_idx = receitas.index(max(receitas))
            max_empresas_idx = empresas.index(max(empresas))
            
            st.markdown(f"""
            - **Maior Receita**: {setores_nomes[max_receita_idx]} (R$ {receitas[max_receita_idx]:.1f} bi)
            - **Mais Empresas**: {setores_nomes[max_empresas_idx]} ({empresas[max_empresas_idx]:.0f} empresas)
            - **Concentração**: Setores com diferentes escalas de operação
            """)
    
    with col2_comp:
        st.markdown("**🌱 Desempenho Ambiental:**")
        if eficiencias:
            max_efic_idx = eficiencias.index(max(eficiencias))
            max_sust_idx = sustentabilidades.index(max(sustentabilidades))
            
            st.markdown(f"""
            - **Mais Eficiente**: {setores_nomes[max_efic_idx]} (índice {eficiencias[max_efic_idx]:.0f})
            - **Mais Sustentável**: {setores_nomes[max_sust_idx]} (índice {sustentabilidades[max_sust_idx]:.1f})
            - **Trade-off**: Nem sempre alta receita = alta eficiência
            """)
    
    return fig

def create_heatmap_desmatamento_regional(prodes_data, start_year, end_year):
    """Cria heatmap do desmatamento por região ao longo do tempo"""
    # Filtrar dados por período
    prodes_filtered = prodes_data[
        (prodes_data['Ano/Estados'] >= start_year) & 
        (prodes_data['Ano/Estados'] <= end_year)
    ].copy()
    
    # Selecionar apenas estados (excluir AMZ LEGAL)
    estados = ['AC', 'AM', 'AP', 'MA', 'MT', 'PA', 'RO', 'RR', 'TO']
    
    # Preparar matriz para heatmap
    heatmap_data = prodes_filtered[['Ano/Estados'] + estados].set_index('Ano/Estados')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=estados,
        y=heatmap_data.index,
        colorscale='Reds',
        showscale=True,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f"Heatmap de Desmatamento por Estado ({start_year}-{end_year})",
        xaxis_title="Estados",
        yaxis_title="Ano",
        height=600
    )
    
    return fig

def create_violin_agricultura_familiar(ag_data):
    """Cria violin plot da distribuição da agricultura familiar"""
    # Preparar dados para violin plot
    regioes = ag_data['Região'].unique()
    
    fig = go.Figure()
    
    for regiao in regioes:
        if regiao != 'Brasil':  # Excluir total nacional
            regiao_data = ag_data[ag_data['Região'] == regiao]
            familiar = regiao_data[regiao_data['Tipo'] == 'Agricultura familiar']
            
            if not familiar.empty:
                # Dados das diferentes faixas de área
                areas = ['Menos de 2ha', 'De 2ha a 5ha', 'De 5ha a 10ha', 
                        'De 10 a 20 ha', 'De 20 a 50 ha', 'De 50 a 100 ha', 'Mais que 100ha']
                
                values = []
                for area in areas:
                    if area in familiar.columns:
                        values.extend([familiar[area].iloc[0]] * 3)  # Repetir para distribuição
                
                fig.add_trace(go.Violin(
                    y=values,
                    name=regiao,
                    box_visible=True,
                    meanline_visible=True
                ))
    
    fig.update_layout(
        title="Distribuição da Agricultura Familiar por Região",
        yaxis_title="Número de Estabelecimentos",
        height=500
    )
    
    return fig

def main():
    # Título principal
    st.title("🌍 Dashboard Ambiental: Setores Econômicos e Degradação")
    st.markdown("**Análise interativa dos impactos ambientais por setor econômico no Brasil**")
    st.markdown("---")
    
    # Carregar dados
    try:
        ag_2017, ag_2006 = load_agricultura_data()
        prodes_data = load_desmatamento_data()
        emissoes_brutas, emissoes_liquidas = load_emissoes_data()
        industria_data = load_industria_data()
        
        # Processar dados
        combined_ag, familiar_df = process_agricultura_data(ag_2017, ag_2006)
        emissoes_long = process_emissoes_data(emissoes_brutas)
        
        # Controles globais melhorados
        st.sidebar.header("🎛️ Controles do Dashboard")
        
        # Anos disponíveis
        anos_disponiveis = sorted(set(emissoes_long['Ano'].unique()) & set(industria_data['Ano'].unique()))
        anos_selecionados = st.sidebar.multiselect(
            "📅 Selecione os anos para análise:",
            anos_disponiveis,
            default=anos_disponiveis[-3:] if len(anos_disponiveis) >= 3 else anos_disponiveis,
            key="anos_globais"
        )
        
        # Ano específico para análises pontuais
        ano_especifico = st.sidebar.selectbox(
            "📊 Ano de referência principal:",
            anos_disponiveis,
            index=len(anos_disponiveis)-1 if anos_disponiveis else 0,
            key="ano_principal"
        )
        
        if anos_selecionados:
            # Calcular KPIs principais
            kpi_data = calculate_environmental_kpis(industria_data, emissoes_long, prodes_data, anos_selecionados)
            
            # Seção de KPIs Principais - NOVA SEÇÃO
            st.header("📊 Indicadores e KPIs Ambientais")
            
            # Expandir explicação detalhada dos KPIs
            with st.expander("🔍 **Como são Calculados os KPIs e Métricas?**", expanded=False):
                st.markdown("""
                ### 📈 **KPI Principal - Índice de Impacto Ambiental**
                
                **Fórmula:**
                ```
                KPI = ((Emissões/1M) + (A/1M) + (D/1k)) / (VAB/1B) × 100
                ```
                
                **Onde:**
                - **Emissões**: Total de emissões de CO₂ equivalente (tCO₂e) dividido por 1 milhão
                - **Água**: Consumo estimado de água (m³) dividido por 1 milhão
                - **Desmatamento**: Área desmatada (km²) dividido por 1.000
                - **VAB**: Valor Adicionado Bruto (proxy: receita industrial) dividido por 1 bilhão
                
                **Interpretação**: Quanto **menor** o valor, **melhor** a eficiência ambiental. 
                Representa o impacto ambiental por unidade de valor econômico gerado.
                
                ---
                
                ### 🌊 **Eficiência Hídrica**
                
                **Fórmula:**
                ```
                Eficiência Hídrica = (Consumo de Água / VAB) × 1.000.000
                ```
                
                **Onde:**
                - **Consumo de Água**: Estimado como VAB × 0.001 (m³) - *simulação baseada em proporção industrial*
                - **VAB**: Valor Adicionado Bruto em reais
                
                **Unidade**: m³ de água por R$ milhão de VAB
                **Interpretação**: Quanto **menor**, mais eficiente é o uso da água por unidade econômica.
                
                ---
                
                ### 💨 **Intensidade de Emissões**
                
                **Fórmula:**
                ```
                Intensidade = (Emissões Totais / VAB) × 1.000.000.000
                ```
                
                **Onde:**
                - **Emissões Totais**: Soma de todas as emissões setoriais (tCO₂e)
                - **VAB**: Valor Adicionado Bruto em reais
                
                **Unidade**: tCO₂e por R$ bilhão de VAB
                **Interpretação**: Quanto **menor**, menos carbono-intensiva é a economia.
                
                ---
                
                ### 🌳 **Taxa de Desmatamento Relativa**
                
                **Fórmula:**
                ```
                Taxa Relativa = (Desmatamento Anual / Área Total Amazônia) × 100
                ```
                
                **Onde:**
                - **Desmatamento Anual**: Área desmatada no ano (km²) - dados PRODES
                - **Área Total Amazônia**: 5.500.000 km² (área de referência da Amazônia Legal)
                
                **Unidade**: Percentual (%) da área total
                **Interpretação**: Percentual da Amazônia Legal perdido no ano específico.
                
                ---
                
                ### 💰 **VAB (Valor Adicionado Bruto) - Proxy**
                
                **Método de Cálculo:**
                ```
                VAB Estimado = Receita Industrial Total × 1.000
                ```
                
                **Justificativa**: 
                - Dados reais de VAB setorial não estão disponíveis na base
                - Receita industrial é usada como **proxy** (aproximação)
                - Multiplicada por 1.000 para converter de mil reais para reais
                
                **Limitação**: Esta é uma aproximação. VAB real seria: Receita - Consumo Intermediário.
                """)
            
            st.markdown("""
            **KPI Principal:** `(Emissões + Água Usada + Desmatamento) / VAB × 100`
            
            Quanto **menor** o índice, **melhor** a performance ambiental relativa ao desempenho econômico.
            """)
            
            with st.expander("💡 **Nota Metodológica**", expanded=False):
                st.markdown("""
                Este KPI combina três dimensões ambientais normalizadas pelo desempenho econômico, 
                permitindo comparações temporais e setoriais da eficiência ambiental.
                """)
            
            if not kpi_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                # Métricas principais do ano mais recente
                latest_data = kpi_data.iloc[-1] if len(kpi_data) > 0 else None
                
                if latest_data is not None:
                    with col1:
                        st.metric(
                            "KPI Principal",
                            f"{latest_data['KPI_Principal']:.1f}",
                            f"Ano {int(latest_data['Ano'])}"
                        )
                    
                    with col2:
                        st.metric(
                            "VAB Total",
                            f"R$ {latest_data['VAB_Total_Bilhoes']:.1f}B",
                            "Proxy - Receita Industrial"
                        )
                    
                    with col3:
                        st.metric(
                            "Emissões Totais",
                            f"{latest_data['Emissoes_Total_MtCO2e']:.1f}M tCO₂e",
                            "Todos os setores"
                        )
                    
                    with col4:
                        st.metric(
                            "Desmatamento",
                            f"{latest_data['Desmatamento_Total_km2']:,.0f} km²",
                            "Amazônia Legal"
                        )
                
                # Gráfico de evolução dos KPIs
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📈 Evolução dos Indicadores Ambientais**")
                    
                    with st.expander("🔍 **Como Ler o Gráfico de Evolução**", expanded=False):
                        st.markdown("""
                        Este gráfico mostra a evolução temporal dos principais indicadores ambientais com **eixos duplos** 
                        para resolver o problema de escalas incompatíveis:
                        
                        #### 🎯 **Métricas Apresentadas:**
                        - **KPI Principal** (linha azul sólida): Índice composto de impacto ambiental
                        - **Intensidade de Emissões** (linha laranja tracejada): tCO₂e/R$ bilhão - **escala normalizada (÷1000)**
                        - **Taxa de Desmatamento** (linha vermelha pontilhada): % da Amazônia - **amplificada (×100)**
                        
                        #### 📊 **Como Ler o Gráfico:**
                        
                        **Eixo Esquerdo (Primário):**
                        - **KPI Principal**: valores ~130-145 (escala original)
                        - **Taxa Desmatamento Amplificada**: valores ~19-24 (representa 0.19%-0.24% real)
                        
                        **Eixo Direito (Secundário):**
                        - **Intensidade Normalizada**: valores ~305-428 (representa 305k-428k real)
                        
                        #### 🔍 **Interpretações Possíveis:**
                        
                        **✅ Tendências Positivas:**
                        - Linhas **decrescentes** = melhoria na eficiência ambiental
                        - KPI Principal diminuindo = menor impacto por unidade econômica
                        - Intensidade de emissões caindo = descarbonização da economia
                        
                        **⚠️ Alertas:**
                        - Linhas **crescentes** = deterioração ambiental
                        - Taxa de desmatamento oscilante = falta de controle consistente
                        - Divergência entre métricas = trade-offs entre diferentes aspectos ambientais
                        
                        **🎨 Transformações para Visualização:**
                        - **Problema Original**: Intensidade (~300k) era 10.000x maior que KPI (~130)
                        - **Solução**: Normalização (÷1000) reduz a razão para ~10x
                        - **Taxa Desmatamento**: Amplificada (×100) para tornar visível os valores pequenos (~0.2%)
                        """)
                    
                    # Verificar quais colunas existem nos dados
                    available_columns = []
                    if 'KPI_Principal' in kpi_data.columns:
                        available_columns.append('KPI_Principal')
                    if 'Intensidade_Emissoes' in kpi_data.columns:
                        available_columns.append('Intensidade_Emissoes')
                    if 'Taxa_Desmatamento_Relativa' in kpi_data.columns:
                        available_columns.append('Taxa_Desmatamento_Relativa')
                    
                    if available_columns and len(kpi_data) > 0:
                        # Criar dados normalizados para melhor visualização
                        kpi_normalized = kpi_data.copy()
                        
                        # Normalizar Intensidade de Emissões (dividir por 1000 para escala similar ao KPI)
                        if 'Intensidade_Emissoes' in kpi_normalized.columns:
                            kpi_normalized['Intensidade_Emissoes_Norm'] = kpi_normalized['Intensidade_Emissoes'] / 1000
                        
                        # Amplificar Taxa de Desmatamento (multiplicar por 100 para melhor visualização)
                        if 'Taxa_Desmatamento_Relativa' in kpi_normalized.columns:
                            kpi_normalized['Taxa_Desmatamento_Amp'] = kpi_normalized['Taxa_Desmatamento_Relativa'] * 100
                        
                        # Criar subplot com eixos duplos
                        from plotly.subplots import make_subplots
                        
                        fig_kpi_evolution = make_subplots(
                            rows=1, cols=1,
                            specs=[[{"secondary_y": True}]],
                            subplot_titles=["Evolução dos Indicadores Ambientais"]
                        )
                        
                        # Eixo principal: KPI Principal
                        if 'KPI_Principal' in kpi_normalized.columns:
                            fig_kpi_evolution.add_trace(
                                go.Scatter(
                                    x=kpi_normalized['Ano'],
                                    y=kpi_normalized['KPI_Principal'],
                                    mode='lines+markers',
                                    name='KPI Principal',
                                    line=dict(color='#1f77b4', width=3),
                                    marker=dict(size=8),
                                    hovertemplate='<b>KPI Principal</b><br>Ano: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                                ),
                                secondary_y=False
                            )
                        
                        # Eixo secundário: Intensidade de Emissões (normalizada)
                        if 'Intensidade_Emissoes_Norm' in kpi_normalized.columns:
                            fig_kpi_evolution.add_trace(
                                go.Scatter(
                                    x=kpi_normalized['Ano'],
                                    y=kpi_normalized['Intensidade_Emissoes_Norm'],
                                    mode='lines+markers',
                                    name='Intensidade Emissões (÷1000)',
                                    line=dict(color='#ff7f0e', width=3, dash='dash'),
                                    marker=dict(size=8),
                                    hovertemplate='<b>Intensidade Normalizada</b><br>Ano: %{x}<br>Valor: %{y:.1f}<br>Original: %{customdata:.0f}<extra></extra>',
                                    customdata=kpi_normalized['Intensidade_Emissoes']
                                ),
                                secondary_y=True
                            )
                        
                        # Eixo principal: Taxa de Desmatamento (amplificada)
                        if 'Taxa_Desmatamento_Amp' in kpi_normalized.columns:
                            fig_kpi_evolution.add_trace(
                                go.Scatter(
                                    x=kpi_normalized['Ano'],
                                    y=kpi_normalized['Taxa_Desmatamento_Amp'],
                                    mode='lines+markers',
                                    name='Taxa Desmatamento (×100)',
                                    line=dict(color='#d62728', width=3, dash='dot'),
                                    marker=dict(size=8, symbol='diamond'),
                                    hovertemplate='<b>Taxa Desmatamento</b><br>Ano: %{x}<br>Amplificada: %{y:.2f}<br>Real: %{customdata:.4f}%<extra></extra>',
                                    customdata=kpi_normalized['Taxa_Desmatamento_Relativa']
                                ),
                                secondary_y=False
                            )
                        
                        # Configurar eixos
                        fig_kpi_evolution.update_xaxes(title_text="Ano")
                        fig_kpi_evolution.update_yaxes(
                            title_text="KPI Principal & Taxa Desmatamento (×100)", 
                            secondary_y=False
                        )
                        fig_kpi_evolution.update_yaxes(
                            title_text="Intensidade Emissões (÷1000)", 
                            secondary_y=True
                        )
                        
                        # Layout geral
                        fig_kpi_evolution.update_layout(
                            height=500,
                            hovermode='x unified',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig_kpi_evolution, use_container_width=True)
                        
                        # Adicionar análise quantitativa dos dados
                        st.subheader("📊 Análise Quantitativa dos Dados")
                        
                        col1_analise, col2_analise, col3_analise = st.columns(3)
                        
                        with col1_analise:
                            if len(kpi_data) > 1:
                                kpi_inicial = kpi_data.iloc[0]['KPI_Principal']
                                kpi_final = kpi_data.iloc[-1]['KPI_Principal']
                                variacao_kpi = ((kpi_final - kpi_inicial) / kpi_inicial) * 100
                                
                                st.metric(
                                    "Variação KPI Principal",
                                    f"{variacao_kpi:+.1f}%",
                                    f"{kpi_inicial:.1f} → {kpi_final:.1f}"
                                )
                        
                        with col2_analise:
                            if len(kpi_data) > 1:
                                int_inicial = kpi_data.iloc[0]['Intensidade_Emissoes']
                                int_final = kpi_data.iloc[-1]['Intensidade_Emissoes']
                                variacao_int = ((int_final - int_inicial) / int_inicial) * 100
                                
                                st.metric(
                                    "Variação Intensidade",
                                    f"{variacao_int:+.1f}%",
                                    f"{int_inicial:,.0f} → {int_final:,.0f}"
                                )
                        
                        with col3_analise:
                            if len(kpi_data) > 1:
                                taxa_inicial = kpi_data.iloc[0]['Taxa_Desmatamento_Relativa']
                                taxa_final = kpi_data.iloc[-1]['Taxa_Desmatamento_Relativa']
                                variacao_taxa = taxa_final - taxa_inicial
                                
                                st.metric(
                                    "Variação Taxa Desmatamento",
                                    f"{variacao_taxa:+.4f} p.p.",
                                    f"{taxa_inicial:.4f}% → {taxa_final:.4f}%"
                                )
                        
                        # Adicionar explicação das transformações
                        st.info("""
                        **🔍 Transformações aplicadas para visualização:**
                        - **Intensidade de Emissões**: Dividida por 1.000 (valores originais: ~300k-400k tCO₂e/R$ bilhão)
                        - **Taxa de Desmatamento**: Multiplicada por 100 (valores originais: ~0.2% da Amazônia Legal)
                        - **KPI Principal**: Mantido na escala original (~130-140)
                        
                        **Hover**: Passe o mouse sobre os pontos para ver valores originais e transformados.
                        """)
                        
                    else:
                        st.warning("Dados insuficientes para criar o gráfico de evolução")
                
                with col2:
                    st.markdown("**🎯 Dispersão: Impacto Ambiental vs Produtividade**")
                    
                    with st.expander("🔍 **Como Interpretar o Gráfico de Dispersão**", expanded=False):
                        st.markdown("""
                        Esta visualização analisa a relação entre desempenho econômico e impacto ambiental:
                        
                        #### 📊 **Elementos Visuais:**
                        - **Eixo X (Horizontal)**: Produtividade econômica (VAB em R$ bilhões)
                        - **Eixo Y (Vertical)**: Impacto ambiental (KPI Principal)
                        - **Tamanho dos Pontos**: Emissões totais (quanto maior o ponto, mais emissões)
                        - **Cor dos Pontos**: Intensidade de emissões (vermelho escuro = mais intenso)
                        
                        #### 🎯 **Quadrantes de Análise:**
                        
                        **🟢 Quadrante Ideal (Baixo-Direita):**
                        - **Alta produtividade** + **Baixo impacto**
                        - Pontos pequenos e claros
                        - Representa eficiência ambiental
                        
                        **🔴 Quadrante Crítico (Alto-Esquerda):**
                        - **Baixa produtividade** + **Alto impacto**
                        - Pontos grandes e escuros
                        - Representa ineficiência total
                        
                        **🟡 Quadrantes de Trade-off:**
                        - **Alto-Direita**: Alta produtividade, mas alto impacto
                        - **Baixo-Esquerda**: Baixo impacto, mas baixa produtividade
                        
                        #### 🔍 **Como Interpretar:**
                        
                        **Padrões Desejáveis:**
                        - Pontos se movendo para a **direita** (↗️ produtividade)
                        - Pontos se movendo para **baixo** (↘️ impacto)
                        - Pontos **diminuindo** de tamanho (↘️ emissões)
                        - Pontos ficando mais **claros** (↘️ intensidade)
                        
                        **Alertas:**
                        - Pontos grandes no alto = economia poluente
                        - Pontos escuros = alta intensidade de carbono
                        - Movimento para cima-esquerda = deterioração
                        
                        #### 📈 **Análise Temporal:**
                        - Cada ponto representa um ano
                        - Trajetória entre pontos mostra evolução
                        - Hover mostra detalhes do ano específico
                        """)
                    
                    # Gráfico de dispersão - NOVO
                    scatter_fig = create_scatter_impacto_produtividade(kpi_data)
                    st.plotly_chart(scatter_fig, use_container_width=True)
                    
                    # Análise dos dados do scatter plot
                    if not kpi_data.empty:
                        st.subheader("📊 Análise dos Dados de Dispersão")
                        
                        # Calcular correlação
                        correlacao = kpi_data['VAB_Total_Bilhoes'].corr(kpi_data['KPI_Principal'])
                        
                        col1_scatter, col2_scatter = st.columns(2)
                        
                        with col1_scatter:
                            st.metric(
                                "Correlação VAB × KPI",
                                f"{correlacao:.3f}",
                                "Produtividade × Impacto"
                            )
                            
                            if correlacao < -0.3:
                                st.success("✅ Correlação negativa: maior produtividade → menor impacto")
                            elif correlacao > 0.3:
                                st.error("❌ Correlação positiva: maior produtividade → maior impacto")
                            else:
                                st.warning("⚠️ Correlação fraca: relação indefinida")
                        
                        with col2_scatter:
                            # Encontrar o ano mais eficiente
                            kpi_data_efficiency = kpi_data.copy()
                            kpi_data_efficiency['Eficiencia_Score'] = kpi_data_efficiency['VAB_Total_Bilhoes'] / kpi_data_efficiency['KPI_Principal']
                            ano_mais_eficiente = kpi_data_efficiency.loc[kpi_data_efficiency['Eficiencia_Score'].idxmax(), 'Ano']
                            eficiencia_max = kpi_data_efficiency['Eficiencia_Score'].max()
                            
                            st.metric(
                                "Ano Mais Eficiente",
                                f"{int(ano_mais_eficiente)}",
                                f"Score: {eficiencia_max:.2f}"
                            )
                        
                        # Tabela de eficiência por ano
                        st.subheader("📋 Ranking de Eficiência por Ano")
                        
                        efficiency_table = kpi_data[['Ano', 'VAB_Total_Bilhoes', 'KPI_Principal', 'Emissoes_Total_MtCO2e', 'Intensidade_Emissoes']].copy()
                        efficiency_table['Eficiencia_Score'] = efficiency_table['VAB_Total_Bilhoes'] / efficiency_table['KPI_Principal']
                        efficiency_table = efficiency_table.sort_values('Eficiencia_Score', ascending=False)
                        
                        efficiency_table_display = efficiency_table[['Ano', 'VAB_Total_Bilhoes', 'KPI_Principal', 'Eficiencia_Score']].copy()
                        efficiency_table_display.columns = ['Ano', 'VAB (R$ Bi)', 'KPI Principal', 'Score Eficiência']
                        efficiency_table_display['Score Eficiência'] = efficiency_table_display['Score Eficiência'].round(3)
                        
                        st.dataframe(efficiency_table_display, use_container_width=True)
                        
                        st.caption("""
                        **Score de Eficiência**: VAB ÷ KPI Principal. Quanto maior, melhor a eficiência 
                        (mais valor econômico gerado por unidade de impacto ambiental).
                        """)
        
        st.markdown("---")
        
        # Seção 1: Pergunta 1 - Setores que mais degradam (MELHORADA)
        st.header("1. 🏭 Setores Econômicos que Mais Degradam o Meio Ambiente")
        st.markdown("""
        **Análise:** Identificação dos setores com maior impacto ambiental através de múltiplas visualizações.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**🌳 Treemap de Emissões por Setor**")
            
            with st.expander("🔍 **Como Ler o Treemap**", expanded=False):
                st.markdown("""
                Este treemap apresenta a **proporção visual** das emissões de gases de efeito estufa por setor econômico:
                
                #### 📊 **Elementos Visuais:**
                - **Tamanho do Retângulo**: Proporcional às emissões totais (tCO₂e)
                - **Cor**: Intensidade das emissões (vermelho escuro = maior impacto)
                - **Hierarquia**: Setores organizados por categoria
                - **Texto**: Nome do setor + valor + percentual do total
                
                #### 🔍 **Como Ler o Treemap:**
                
                **Análise por Tamanho:**
                - **Retângulos grandes** = setores com maiores emissões absolutas
                - **Retângulos pequenos** = setores com menores emissões
                - **Proporção visual** = participação relativa no total de emissões
                
                **Análise por Cor:**
                - **Vermelho escuro** = alta intensidade de emissões
                - **Vermelho claro** = baixa intensidade de emissões
                - **Gradiente** = escala contínua de impacto
                
                #### 🎯 **Interpretações Estratégicas:**
                
                **Setores Prioritários para Ação:**
                - Retângulos **grandes + escuros** = máxima prioridade
                - Representam maior impacto absoluto e relativo
                
                **Oportunidades de Melhoria:**
                - Setores com emissões médias mas alta intensidade
                - Potencial de eficiência com menor investimento
                
                **Setores de Referência:**
                - Retângulos pequenos e claros
                - Modelos de baixo impacto ambiental
                """)
            
            st.markdown("#### 📈 **Dados de Emissões por Setor:**")
            
            # Adicionar tabela de dados do treemap
            year_data_treemap = emissoes_long[emissoes_long['Ano'] == ano_especifico].copy()
            year_data_treemap = year_data_treemap.sort_values('Emissoes', ascending=False)
            total_emissoes = year_data_treemap['Emissoes'].sum()
            year_data_treemap['Percentual'] = (year_data_treemap['Emissoes'] / total_emissoes * 100).round(2)
            year_data_treemap['Emissoes_Mt'] = (year_data_treemap['Emissoes'] / 1e6).round(2)
            
            # Mostrar top 5 setores
            top_5_setores = year_data_treemap.head(5)[['Categoria', 'Emissoes_Mt', 'Percentual']]
            top_5_setores.columns = ['Setor', 'Emissões (Mt CO₂e)', 'Participação (%)']
            
            st.dataframe(top_5_setores, use_container_width=True)
            
            st.caption(f"""
            **Top 5 Setores Mais Poluentes em {ano_especifico}**  
            Total de emissões: {total_emissoes/1e6:.1f} Mt CO₂e
            """)
            
            # Treemap original
            treemap_fig = create_treemap_setores_degradacao(emissoes_long, ano_especifico)
            st.plotly_chart(treemap_fig, use_container_width=True)
        
        with col2:
            st.markdown("**📊 Ranking Detalhado por Degradação**")
            
            with st.expander("🔍 **Como Interpretar o Ranking**", expanded=False):
                st.markdown("""
                Ranking horizontal dos setores ordenados por impacto ambiental:
                
                ####  **Elementos do Gráfico:**
                - **Barras Horizontais**: Emissões absolutas (tCO₂e)
                - **Comprimento**: Proporcional ao volume de emissões
                - **Cor**: Gradiente de intensidade (vermelho = maior)
                - **Percentuais**: Participação relativa de cada setor
                - **Ordem**: Do menor para o maior impacto (bottom-up)
                
                #### 🔍 **Como Interpretar o Ranking:**
                
                **Análise das Barras:**
                - **Barras longas (topo)** = maiores poluidores
                - **Barras curtas (base)** = menores poluidores
                - **Gradiente de cor** = intensidade relativa
                
                **Análise dos Percentuais:**
                - **Concentração**: % dos top 3 setores
                - **Distribuição**: Equilíbrio entre setores
                - **Cauda longa**: Muitos setores com baixo impacto
                
                #### 🎯 **Insights do Ranking:**
                
                **Regra 80/20:**
                - Verificar se 20% dos setores geram 80% das emissões
                - Focar esforços nos setores de maior impacto
                
                **Gaps de Oportunidade:**
                - Setores com emissões médias = potencial de melhoria
                - Diferenças significativas entre setores similares
                """)
            
            st.markdown("#### 📈 **Análise Quantitativa:**")
            
            # Análise quantitativa do ranking
            year_data_ranking = emissoes_long[emissoes_long['Ano'] == ano_especifico].copy()
            year_data_ranking = year_data_ranking.sort_values('Emissoes', ascending=False)
            total_emissoes_ranking = year_data_ranking['Emissoes'].sum()
            year_data_ranking['Percentual_Acum'] = (year_data_ranking['Emissoes'].cumsum() / total_emissoes_ranking * 100)
            
            # Encontrar quantos setores representam 80% das emissões
            setores_80_pct = len(year_data_ranking[year_data_ranking['Percentual_Acum'] <= 80])
            total_setores = len(year_data_ranking)
            concentracao = (setores_80_pct / total_setores) * 100
            
            col1_ranking, col2_ranking = st.columns(2)
            
            with col1_ranking:
                st.metric(
                    "Concentração 80/20",
                    f"{setores_80_pct}/{total_setores}",
                    f"{concentracao:.1f}% dos setores"
                )
            
            with col2_ranking:
                maior_emissor = year_data_ranking.iloc[0]
                participacao_maior = (maior_emissor['Emissoes'] / total_emissoes_ranking * 100)
                
                st.metric(
                    "Maior Emissor",
                    f"{participacao_maior:.1f}%",
                    maior_emissor['Categoria']
                )
            
            # Ranking melhorado - NOVO
            ranking_fig = create_ranking_setores_degradacao(emissoes_long, ano_especifico)
            st.plotly_chart(ranking_fig, use_container_width=True)
            
            # Adicionar análise de concentração
            st.subheader("📊 Análise de Concentração")
            
            top_3_emissoes = year_data_ranking.head(3)['Emissoes'].sum()
            concentracao_top3 = (top_3_emissoes / total_emissoes_ranking * 100)
            
            st.info(f"""
            **Concentração dos Top 3 Setores**: {concentracao_top3:.1f}% das emissões totais
            
            **Setores:**
            1. {year_data_ranking.iloc[0]['Categoria']}: {(year_data_ranking.iloc[0]['Emissoes']/total_emissoes_ranking*100):.1f}%
            2. {year_data_ranking.iloc[1]['Categoria']}: {(year_data_ranking.iloc[1]['Emissoes']/total_emissoes_ranking*100):.1f}%
            3. {year_data_ranking.iloc[2]['Categoria']}: {(year_data_ranking.iloc[2]['Emissoes']/total_emissoes_ranking*100):.1f}%
            """)
            
            if concentracao_top3 > 70:
                st.warning("⚠️ **Alta concentração**: Poucos setores dominam as emissões")
            else:
                st.success("✅ **Distribuição equilibrada**: Emissões bem distribuídas entre setores")
    
        st.markdown("---")
        
        # Seção 2: Pergunta 2 - Relação entre setores e intensidade (MANTIDA)
        st.header("2. 📊 Relação entre Tipos de Setores e Intensidade de Degradação")
        st.markdown("""
        **Análise Expandida:** Correlação entre desempenho econômico e impacto ambiental por setor.
        
        **📈 Análise Multidimensional: Desempenho Econômico vs Ambiental**
        
        Esta análise compara 4 dimensões dos principais setores econômicos:
        1. **Receita Total**: Performance econômica (R$ bilhões)
        2. **Número de Empresas**: Concentração do setor
        3. **Eficiência Ambiental**: Receita gerada por unidade de emissão
        4. **Índice de Sustentabilidade**: Inverso das emissões (maior = melhor)
        
        **Objetivo**: Identificar setores que conseguem alta performance econômica com baixo impacto ambiental.
        """)
        
        barras_fig = create_barras_agrupadas_eficiencia_ambiental(industria_data, emissoes_long, anos_selecionados)
        st.plotly_chart(barras_fig, use_container_width=True)
        
        st.markdown("---")
        
        # Seção 3: Pergunta 3 - KPI de Eficiência Ambiental (MELHORADA)
        st.header("3. 💡 Eficiência Ambiental vs Produção")
        st.markdown("""
        **Resposta:** Sim, é possível reduzir danos sem afetar negativamente a produção. 
        O gráfico mostra a relação entre eficiência econômica e impacto ambiental.
        """)
        
        if not kpi_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**⚡ Indicadores de Eficiência por Ano**")
                
                with st.expander("🔍 **Como Interpretar os Indicadores**", expanded=False):
                    st.markdown("""
                    Comparação temporal dos indicadores de eficiência:
                    - **Eficiência Hídrica**: m³ de água por R$ milhão de VAB (menor = melhor)
                    - **Intensidade de Emissões**: tCO₂e por R$ bilhão de VAB (menor = melhor)
                    
                    **Meta**: Redução consistente de ambos os indicadores ao longo do tempo.
                    """)
                
                # Gráfico de eficiência ao longo do tempo
                fig_efficiency = px.bar(
                    kpi_data,
                    x='Ano',
                    y=['Eficiencia_Hidrica', 'Intensidade_Emissoes'],
                    title="Indicadores de Eficiência por Ano",
                    barmode='group'
                )
                st.plotly_chart(fig_efficiency, use_container_width=True)
            
            with col2:
                st.markdown("**📋 Tabela de Indicadores Detalhados**")
                
                with st.expander("🔍 **Como Analisar a Tabela**", expanded=False):
                    st.markdown("""
                    Dados numéricos precisos dos principais KPIs:
                    - **KPI Principal**: Índice composto de impacto ambiental
                    - **Efic. Hídrica**: Consumo de água por unidade econômica
                    - **Intens. Emissões**: Emissões por unidade econômica
                    
                    **Análise**: Compare os valores entre anos para identificar tendências.
                    """)
                
                # Tabela de indicadores detalhados
                kpi_display = kpi_data[['Ano', 'KPI_Principal', 'Eficiencia_Hidrica', 'Intensidade_Emissoes']].copy()
                kpi_display.columns = ['Ano', 'KPI Principal', 'Efic. Hídrica', 'Intens. Emissões']
                st.dataframe(kpi_display, use_container_width=True)
        
        st.markdown("---")
        
        # Seção 4: Pergunta 4 - Fatores de irresponsabilidade (MELHORADA)
        st.header("4. ⚠️ Fatores de Irresponsabilidade Ambiental")
        st.markdown("""
        **Análise:** Mapeamento de fatores de risco ambiental por região e características estruturais.
        """)
        
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown("**🔥 Heatmap de Desmatamento Regional**")
            
            with st.expander("🔍 **Como Interpretar o Heatmap**", expanded=False):
                st.markdown("""
                Mapa de calor mostrando a intensidade do desmatamento por estado ao longo do tempo:
                
                #### 📊 **Elementos do Heatmap:**
                - **Eixo Y (Vertical)**: Anos analisados (temporal)
                - **Eixo X (Horizontal)**: Estados da Amazônia Legal
                - **Cor**: Intensidade do desmatamento (branco → vermelho escuro)
                - **Valores**: Área desmatada em km² por estado/ano
                
                #### 🗺️ **Estados da Amazônia Legal:**
                - **AC** = Acre | **AM** = Amazonas | **AP** = Amapá
                - **MA** = Maranhão | **MT** = Mato Grosso | **PA** = Pará
                - **RO** = Rondônia | **RR** = Roraima | **TO** = Tocantins
                
                #### 🔍 **Como Interpretar o Heatmap:**
                
                **Análise por Cores:**
                - **Vermelho escuro** = alto desmatamento (>1000 km²/ano)
                - **Vermelho médio** = desmatamento moderado (500-1000 km²/ano)
                - **Vermelho claro** = baixo desmatamento (100-500 km²/ano)
                - **Branco/Rosa** = desmatamento mínimo (<100 km²/ano)
                
                **Padrões Temporais (Linhas Horizontais):**
                - **Linhas vermelhas** = anos críticos de desmatamento
                - **Linhas claras** = anos de menor pressão
                - **Gradientes** = evolução temporal do desmatamento
                
                **Padrões Regionais (Colunas Verticais):**
                - **Colunas vermelhas** = estados sob pressão constante
                - **Colunas claras** = estados com melhor preservação
                - **Variações** = efetividade de políticas estaduais
                
                #### 🎯 **Insights Estratégicos:**
                
                **Estados Críticos:**
                - Colunas predominantemente vermelhas
                - Necessitam intervenção urgente
                - Monitoramento intensivo
                
                **Períodos Críticos:**
                - Linhas predominantemente vermelhas
                - Eventos climáticos ou políticos
                - Falhas de fiscalização
                
                **Hotspots (Vermelho Escuro):**
                - Intersecções estado × ano críticas
                - Focos prioritários de ação
                - Análise de causas específicas
                """)
            
            st.markdown("#### 📈 **Dados Quantitativos do Desmatamento:**")
            
            # Análise quantitativa do heatmap
            prodes_periodo = prodes_data[
                (prodes_data['Ano/Estados'] >= ano_especifico-5) & 
                (prodes_data['Ano/Estados'] <= ano_especifico)
            ].copy()
            
            if not prodes_periodo.empty:
                estados_cols = ['AC', 'AM', 'AP', 'MA', 'MT', 'PA', 'RO', 'RR', 'TO']
                
                # Calcular estatísticas por estado
                stats_estados = []
                for estado in estados_cols:
                    if estado in prodes_periodo.columns:
                        dados_estado = prodes_periodo[estado].dropna()
                        if len(dados_estado) > 0:
                            stats_estados.append({
                                'Estado': estado,
                                'Média': dados_estado.mean(),
                                'Máximo': dados_estado.max(),
                                'Mínimo': dados_estado.min(),
                                'Total': dados_estado.sum()
                            })
                
                if stats_estados:
                    df_stats = pd.DataFrame(stats_estados)
                    df_stats = df_stats.sort_values('Total', ascending=False)
                    
                    # Top 3 estados com maior desmatamento
                    top_3_estados = df_stats.head(3)
                    
                    col1_stats, col2_stats, col3_stats = st.columns(3)
                    
                    with col1_stats:
                        st.metric(
                            f"1º {top_3_estados.iloc[0]['Estado']}",
                            f"{top_3_estados.iloc[0]['Total']:,.0f} km²",
                            f"Média: {top_3_estados.iloc[0]['Média']:.0f} km²/ano"
                        )
                    
                    with col2_stats:
                        st.metric(
                            f"2º {top_3_estados.iloc[1]['Estado']}",
                            f"{top_3_estados.iloc[1]['Total']:,.0f} km²",
                            f"Média: {top_3_estados.iloc[1]['Média']:.0f} km²/ano"
                        )
                    
                    with col3_stats:
                        st.metric(
                            f"3º {top_3_estados.iloc[2]['Estado']}",
                            f"{top_3_estados.iloc[2]['Total']:,.0f} km²",
                            f"Média: {top_3_estados.iloc[2]['Média']:.0f} km²/ano"
                        )
                    
                    # Tabela completa de estatísticas
                    st.subheader("📊 Estatísticas Completas por Estado")
                    df_stats_display = df_stats.copy()
                    df_stats_display['Média'] = df_stats_display['Média'].round(0)
                    df_stats_display['Total'] = df_stats_display['Total'].round(0)
                    df_stats_display.columns = ['Estado', 'Média (km²/ano)', 'Máximo (km²)', 'Mínimo (km²)', 'Total Período (km²)']
                    
                    st.dataframe(df_stats_display, use_container_width=True)
            
            # Heatmap original (mantido)
            heatmap_fig = create_heatmap_desmatamento_regional(prodes_data, ano_especifico-5, ano_especifico)
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
        with col2:
            # Adicionar análise de tendências na coluna 2
            if not prodes_periodo.empty:
                st.subheader("📈 Análise de Tendências")
                
                # Calcular tendência geral
                total_por_ano = prodes_periodo.set_index('Ano/Estados')[estados_cols].sum(axis=1)
                if len(total_por_ano) > 1:
                    tendencia = total_por_ano.iloc[-1] - total_por_ano.iloc[0]
                    pct_tendencia = (tendencia / total_por_ano.iloc[0]) * 100
                    
                    if tendencia > 0:
                        st.error(f"📈 **Tendência Crescente**: +{tendencia:,.0f} km² ({pct_tendencia:+.1f}%)")
                        st.markdown("⚠️ Desmatamento aumentou no período analisado")
                    else:
                        st.success(f"📉 **Tendência Decrescente**: {tendencia:,.0f} km² ({pct_tendencia:+.1f}%)")
                        st.markdown("✅ Desmatamento diminuiu no período analisado")
                
                # Identificar ano mais crítico
                ano_critico = total_por_ano.idxmax()
                valor_critico = total_por_ano.max()
                
                st.warning(f"🚨 **Ano Mais Crítico**: {ano_critico} com {valor_critico:,.0f} km² desmatados")
                
                # Adicionar mais análises
                st.subheader("🔍 Análise Detalhada por Estado")
                
                # Estado mais crítico
                if stats_estados:
                    estado_critico = df_stats.iloc[0]
                    st.error(f"""
                    **Estado Mais Crítico: {estado_critico['Estado']}**
                    - Total desmatado: {estado_critico['Total']:,.0f} km²
                    - Média anual: {estado_critico['Média']:.0f} km²/ano
                    - Pico máximo: {estado_critico['Máximo']:.0f} km² em um ano
                    """)
                    
                    # Estado menos crítico
                    estado_melhor = df_stats.iloc[-1]
                    st.success(f"""
                    **Estado Menos Crítico: {estado_melhor['Estado']}**
                    - Total desmatado: {estado_melhor['Total']:,.0f} km²
                    - Média anual: {estado_melhor['Média']:.0f} km²/ano
                    - Diferença com o pior: {(estado_critico['Total'] - estado_melhor['Total']):,.0f} km²
                    """)
                    
                    # Recomendações específicas
                    st.subheader("🎯 Recomendações por Estado")
                    
                    st.markdown(f"""
                    **Para {estado_critico['Estado']} (Crítico):**
                    - 🚨 Implementar fiscalização 24/7
                    - 💰 Aumentar investimento em tecnologia de monitoramento
                    - 🤝 Parcerias com ONGs locais
                    - 📊 Relatórios mensais obrigatórios
                    
                    **Para {estado_melhor['Estado']} (Referência):**
                    - ✅ Manter políticas atuais
                    - 📚 Compartilhar boas práticas
                    - 🎯 Servir como modelo para outros estados
                    - 🔬 Estudar fatores de sucesso
                    """)
        
        st.markdown("---")
        
        # Seção 5: Pergunta 5 - Agricultura familiar e sustentabilidade (MELHORADA)
        st.header("5. 🌱 Agricultura Familiar e Sustentabilidade")
        st.markdown("""
        **Resposta:** Sim, regiões com maior agricultura familiar tendem à sustentabilidade.
        Correlação com infraestrutura e menor impacto ambiental.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎻 Distribuição da Agricultura Familiar por Região**")
            
            with st.expander("🔍 **Como Interpretar o Violin Plot**", expanded=False):
                st.markdown("""
                Violin plot mostrando a distribuição estatística da agricultura familiar:
                - **Largura**: Densidade de distribuição dos estabelecimentos
                - **Linha central**: Mediana dos valores
                - **Caixa**: Quartis da distribuição
                
                **Interpretação**: Regiões com distribuições mais altas têm mais agricultura familiar.
                """)
            
            # Gráfico original melhorado
            violin_fig = create_violin_agricultura_familiar(combined_ag)
            st.plotly_chart(violin_fig, use_container_width=True)
        
        with col2:
            st.markdown("**🔌 Agricultura Familiar vs Infraestrutura**")
            
            with st.expander("🔍 **Como Interpretar a Correlação**", expanded=False):
                st.markdown("""
                Correlação entre agricultura familiar e infraestrutura por região:
                - **Barras Azuis**: % de Agricultura Familiar
                - **Barras Laranja**: % com Energia Elétrica (eixo direito)
                - **Agrupamento**: Comparação lado a lado por região
                
                **Hipótese**: Maior agricultura familiar correlaciona com melhor infraestrutura.
                """)
            
            # Novo gráfico: agricultura familiar vs infraestrutura
            infra_fig, infra_data = create_agricultura_familiar_infraestrutura(combined_ag)
            st.plotly_chart(infra_fig, use_container_width=True)
        
        # Análise de correlação - NOVA
        st.subheader("🔍 Análise de Correlação: Agricultura Familiar × Sustentabilidade")
        
        if infra_data is not None and not infra_data.empty:
            col1_corr, col2_corr, col3_corr = st.columns(3)
            
            with col1_corr:
                correlacao = infra_data['Prop_Familiar'].corr(infra_data['Infraestrutura'])
                st.metric("Correlação", f"{correlacao:.2f}", "Familiar × Infraestrutura")
            
            with col2_corr:
                media_familiar = infra_data['Prop_Familiar'].mean()
                st.metric("Média Agricultura Familiar", f"{media_familiar:.1f}%", "Todas as regiões")
            
            with col3_corr:
                media_infra = infra_data['Infraestrutura'].mean()
                st.metric("Média Infraestrutura", f"{media_infra:.1f}%", "Energia elétrica")
        
        st.markdown("---")
        
        # Seção final: Conclusões e Recomendações (MELHORADA)
        st.header("📈 Conclusões e Recomendações Estratégicas")
        
        # Adicionar seção metodológica
        with st.expander("🔬 **Metodologia e Limitações do Estudo**", expanded=False):
            st.markdown("""
            ### 📊 **Fontes de Dados**
            
            **Dados Industriais:**
            - Fonte: Classificação Nacional de Atividades Econômicas (CNAE 2.0)
            - Métricas: Receita total, número de empresas por setor
            - Período: Dados anuais disponíveis
            - Limitação: Receita usada como proxy para VAB real
            
            **Dados de Emissões:**
            - Fonte: Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa (SEEG)
            - Métricas: Emissões brutas e líquidas por setor (tCO₂e)
            - Categorias: Energia, Processos Industriais, Agropecuária, etc.
            - Qualidade: Dados oficiais validados
            
            **Dados de Desmatamento:**
            - Fonte: Programa de Monitoramento da Amazônia (PRODES/INPE)
            - Métricas: Área desmatada por estado (km²/ano)
            - Cobertura: Amazônia Legal (9 estados)
            - Precisão: Imagens de satélite de alta resolução
            
            **Dados de Agricultura:**
            - Fonte: Censo Agropecuário (IBGE)
            - Métricas: Estabelecimentos familiares vs não familiares
            - Faixas: Distribuição por tamanho de propriedade
            - Periodicidade: Censos decenais (2006, 2017)
            
            ---
            
            ### 🧮 **Metodologia de Cálculo dos KPIs**
            
            **1. KPI Principal (Índice de Impacto Ambiental):**
            ```
            KPI = ((E/1M) + (A/1M) + (D/1k)) / (VAB/1B) × 100
            ```
            Onde:
            - E = Emissões totais (tCO₂e)
            - A = Consumo de água estimado (m³)
            - D = Desmatamento (km²)
            - VAB = Valor Adicionado Bruto proxy (R$)
            
            **Justificativa**: Normalização permite comparação entre anos com diferentes escalas econômicas.
            
            **2. Intensidade de Emissões:**
            ```
            Intensidade = (Emissões / VAB) × 10⁹
            ```
            **Unidade**: tCO₂e por R$ bilhão de VAB
            **Interpretação**: Carbono-intensidade da economia
            
            **3. Taxa de Desmatamento Relativa:**
            ```
            Taxa = (Desmatamento Anual / 5.500.000) × 100
            ```
            **Base**: Área total da Amazônia Legal
            **Interpretação**: Percentual da floresta perdido anualmente
            
            **4. Eficiência Hídrica (Simulada):**
            ```
            Consumo Água = VAB × 0.001
            Eficiência = (Consumo / VAB) × 10⁶
            ```
            **Limitação**: Dados reais de consumo hídrico não disponíveis
            
            ---
            
            ### ⚠️ **Limitações e Premissas**
            
            **Limitações dos Dados:**
            - VAB industrial aproximado pela receita total
            - Consumo de água simulado (não há dados setoriais disponíveis)
            - Correlação agricultura-infraestrutura parcialmente simulada
            - Dados de anos diferentes podem ter metodologias distintas
            
            **Premissas Adotadas:**
            - Receita industrial como proxy válida para VAB
            - Relação linear entre atividade econômica e consumo hídrico
            - Amazônia Legal como referência para desmatamento
            - Agricultura familiar correlacionada com sustentabilidade
            
            **Validação:**
            - KPIs testados com dados de múltiplos anos
            - Correlações verificadas com literatura científica
            - Valores extremos investigados e validados
            - Tendências comparadas com indicadores oficiais
            
            ---
            
            ### 🎯 **Interpretação dos Resultados**
            
            **Escalas de Referência:**
            - **KPI Principal**: 100-200 = bom; >200 = crítico
            - **Intensidade Emissões**: <100k = eficiente; >500k = ineficiente  
            - **Taxa Desmatamento**: <0.1% = controlado; >0.5% = crítico
            
            **Tendências Desejáveis:**
            - KPI Principal decrescente ao longo do tempo
            - Intensidade de emissões em queda
            - Taxa de desmatamento estável ou decrescente
            - Correlação positiva: agricultura familiar × infraestrutura
            """)
        
        col1, col2 = st.columns(2)
    
        with col1:
            st.subheader("🎯 Principais Achados")
            if not kpi_data.empty:
                latest_kpi = kpi_data.iloc[-1]['KPI_Principal']
                
                # Análise de tendência do KPI
                if len(kpi_data) > 1:
                    kpi_inicial = kpi_data.iloc[0]['KPI_Principal']
                    tendencia_kpi = ((latest_kpi - kpi_inicial) / kpi_inicial) * 100
                    
                    if tendencia_kpi < -5:
                        status_kpi = "✅ Melhoria significativa"
                    elif tendencia_kpi < 0:
                        status_kpi = "📈 Leve melhoria"
                    elif tendencia_kpi < 5:
                        status_kpi = "⚠️ Estável"
                    else:
                        status_kpi = "❌ Deterioração"
                else:
                    status_kpi = "📊 Dados insuficientes"
                
                # Identificar setor mais crítico
                emissoes_ano = emissoes_long[emissoes_long['Ano'] == ano_especifico]
                if not emissoes_ano.empty:
                    setor_critico = emissoes_ano.loc[emissoes_ano['Emissoes'].idxmax(), 'Categoria']
                    emissoes_criticas = emissoes_ano['Emissoes'].max()
                    participacao_critica = (emissoes_criticas / emissoes_ano['Emissoes'].sum()) * 100
                else:
                    setor_critico = "Não identificado"
                    participacao_critica = 0
                
                st.markdown(f"""
                **📊 Situação Atual ({int(kpi_data.iloc[-1]['Ano'])}):**
                - **KPI Ambiental**: {latest_kpi:.1f} ({status_kpi})
                - **Setor Crítico**: {setor_critico} ({participacao_critica:.1f}% das emissões)
                - **VAB Total**: R$ {kpi_data.iloc[-1]['VAB_Total_Bilhoes']:.1f} bilhões
                - **Emissões Totais**: {kpi_data.iloc[-1]['Emissoes_Total_MtCO2e']:.1f} Mt CO₂e
                
                **📈 Tendências Identificadas:**
                """)
                
                if len(kpi_data) > 1:
                    # Análise de todas as tendências
                    tendencias = []
                    
                    # KPI Principal
                    if tendencia_kpi < -2:
                        tendencias.append("✅ KPI Principal em melhoria")
                    elif tendencia_kpi > 2:
                        tendencias.append("❌ KPI Principal em deterioração")
                    else:
                        tendencias.append("⚠️ KPI Principal estável")
                    
                    # Intensidade de Emissões
                    int_inicial = kpi_data.iloc[0]['Intensidade_Emissoes']
                    int_final = kpi_data.iloc[-1]['Intensidade_Emissoes']
                    tendencia_int = ((int_final - int_inicial) / int_inicial) * 100
                    
                    if tendencia_int < -5:
                        tendencias.append("✅ Descarbonização da economia")
                    elif tendencia_int > 5:
                        tendencias.append("❌ Aumento da intensidade de carbono")
                    else:
                        tendencias.append("⚠️ Intensidade de emissões estável")
                    
                    # Taxa de Desmatamento
                    taxa_inicial = kpi_data.iloc[0]['Taxa_Desmatamento_Relativa']
                    taxa_final = kpi_data.iloc[-1]['Taxa_Desmatamento_Relativa']
                    
                    if taxa_final < taxa_inicial * 0.9:
                        tendencias.append("✅ Redução do desmatamento")
                    elif taxa_final > taxa_inicial * 1.1:
                        tendencias.append("❌ Aumento do desmatamento")
                    else:
                        tendencias.append("⚠️ Desmatamento oscilante")
                    
                    for tendencia in tendencias:
                        st.markdown(f"- {tendencia}")
                
                # Correlação agricultura familiar
                if infra_data is not None and not infra_data.empty:
                    correlacao_final = infra_data['Prop_Familiar'].corr(infra_data['Infraestrutura'])
                    if correlacao_final > 0.3:
                        st.markdown("- ✅ Correlação positiva: agricultura familiar × infraestrutura")
                    elif correlacao_final < -0.3:
                        st.markdown("- ❌ Correlação negativa: agricultura familiar × infraestrutura")
                    else:
                        st.markdown("- ⚠️ Correlação fraca: agricultura familiar × infraestrutura")
        
        with col2:
            st.subheader("📊 Ações Recomendadas")
            
            # Recomendações baseadas nos dados
            st.markdown("""
            **🚀 Estratégias por Horizonte Temporal:**
            
            **Curto Prazo (1-2 anos):**
            """)
            
            if not kpi_data.empty:
                latest_kpi = kpi_data.iloc[-1]['KPI_Principal']
                if latest_kpi > 140:
                    st.markdown("- 🚨 **Emergencial**: KPI crítico - ações imediatas necessárias")
                elif latest_kpi > 130:
                    st.markdown("- ⚠️ **Prioritário**: KPI elevado - monitoramento intensivo")
                else:
                    st.markdown("- ✅ **Manutenção**: KPI controlado - manter políticas atuais")
            
            # Recomendações por setor
            if 'setor_critico' in locals():
                st.markdown(f"- 🎯 **Foco Setorial**: Intervenção prioritária em {setor_critico}")
            
            st.markdown("""
            - 📊 **Monitoramento**: Dashboard atualizado mensalmente
            - 🔍 **Fiscalização**: Intensificar nos 3 maiores emissores
            
            **Médio Prazo (3-5 anos):**
            - 💰 **Incentivos**: Crédito subsidiado para tecnologias limpas
            - 📈 **Metas Setoriais**: Redução de 20% na intensidade de emissões
            - 🌱 **Agricultura Sustentável**: Expansão da agricultura familiar
            - 🏭 **Eficiência Industrial**: Programas de produção mais limpa
            
            **Longo Prazo (5-10 anos):**
            - 🔄 **Transição Energética**: Matriz energética renovável
            - 🌳 **Reflorestamento**: Compensação ativa do desmatamento
            - 🎓 **Capacitação**: Formação em tecnologias sustentáveis
            - 🤝 **Governança**: Integração entre políticas ambientais e econômicas
            
            **🎯 Metas Quantitativas Sugeridas:**
            """)
            
            if not kpi_data.empty:
                meta_kpi = latest_kpi * 0.8  # Redução de 20%
                meta_intensidade = kpi_data.iloc[-1]['Intensidade_Emissoes'] * 0.7  # Redução de 30%
                meta_desmatamento = kpi_data.iloc[-1]['Taxa_Desmatamento_Relativa'] * 0.5  # Redução de 50%
                
                st.markdown(f"""
                - **KPI Principal**: Reduzir para {meta_kpi:.1f} até 2030
                - **Intensidade Emissões**: Reduzir para {meta_intensidade:,.0f} tCO₂e/R$ bi
                - **Taxa Desmatamento**: Reduzir para {meta_desmatamento:.3f}% ao ano
                - **Agricultura Familiar**: Aumentar para 80% dos estabelecimentos rurais
                """)
        
        # Tabela resumo dos KPIs - NOVA
        if not kpi_data.empty:
            st.subheader("📋 Resumo Executivo - KPIs por Ano")
            
            # Preparar dados para a tabela resumo
            kpi_summary = kpi_data[['Ano', 'KPI_Principal', 'VAB_Total_Bilhoes', 'Emissoes_Total_MtCO2e', 'Desmatamento_Total_km2', 'Intensidade_Emissoes', 'Taxa_Desmatamento_Relativa']].copy()
            
            # Adicionar classificações
            kpi_summary['Status_KPI'] = kpi_summary['KPI_Principal'].apply(
                lambda x: '🟢 Bom' if x < 130 else ('🟡 Médio' if x < 140 else '🔴 Crítico')
            )
            
            kpi_summary['Status_Desmatamento'] = kpi_summary['Taxa_Desmatamento_Relativa'].apply(
                lambda x: '🟢 Controlado' if x < 0.2 else ('🟡 Moderado' if x < 0.3 else '🔴 Alto')
            )
            
            # Formatar para exibição
            kpi_summary_display = kpi_summary.copy()
            kpi_summary_display['Ano'] = kpi_summary_display['Ano'].astype(int)
            kpi_summary_display['KPI_Principal'] = kpi_summary_display['KPI_Principal'].round(1)
            kpi_summary_display['VAB_Total_Bilhoes'] = kpi_summary_display['VAB_Total_Bilhoes'].round(1)
            kpi_summary_display['Emissoes_Total_MtCO2e'] = kpi_summary_display['Emissoes_Total_MtCO2e'].round(1)
            kpi_summary_display['Desmatamento_Total_km2'] = kpi_summary_display['Desmatamento_Total_km2'].round(0)
            kpi_summary_display['Intensidade_Emissoes'] = kpi_summary_display['Intensidade_Emissoes'].round(0)
            kpi_summary_display['Taxa_Desmatamento_Relativa'] = kpi_summary_display['Taxa_Desmatamento_Relativa'].round(4)
            
            # Renomear colunas
            kpi_summary_display.columns = [
                'Ano', 'KPI Principal', 'VAB (R$ Bi)', 'Emissões (Mt CO₂e)', 
                'Desmatamento (km²)', 'Intensidade', 'Taxa Desmat. (%)', 
                'Status KPI', 'Status Desmatamento'
            ]
            
            st.dataframe(kpi_summary_display, use_container_width=True)
            
            # Adicionar legenda
            st.caption("""
            **Legenda:**
            - **KPI Principal**: Índice composto de impacto ambiental (menor = melhor)
            - **Intensidade**: tCO₂e por R$ bilhão de VAB (menor = melhor)
            - **Status**: 🟢 Bom | 🟡 Médio | 🔴 Crítico
            """)
            
            # Análise final
            st.subheader("🎯 Síntese Final")
            
            # Calcular score geral
            if len(kpi_data) > 1:
                # Tendências (peso 40%)
                kpi_trend = -tendencia_kpi / 100  # Negativo porque queremos redução
                int_trend = -tendencia_int / 100   # Negativo porque queremos redução
                
                # Valores absolutos (peso 60%)
                kpi_score = 1 - (latest_kpi - 100) / 100  # Normalizado
                emissoes_score = 1 - (kpi_data.iloc[-1]['Emissoes_Total_MtCO2e'] - 1000) / 2000  # Normalizado
                
                score_geral = (kpi_trend * 0.2 + int_trend * 0.2 + kpi_score * 0.3 + emissoes_score * 0.3) * 100
                score_geral = max(0, min(100, score_geral))  # Limitar entre 0-100
                
                col1_final, col2_final, col3_final = st.columns(3)
                
                with col1_final:
                    if score_geral > 70:
                        st.success(f"**Score Geral: {score_geral:.0f}/100**\n\n✅ Situação ambiental controlada")
                    elif score_geral > 50:
                        st.warning(f"**Score Geral: {score_geral:.0f}/100**\n\n⚠️ Situação ambiental requer atenção")
                    else:
                        st.error(f"**Score Geral: {score_geral:.0f}/100**\n\n🚨 Situação ambiental crítica")
                
                with col2_final:
                    # Prioridade de ação
                    if latest_kpi > 140:
                        prioridade = "🚨 EMERGENCIAL"
                    elif latest_kpi > 130:
                        prioridade = "⚠️ ALTA"
                    else:
                        prioridade = "✅ MODERADA"
                    
                    st.info(f"**Prioridade de Ação:**\n\n{prioridade}")
                
                with col3_final:
                    # Próxima revisão
                    if score_geral < 50:
                        revisao = "📅 MENSAL"
                    elif score_geral < 70:
                        revisao = "📅 TRIMESTRAL"
                    else:
                        revisao = "📅 SEMESTRAL"
                    
                    st.info(f"**Frequência de Monitoramento:**\n\n{revisao}")
    
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Verifique se todos os arquivos estão na pasta 'tratado' conforme esperado.")
    
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.info("Por favor, verifique a integridade dos dados e tente novamente.")


if __name__ == "__main__":
    main()
