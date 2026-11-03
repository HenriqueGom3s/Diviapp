import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(page_title="Diviapp - Financeiro", page_icon="💰", layout="wide")

# ================================
# CONEXÃO COM SUPABASE
# ================================
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# ================================
# LISTAS DE REFERÊNCIA
# ================================
categorias = ['Moradia', 'Mercado', 'Energia', 'Água', 'Casamento', 'Telefone', 'Transporte', 'Saúde', 'Lazer', 'Compras pessoais', 'Cartão de crédito', 'Financiamento', 'Carro', 'Outros']
status_list = ['Pendente', 'Pago', 'Atrasado', 'Cancelado']
formas_pagamento = ['Pix', 'Débito', 'Crédito', 'Boleto', 'Dinheiro', 'Transferência', 'Débito automático']
responsaveis = ['Henrique', 'Camila', 'Casal']

def formata_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

# ================================
# FUNÇÕES DE BANCO DE DADOS
# ================================
def buscar_dados(tabela):
    resposta = supabase.table(tabela).select("*").execute()
    return pd.DataFrame(resposta.data) if resposta.data else pd.DataFrame()

def adicionar_conta(desc, cat, valor, venc, status, forma, resp):
    nova_conta = {
        "descricao": desc, "categoria": cat, "valor": float(valor),
        "vencimento": str(venc), "status": status, "forma_pagamento": forma, "responsavel": resp
    }
    
    if resp == 'Casal':
        c_henrique = nova_conta.copy()
        c_camila = nova_conta.copy()
        c_henrique.update({"valor": float(valor) / 2, "responsavel": "Henrique"})
        c_camila.update({"valor": float(valor) / 2, "responsavel": "Camila"})
        supabase.table("contas").insert([c_henrique, c_camila]).execute()
    else:
        supabase.table("contas").insert(nova_conta).execute()

def salvar_ganho(mes, resp, valor):
    existe = supabase.table("ganhos").select("*").eq("mes", mes).eq("responsavel", resp).execute()
    if existe.data:
        supabase.table("ganhos").update({"valor": float(valor)}).eq("id", existe.data[0]['id']).execute()
    else:
        supabase.table("ganhos").insert({"mes": mes, "responsavel": resp, "valor": float(valor)}).execute()

def apagar_registro(tabela, id_registro):
    supabase.table(tabela).delete().eq("id", id_registro).execute()

# ================================
# CARREGAMENTO DE DADOS
# ================================
df_contas = buscar_dados("contas")
df_ganhos = buscar_dados("ganhos")
df_invest = buscar_dados("investimentos")

if not df_contas.empty:
    df_contas['vencimento'] = pd.to_datetime(df_contas['vencimento']).dt.date
    df_contas['mes_ano'] = pd.to_datetime(df_contas['vencimento']).dt.strftime('%Y-%m')
    meses_disp = sorted(df_contas['mes_ano'].unique(), reverse=True)
else:
    meses_disp = [datetime.now().strftime('%Y-%m')]

# ================================
# BARRA LATERAL (MENU)
# ================================
st.sidebar.title("Diviapp 💍")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação", ["🏠 Dashboard", "👨 Contas Henrique", "👩 Contas Camila", "📈 Investimentos"])

# ================================
# TELAS
# ================================
if menu == "🏠 Dashboard":
    st.header("🏠 Dashboard do Casal")
    mes_selecionado = st.selectbox("Mês de Referência", meses_disp)
    
    # Cálculos de Contas
    df_mes = df_contas[df_contas['mes_ano'] == mes_selecionado] if not df_contas.empty else pd.DataFrame()
    saida_total = df_mes['valor'].sum() if not df_mes.empty else 0.0
    
    # Cálculos de Ganhos
    ganho_h = df_ganhos[(df_ganhos['mes'] == mes_selecionado) & (df_ganhos['responsavel'] == 'Henrique')]['valor'].sum() if not df_ganhos.empty else 0.0
    ganho_c = df_ganhos[(df_ganhos['mes'] == mes_selecionado) & (df_ganhos['responsavel'] == 'Camila')]['valor'].sum() if not df_ganhos.empty else 0.0
    ganho_total = ganho_h + ganho_c
    
    # Cálculos de Investimentos
    if not df_invest.empty:
        df_invest['mes_ano'] = pd.to_datetime(df_invest['data']).dt.strftime('%Y-%m')
        inv_total = df_invest[df_invest['mes_ano'] == mes_selecionado]['valor_aplicado'].sum()
    else:
        inv_total = 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Entrada Total", formata_moeda(ganho_total))
    col2.metric("Saída Total", formata_moeda(saida_total))
    col3.metric("Total Investido", formata_moeda(inv_total))
    col4.metric("Sobra do Casal", formata_moeda(ganho_total - saida_total))
    
    st.markdown("### Gastos por Categoria")
    if not df_mes.empty:
        resumo_cat = df_mes.groupby('categoria')['valor'].sum().reset_index()
        st.bar_chart(resumo_cat.set_index('categoria'))
    else:
        st.info("Nenhuma conta para este mês.")

