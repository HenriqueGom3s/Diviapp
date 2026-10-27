import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração inicial da página
st.set_page_config(page_title="Diviapp - Financeiro", page_icon="🌱", layout="wide")

# Estilo customizado (Cores da logo)
st.markdown("""
    <style>
    .main {background-color: #F8F9FA;}
    h1, h2, h3 {color: #1E2A4F;}
    </style>
    """, unsafe_allow_html=True)

# Função para carregar os dados
@st.cache_data
def carregar_dados(arquivo):
    # Lendo as abas pulando as linhas de cabeçalho estilizado do Excel (skiprows=6)
    df_henrique = pd.read_excel(arquivo, sheet_name="Contas do Mês Henrique", skiprows=6)
    df_camila = pd.read_excel(arquivo, sheet_name="Contas do Mês Camila", skiprows=6)
    df_investimentos = pd.read_excel(arquivo, sheet_name="Investimentos")
    
    # Limpando linhas completamente vazias
    df_henrique = df_henrique.dropna(subset=['Descrição', 'Valor'], how='all')
    df_camila = df_camila.dropna(subset=['Descrição', 'Valor'], how='all')
    
    # Adicionando coluna para identificar a pessoa no Dashboard Unificado
    df_henrique['Dono da Conta'] = 'Henrique'
    df_camila['Dono da Conta'] = 'Camila'
    
    return df_henrique, df_camila, df_investimentos

# Barra lateral (Sidebar)
st.sidebar.image("logo.jpg", use_column_width=True) # Nome da sua logo
st.sidebar.title("🌱 Diviapp")
st.sidebar.markdown("Organização financeira do casal.")

# Carregamento do arquivo
arquivo_padrao = "controle_financeiro - HENRIQUE E CAMILA_2.xlsx"
arquivo_upload = st.sidebar.file_uploader("Atualizar Planilha (Opcional)", type=["xlsx"])

arquivo_ativo = arquivo_upload if arquivo_upload is not None else (arquivo_padrao if os.path.exists(arquivo_padrao) else None)

if arquivo_ativo is None:
    st.warning("⚠️ Planilha não encontrada. Faça o upload do arquivo Excel na barra lateral.")
else:
    df_henrique, df_camila, df_investimentos = carregar_dados(arquivo_ativo)
    
    # Unindo os dados para o Dashboard do casal
    df_casal = pd.concat([df_henrique, df_camila], ignore_index=True)
    
    # Navegação
    menu = st.sidebar.radio("Navegação", ["📊 Dashboard do Casal", "🧔🏻 Contas Henrique", "👩🏻 Contas Camila", "📈 Investimentos"])
    
    # ---------------------------------------------------------
    # TELA 1: DASHBOARD
    # ---------------------------------------------------------
    if menu == "📊 Dashboard do Casal":
        st.title("Dashboard Financeiro")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        total_geral = df_casal['Valor'].sum()
        total_henrique = df_henrique['Valor'].sum()
        total_camila = df_camila['Valor'].sum()
        
        col1.metric("Despesas Totais", f"R$ {total_geral:,.2f}")
        col2.metric("Henrique", f"R$ {total_henrique:,.2f}")
        col3.metric("Camila", f"R$ {total_camila:,.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("Despesas por Categoria")
            df_cat = df_casal.groupby('Categoria')['Valor'].sum().reset_index()
            fig_cat = px.pie(df_cat, names='Categoria', values='Valor', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_graf2:
            st.subheader("Status de Pagamento")
            df_status = df_casal.groupby('Status')['Valor'].sum().reset_index()
            fig_status = px.bar(df_status, x='Status', y='Valor', color='Status', text_auto='.2s')
            st.plotly_chart(fig_status, use_container_width=True)

    # ---------------------------------------------------------
    # TELA 2 e 3: CONTAS (HENRIQUE E CAMILA)
    # ---------------------------------------------------------
    elif menu in ["🧔🏻 Contas Henrique", "👩🏻 Contas Camila"]:
        nome = "Henrique" if menu == "🧔🏻 Contas Henrique" else "Camila"
        df_atual = df_henrique if nome == "Henrique" else df_camila
        
        st.title(f"Contas do Mês - {nome}")
        
        # Filtro de Status
        status_selecionado = st.multiselect("Filtrar por Status", df_atual['Status'].dropna().unique(), default=df_atual['Status'].dropna().unique())
        df_filtrado = df_atual[df_atual['Status'].isin(status_selecionado)]
        
        st.dataframe(
            df_filtrado[['Descrição', 'Categoria', 'Valor', 'Vencimento', 'Status', 'Forma de pagamento']], 
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------------------
    # TELA 4: INVESTIMENTOS
    # ---------------------------------------------------------
    elif menu == "📈 Investimentos":
        st.title("Meus Investimentos")
        st.markdown("Acompanhamento de patrimônio e rentabilidade.")
        
        total_investido = df_investimentos['Saldo atual'].sum()
        st.metric("Patrimônio Total Acumulado", f"R$ {total_investido:,.2f}")
        
        st.dataframe(df_investimentos, use_container_width=True, hide_index=True)