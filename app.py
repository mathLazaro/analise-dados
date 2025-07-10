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
        
        # Seção 1: Pergunta 1 - Setores que mais degradam
        st.header("1. 🏭 Setores Econômicos que Mais Degradam o Meio Ambiente")
        st.markdown("""
        **Análise:** Com base nos dados de emissões do SEEG, identificamos os setores com maior impacto ambiental.
        O gráfico treemap mostra a proporção de emissões por setor econômico.
        """)
        
        # Controle específico para emissões
        anos_emissoes = sorted(emissoes_long['Ano'].unique())
        col1_control, col2_control, col3_control = st.columns([1, 1, 2])
        with col1_control:
            selected_year_emissoes = st.selectbox(
                "📅 Selecione o ano para análise:",
                anos_emissoes,
                index=len(anos_emissoes)-1,
                key="year_emissoes"
            )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            treemap_fig = create_treemap_setores_degradacao(emissoes_long, selected_year_emissoes)
            st.plotly_chart(treemap_fig, use_container_width=True)
        
        with col2:
            # KPIs de emissões
            year_emissions = emissoes_long[emissoes_long['Ano'] == selected_year_emissoes]
            total_emissions = year_emissions['Emissoes'].sum()
            
            st.metric("Total de Emissões", f"{total_emissions/1e9:.1f}B ton CO²eq")
            
            # Setor com maior emissão
            top_setor = year_emissions.loc[year_emissions['Emissoes'].idxmax(), 'Categoria']
            top_emission = year_emissions['Emissoes'].max()
            
            st.metric(
                "Maior Emissor", 
                top_setor.split()[0] + "...",
                f"{(top_emission/total_emissions)*100:.1f}% do total"
            )
        
        st.markdown("---")
        
        # Seção 2: Pergunta 2 - Relação entre setores e intensidade
        st.header("2. 📊 Relação entre Tipos de Setores e Intensidade de Degradação")
        st.markdown("""
        **Análise Expandida:** Comparamos **todos os setores industriais** disponíveis correlacionando:
        - **Desempenho Econômico** (receita, empresas, valor de transformação)
        - **Impacto Ambiental** (emissões por setor correspondente)
        - **Eficiência Ambiental** (receita gerada por unidade de emissão)
        """)
        
        # Controles específicos para análise industrial
        anos_industria = sorted(industria_data['Ano'].unique())
        col1_ind, col2_ind, col3_ind = st.columns([2, 1, 1])
        with col1_ind:
            selected_years_industria = st.multiselect(
                "📅 Selecione os anos para análise industrial:",
                anos_industria,
                default=anos_industria[-3:],
                key="years_industria"
            )
        
        with col2_ind:
            st.markdown("**Setores Analisados:**")
            st.info("4 setores industriais principais")
        
        with col3_ind:
            st.markdown("**Correlação:**")
            st.info("Dados industriais + emissões")
        
        if selected_years_industria:
            barras_fig = create_barras_agrupadas_eficiencia_ambiental(industria_data, emissoes_long, selected_years_industria)
            st.plotly_chart(barras_fig, use_container_width=True)
            
            # Insights adicionais sobre correlações
            st.markdown("### 🔍 Insights da Análise Multidimensional")
            
            col1_insight, col2_insight = st.columns(2)
            
            with col1_insight:
                st.markdown("""
                **🏭 Setores Industriais:**
                - **Petróleo/Gás**: Alta receita, maior impacto energético
                - **Mineração**: Receita concentrada, impacto em processos industriais  
                - **Metalurgia**: Transformação intensiva, emissões significativas
                - **Carvão**: Menor escala, alto impacto por unidade
                """)
            
            with col2_insight:
                st.markdown("""
                **🌱 Correlações Ambientais:**
                - **Energia**: Responsável por emissões diretas de combustão
                - **Processos Industriais**: Emissões de transformação química
                - **Eficiência**: Varia drasticamente entre setores
                - **Sustentabilidade**: Inversamente proporcional às emissões
                """)
        else:
            st.warning("⚠️ Selecione pelo menos um ano para análise industrial.")
        
        st.markdown("---")
        
        # Seção 3: Pergunta 3 - KPI de Eficiência Ambiental
        st.header("3. 💡 Eficiência Ambiental: Produção vs Impacto")
        st.markdown("""
        **KPI de Eficiência Ambiental:** Receita Total ÷ Emissões do Setor
        
        Setores com maior eficiência conseguem gerar mais valor econômico com menor impacto ambiental.
        """)
        
        # Calcular KPI de eficiência (usando os anos já selecionados na seção anterior)
        if selected_years_industria:
            industry_subset = industria_data[industria_data['Ano'].isin(selected_years_industria)]
            emissions_subset = emissoes_long[emissoes_long['Ano'].isin(selected_years_industria)]
            
            # Criar KPI por ano
            kpi_data = []
            for year in selected_years_industria:
                year_industry = industry_subset[industry_subset['Ano'] == year]
                year_emissions = emissions_subset[emissions_subset['Ano'] == year]
                
                total_receita = year_industry['Receita - total (Mil Reais)'].sum()
                total_emissoes = year_emissions['Emissoes'].sum()
                
                if total_emissoes > 0:
                    eficiencia = total_receita / (total_emissoes / 1e6)  # Ajustar escala
                    kpi_data.append({'Ano': year, 'Eficiência': eficiencia})
            
            if kpi_data:
                kpi_df = pd.DataFrame(kpi_data)
                
                fig_kpi = px.line(
                    kpi_df, 
                    x='Ano', 
                    y='Eficiência',
                    title="Evolução da Eficiência Ambiental (Receita/Emissões)",
                    markers=True
                )
                fig_kpi.update_layout(height=400)
                st.plotly_chart(fig_kpi, use_container_width=True)
        else:
            st.info("💡 Selecione anos na seção anterior para visualizar a eficiência ambiental.")
        
        st.markdown("---")
        
        # Seção 4: Pergunta 4 - Fatores de irresponsabilidade ambiental
        st.header("4. ⚠️ Fatores Relacionados à Falta de Responsabilidade Ambiental")
        st.markdown("""
        **Análise:** O heatmap mostra a intensidade do desmatamento por estado ao longo do tempo.
        Estados com colorações mais intensas apresentam maior risco ambiental.
        """)
        
        # Controles específicos para desmatamento
        anos_desmat = sorted(prodes_data['Ano/Estados'].unique())
        col1_desmat, col2_desmat, col3_desmat = st.columns(3)
        
        with col1_desmat:
            start_year_desmat = st.selectbox(
                "📅 Ano inicial:",
                anos_desmat,
                index=len(anos_desmat)-10,
                key="start_year_desmat"
            )
        
        with col2_desmat:
            end_year_desmat = st.selectbox(
                "📅 Ano final:",
                anos_desmat,
                index=len(anos_desmat)-1,
                key="end_year_desmat"
            )
        
        with col3_desmat:
            st.markdown("**Período selecionado:**")
            st.info(f"{end_year_desmat - start_year_desmat + 1} anos de análise")
        
        heatmap_fig = create_heatmap_desmatamento_regional(prodes_data, start_year_desmat, end_year_desmat)
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # Insights sobre fatores de risco
        col1, col2, col3 = st.columns(3)
        
        recent_data = prodes_data[prodes_data['Ano/Estados'] == prodes_data['Ano/Estados'].max()]
        
        with col1:
            max_desmat_estado = recent_data.drop('AMZ LEGAL', axis=1).iloc[0, 1:].idxmax()
            max_desmat_valor = recent_data[max_desmat_estado].iloc[0]
            st.metric("Estado com Maior Desmatamento", max_desmat_estado, f"{max_desmat_valor:,.0f} km²")
        
        with col2:
            total_amz = recent_data['AMZ LEGAL'].iloc[0]
            st.metric("Total Amazônia Legal", f"{total_amz:,.0f} km²", "Ano mais recente")
        
        with col3:
            # Variação recente
            if len(prodes_data) >= 2:
                var_recente = ((recent_data['AMZ LEGAL'].iloc[0] / 
                              prodes_data[prodes_data['Ano/Estados'] == prodes_data['Ano/Estados'].max()-1]['AMZ LEGAL'].iloc[0]) - 1) * 100
                st.metric("Variação Anual", f"{var_recente:+.1f}%", "vs ano anterior")
        
        st.markdown("---")
        
        # Seção 5: Pergunta 5 - Agricultura familiar e sustentabilidade
        st.header("5. 🌱 Agricultura Familiar e Sustentabilidade")
        st.markdown("""
        **Análise:** A distribuição da agricultura familiar por região mostra que estabelecimentos menores
        tendem a ter menor impacto ambiental per capita.
        """)
        
        # Controles específicos para agricultura
        col1_ag, col2_ag, col3_ag = st.columns(3)
        
        with col1_ag:
            tipo_visualizacao = st.selectbox(
                "📊 Tipo de visualização:",
                ["Distribuição por Região", "Comparação Familiar vs Não Familiar"],
                key="tipo_viz_ag"
            )
        
        with col2_ag:
            ano_agricultura = st.selectbox(
                "📅 Ano de referência:",
                [2017, 2006],
                index=0,
                key="ano_agricultura"
            )
        
        if tipo_visualizacao == "Distribuição por Região":
            violin_fig = create_violin_agricultura_familiar(combined_ag)
            st.plotly_chart(violin_fig, use_container_width=True)
        
        # Comparação agricultura familiar vs não familiar
        st.subheader(f"Comparação: Agricultura Familiar vs Não Familiar ({ano_agricultura})")
        
        # Selecionar dados do ano escolhido
        ag_selected = ag_2017 if ano_agricultura == 2017 else ag_2006
        
        col1, col2 = st.columns(2)
        
        with col1:
            familiar_selected = ag_selected[ag_selected['Tipo'] == 'Agricultura familiar']
            
            # Sunburst da agricultura familiar
            familiar_brasil = familiar_selected[familiar_selected['Região'] == 'Brasil']
            if not familiar_brasil.empty:
                areas = ['Menos de 2ha', 'De 2ha a 5ha', 'De 5ha a 10ha', 'De 10 a 20 ha', 
                        'De 20 a 50 ha', 'De 50 a 100 ha', 'Mais que 100ha']
                valores_familiar = [familiar_brasil[area].iloc[0] for area in areas if area in familiar_brasil.columns]
                
                fig_sunburst = go.Figure(go.Sunburst(
                    labels=areas[:len(valores_familiar)],
                    values=valores_familiar
                ))
                fig_sunburst.update_layout(
                    title=f"Distribuição Agricultura Familiar por Tamanho ({ano_agricultura})",
                    height=400
                )
                st.plotly_chart(fig_sunburst, use_container_width=True)
        
        with col2:
            # Métricas comparativas
            total_familiar = ag_selected[ag_selected['Tipo'] == 'Agricultura familiar']['Total'].sum()
            total_nao_familiar = ag_selected[ag_selected['Tipo'] == 'Agricultura não familiar']['Total'].sum()
            
            st.metric("Total Agricultura Familiar", f"{total_familiar:,.0f}", "estabelecimentos")
            st.metric("Total Agricultura Não Familiar", f"{total_nao_familiar:,.0f}", "estabelecimentos")
            
            prop_familiar = (total_familiar / (total_familiar + total_nao_familiar)) * 100
            st.metric("% Agricultura Familiar", f"{prop_familiar:.1f}%", "do total")
        
        st.markdown("---")
        
        # Conclusões e insights
        st.header("📈 Indicadores e Conclusões")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Principais Insights")
            st.markdown("""
            - **Mudança de Uso da Terra** é o maior emissor de GEE
            - **Agricultura familiar** representa a maioria dos estabelecimentos
            - **Estados da Amazônia** concentram maior desmatamento
            - **Eficiência ambiental** varia significativamente entre setores
            """)
        
        with col2:
            st.subheader("📊 Recomendações")
            st.markdown("""
            - Foco em **tecnologias sustentáveis** para grandes propriedades
            - **Incentivos** para agricultura familiar
            - **Monitoramento intensivo** em estados críticos
            - **Políticas setoriais** diferenciadas por impacto
            """)
        
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Verifique se todos os arquivos estão na pasta 'tratado' conforme esperado.")
    
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.info("Por favor, verifique a integridade dos dados e tente novamente.")

if __name__ == "__main__":
    main() 