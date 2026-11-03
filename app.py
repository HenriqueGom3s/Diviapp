import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, date

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(page_title="Diviapp - Financeiro", page_icon="💰", layout="wide")

# ================================
# CONEXÃO COM SUPABASE
# ================================
# O Streamlit busca as credenciais no painel de Secrets (configurado na nuvem)
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# ================================
# FUNÇÕES DE BANCO DE DADOS
# ================================
def buscar_contas():
    resposta = supabase.table("contas").select("*").execute()
    if resposta.data:
        df = pd.DataFrame(resposta.data)
        df['vencimento'] = pd.to_datetime(df['vencimento']).dt.date
        return df
    return pd.DataFrame()

def adicionar_conta(desc, cat, valor, venc, status, forma, resp):
    nova_conta = {
        "descricao": desc, "categoria": cat, "valor": float(valor),
        "vencimento": str(venc), "status": status, 
        "forma_pagamento": forma, "responsavel": resp
    }
    
    # Regra: Se a conta é do casal, divide o valor e cria dois registros
    if resp == 'Casal':
        conta_h = nova_conta.copy()
        conta_c = nova_conta.copy()
        conta_h['valor'] = float(valor) / 2
        conta_h['responsavel'] = 'Henrique'
        conta_c['valor'] = float(valor) / 2
        conta_c['responsavel'] = 'Camila'
        supabase.table("contas").insert([conta_h, conta_c]).execute()
    else:
        supabase.table("contas").insert(nova_conta).execute()

# ================================
# INTERFACE DO APLICATIVO
# ================================
st.sidebar.title("Diviapp 💍")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação", ["🏠 Dashboard", "👨 Contas Henrique", "👩 Contas Camila"])

df_contas = buscar_contas()

categorias = ['Moradia', 'Mercado', 'Energia', 'Água', 'Casamento', 'Telefone', 'Transporte', 'Saúde', 'Lazer', 'Compras pessoais', 'Cartão de crédito']
status_list = ['Pendente', 'Pago', 'Atrasado']
formas_pagamento = ['Pix', 'Débito', 'Crédito', 'Boleto', 'Dinheiro']
responsaveis = ['Henrique', 'Camila', 'Casal']

def formata_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

if menu == "🏠 Dashboard":
    st.header("🏠 Dashboard do Casal")
    
    if not df_contas.empty:
        df_contas['mes_ano'] = pd.to_datetime(df_contas['vencimento']).dt.strftime('%Y-%m')
        meses = sorted(df_contas['mes_ano'].unique(), reverse=True)
        mes_dash = st.selectbox("Mês de Referência", meses)
        
        df_mes = df_contas[df_contas['mes_ano'] == mes_dash]
        saida_total = df_mes['valor'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Total de Saída do Mês", formata_moeda(saida_total))
        
        st.markdown("### Gastos por Categoria")
        resumo_cat = df_mes.groupby('categoria')['valor'].sum().reset_index()
        st.bar_chart(resumo_cat.set_index('categoria'))
    else:
        st.info("Nenhuma conta registrada no banco de dados ainda.")

elif menu in ["👨 Contas Henrique", "👩 Contas Camila"]:
    nome = "Henrique" if "Henrique" in menu else "Camila"
    st.header(f"Contas Mensais - {nome}")
    
    with st.expander("➕ Adicionar Nova Conta"):
        with st.form(f"form_{nome}", clear_on_submit=True):
            c1, c2 = st.columns(2)
            desc = c1.text_input("Descrição")
            cat = c2.selectbox("Categoria", categorias)
            
            c3, c4 = st.columns(2)
            val = c3.number_input("Valor (R$)", min_value=0.0, step=10.0)
            venc = c4.date_input("Vencimento")
            
            c5, c6, c7 = st.columns(3)
            status = c5.selectbox("Status", status_list)
            forma = c6.selectbox("Forma de Pagamento", formas_pagamento)
            resp = c7.selectbox("Responsável", responsaveis, index=responsaveis.index(nome) if nome in responsaveis else 0)
            
            if st.form_submit_button("Adicionar"):
                adicionar_conta(desc, cat, val, venc, status, forma, resp)
                st.success("Conta adicionada com sucesso no Supabase!")
                st.rerun() # Recarrega a página para puxar os novos dados

    st.markdown(f"### Histórico de {nome}")
    if not df_contas.empty:
        df_pessoa = df_contas[df_contas['responsavel'] == nome].drop(columns=['id', 'criado_em'], errors='ignore')
        st.dataframe(df_pessoa, use_container_width=True, hide_index=True)