elif menu in ["👨 Contas Henrique", "👩 Contas Camila"]:
    nome = "Henrique" if "Henrique" in menu else "Camila"
    st.header(f"Contas Mensais - {nome}")
    
    mes_selecionado = st.selectbox("Selecione o Mês", meses_disp, key=f"mes_{nome}")
    
    # Gerenciamento de Ganhos
    ganho_atual = df_ganhos[(df_ganhos['mes'] == mes_selecionado) & (df_ganhos['responsavel'] == nome)]['valor'].sum() if not df_ganhos.empty else 0.0
    
    col_g1, col_g2 = st.columns([3, 1])
    novo_ganho = col_g1.number_input(f"Ganho Mensal {nome} (R$)", value=float(ganho_atual), step=100.0)
    if col_g2.button("Salvar Ganho", use_container_width=True):
        salvar_ganho(mes_selecionado, nome, novo_ganho)
        st.success("Salvo!")
        st.rerun()

    # Cálculos da Pessoa
    df_pessoa = df_contas[(df_contas['mes_ano'] == mes_selecionado) & (df_contas['responsavel'] == nome)] if not df_contas.empty else pd.DataFrame()
    total_pagar = df_pessoa['valor'].sum() if not df_pessoa.empty else 0.0
    total_pendente = df_pessoa[df_pessoa['status'] != 'Pago']['valor'].sum() if not df_pessoa.empty else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total a Pagar", formata_moeda(total_pagar))
    col2.metric("Total Pendente", formata_moeda(total_pendente))
    col3.metric("Sobra", formata_moeda(novo_ganho - total_pagar))
    
    # Formulário de Adição
    with st.expander("➕ Adicionar Nova Conta"):
        with st.form(f"form_{nome}", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            desc = c1.text_input("Descrição")
            cat = c2.selectbox("Categoria", categorias)
            val = c3.number_input("Valor (R$)", min_value=0.0, step=10.0)
            
            c4, c5, c6, c7 = st.columns(4)
            venc = c4.date_input("Vencimento")
            status = c5.selectbox("Status", status_list)
            forma = c6.selectbox("Forma de Pagamento", formas_pagamento)
            resp = c7.selectbox("Responsável", responsaveis, index=responsaveis.index(nome))
            
            if st.form_submit_button("Adicionar"):
                adicionar_conta(desc, cat, val, venc, status, forma, resp)
                st.success("Conta adicionada!")
                st.rerun()

    st.markdown("### Histórico do Mês")
    if not df_pessoa.empty:
        df_exibir = df_pessoa[['id', 'descricao', 'categoria', 'valor', 'vencimento', 'status', 'forma_pagamento']]
        st.dataframe(df_exibir.drop(columns=['id']), use_container_width=True, hide_index=True)
        
        # Opção para deletar registro
        id_apagar = st.selectbox("Selecione uma conta para apagar (opcional):", df_exibir['id'].tolist(), format_func=lambda x: df_exibir[df_exibir['id'] == x]['descricao'].values[0])
        if st.button("🗑️ Apagar Conta Selecionada"):
            apagar_registro("contas", id_apagar)
            st.rerun()

elif menu == "📈 Investimentos":
    st.header("📈 Hub de Investimentos")
    
    with st.expander("➕ Adicionar Investimento"):
        with st.form("form_inv", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            data_inv = c1.date_input("Data Referência")
            resp_inv = c2.selectbox("Responsável", responsaveis)
            tipo_inv = c3.text_input("Tipo (CDB, Tesouro, Ações)")
            
            c4, c5, c6 = st.columns(3)
            inst_inv = c4.text_input("Instituição")
            val_inv = c5.number_input("Valor Aplicado (R$)", min_value=0.0, step=100.0)
            ganho_inv = c6.number_input("Ganho no Mês (R$)", step=10.0)
            
            if st.form_submit_button("Registrar Investimento"):
                novo_inv = {
                    'data': str(data_inv), 'responsavel': resp_inv, 'tipo_investimento': tipo_inv,
                    'instituicao': inst_inv, 'valor_aplicado': float(val_inv), 
                    'saldo_atual': float(val_inv + ganho_inv), 'ganho_mes': float(ganho_inv)
                }
                supabase.table("investimentos").insert(novo_inv).execute()
                st.success("Investimento registrado!")
                st.rerun()

    st.markdown("### Histórico de Investimentos")
    if not df_invest.empty:
        st.dataframe(df_invest.drop(columns=['id', 'criado_em'], errors='ignore'), use_container_width=True, hide_index=True)