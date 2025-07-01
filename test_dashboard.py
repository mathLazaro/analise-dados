#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do dashboard atualizado.
Executa verificações básicas de funcionalidade e compatibilidade.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando dependências...")
    
    try:
        import streamlit
        import plotly
        import seaborn
        import matplotlib
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def test_data_structure():
    """Verifica se a estrutura de dados esperada existe"""
    print("\n📁 Verificando estrutura de dados...")
    
    required_files = [
        'tratado/dados agricultura/dados-agricultura-2017.csv',
        'tratado/dados agricultura/dados-agricultura-2006.csv',
        'tratado/desmatamento/taxa_prodes_1988_2024-tratado.csv',
        'tratado/desmatamento/seeg/emissões_brutas.csv',
        'tratado/desmatamento/seeg/emissões_liquidas.csv',
        'tratado/dados industria/dados-industriais.csv'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} arquivos faltando:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print(f"\n✅ Todos os {len(existing_files)} arquivos necessários encontrados")
        return True

def test_data_loading():
    """Testa se os dados podem ser carregados corretamente"""
    print("\n📊 Testando carregamento de dados...")
    
    try:
        # Importar funções do dashboard
        sys.path.append('.')
        from dashboard_ambiental import (
            load_agricultura_data, 
            load_desmatamento_data, 
            load_emissoes_data, 
            load_industria_data
        )
        
        # Tentar carregar cada dataset
        print("   📋 Carregando dados de agricultura...")
        ag_2017, ag_2006 = load_agricultura_data()
        print(f"      - Agricultura 2017: {ag_2017.shape}")
        print(f"      - Agricultura 2006: {ag_2006.shape}")
        
        print("   🌳 Carregando dados de desmatamento...")
        prodes = load_desmatamento_data()
        print(f"      - PRODES: {prodes.shape}")
        
        print("   💨 Carregando dados de emissões...")
        emissoes_brutas, emissoes_liquidas = load_emissoes_data()
        print(f"      - Emissões brutas: {emissoes_brutas.shape}")
        print(f"      - Emissões líquidas: {emissoes_liquidas.shape}")
        
        print("   🏭 Carregando dados industriais...")
        industria = load_industria_data()
        print(f"      - Indústria: {industria.shape}")
        
        print("✅ Todos os dados carregados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        return False

def test_kpi_calculation():
    """Testa se o cálculo dos KPIs funciona corretamente"""
    print("\n📈 Testando cálculo de KPIs...")
    
    try:
        sys.path.append('.')
        from dashboard_ambiental import (
            load_agricultura_data, 
            load_desmatamento_data, 
            load_emissoes_data, 
            load_industria_data,
            process_emissoes_data,
            calculate_environmental_kpis
        )
        
        # Carregar dados necessários
        ag_2017, ag_2006 = load_agricultura_data()
        prodes = load_desmatamento_data()
        emissoes_brutas, emissoes_liquidas = load_emissoes_data()
        industria = load_industria_data()
        
        # Processar emissões
        emissoes_long = process_emissoes_data(emissoes_brutas)
        
        # Pegar anos disponíveis (interseção)
        anos_disponiveis = sorted(set(emissoes_long['Ano'].unique()) & set(industria['Ano'].unique()))
        if len(anos_disponiveis) >= 2:
            anos_teste = anos_disponiveis[-2:]
        else:
            anos_teste = anos_disponiveis
        
        print(f"   📅 Testando com anos: {anos_teste}")
        
        # Calcular KPIs
        kpi_data = calculate_environmental_kpis(industria, emissoes_long, prodes, anos_teste)
        
        if not kpi_data.empty:
            print(f"   ✅ KPIs calculados para {len(kpi_data)} anos")
            print(f"   📊 Colunas: {list(kpi_data.columns)}")
            
            # Verificar se KPI principal está sendo calculado
            if 'KPI_Principal' in kpi_data.columns:
                print(f"   🎯 KPI Principal médio: {kpi_data['KPI_Principal'].mean():.2f}")
                return True
            else:
                print("   ❌ KPI Principal não encontrado")
                return False
        else:
            print("   ❌ Nenhum KPI calculado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no cálculo de KPIs: {e}")
        return False

def test_visualizations():
    """Testa se as funções de visualização funcionam"""
    print("\n📊 Testando criação de visualizações...")
    
    try:
        sys.path.append('.')
        from dashboard_ambiental import (
            create_scatter_impacto_produtividade,
            create_ranking_setores_degradacao,
            create_treemap_setores_degradacao,
            process_emissoes_data,
            load_emissoes_data
        )
        
        # Carregar dados para teste
        emissoes_brutas, _ = load_emissoes_data()
        emissoes_long = process_emissoes_data(emissoes_brutas)
        
        # Testar treemap
        anos_emissoes = sorted(emissoes_long['Ano'].unique())
        if anos_emissoes:
            print("   📊 Testando Treemap...")
            treemap_fig = create_treemap_setores_degradacao(emissoes_long, anos_emissoes[-1])
            print("   ✅ Treemap criado")
            
            print("   📊 Testando Ranking...")
            ranking_fig = create_ranking_setores_degradacao(emissoes_long, anos_emissoes[-1])
            print("   ✅ Ranking criado")
            
            return True
        else:
            print("   ❌ Não há anos disponíveis para teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro na criação de visualizações: {e}")
        return False

def test_dashboard_import():
    """Testa se o dashboard pode ser importado sem erros"""
    print("\n🌍 Testando importação do dashboard...")
    
    try:
        import dashboard_ambiental
        print("✅ Dashboard importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def generate_test_report():
    """Gera relatório completo de testes"""
    print("=" * 60)
    print("🧪 RELATÓRIO DE TESTES - DASHBOARD AMBIENTAL")
    print("=" * 60)
    
    tests = [
        ("Dependências", test_dependencies),
        ("Estrutura de Dados", test_data_structure),
        ("Carregamento de Dados", test_data_loading),
        ("Cálculo de KPIs", test_kpi_calculation),
        ("Visualizações", test_visualizations),
        ("Importação do Dashboard", test_dashboard_import),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Dashboard pronto para uso.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas acima.")
        return False

if __name__ == "__main__":
    success = generate_test_report()
    sys.exit(0 if success else 1) 