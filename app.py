import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import re
from datetime import date
import io

# ==========================================
# CONFIGURAÇÃO E UX/UI MOBILE-FIRST
# ==========================================
st.set_page_config(page_title="Diviapp Pro", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Layout Mobile-First */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 800px; /* Mantém o layout contido estilo App mesmo no Desktop */
        margin: 0 auto;
    }

    /* Ocultar barra superior padrão do Streamlit para parecer mais um App */
    header {visibility: hidden;}
    
    /* Cards de Resumo e Alertas */
    .app-card {
        background: var(--secondary-background-color);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border: 1px solid var(--background-color);
    }
    .app-card h4 { margin: 0; font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .app-card h2 { margin: 5px 0 0 0; font-size: 1.8rem; font-weight: 800; color: var(--text-color); }
    .app-card p { margin: 5px 0 0 0; font-size: 0.85rem; color: #10B981; font-weight: 600; }
    
    /* Cards de Alerta */
    .alert-card {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .alert-card.warning { background: rgba(245, 158, 11, 0.1); border-left-color: #F59E0B; }
    .alert-info { display: flex; flex-direction: column; }
    .alert-title { font-weight: 700; font-size: 0.95rem; }
    .alert-sub { font-size: 0.75rem; opacity: 0.8; }
    .alert-val { font-weight: 800; font-size: 1.1rem; }

    /* Botão Flutuante (FAB) Estilizado via classes padrão */
    div[data-testid="stButton"] button {
        border-radius: 12px;
        font-weight: 700;
        height: 48px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES E FUNÇÕES BASE (Mantidas)
# ==========================================
DB_FILE = "diviapp_pro.db"
MESES_ABREV = {1: "/JAN", 2: "/FEV", 3: "/MAR", 4: "/ABR", 5: "/MAI", 6: "/JUN", 7: "/JUL", 8: "/AGO", 9: "/SET", 10: "/OUT", 11: "/NOV", 12: "/DEZ"}
EMOJI_MAP = {"moradia": "🏠", "mercado": "🛒", "energia": "⚡", "água": "💧", "casamento": "💍", "telefone": "📱", "transporte": "🚗", "saúde": "🩺", "lazer": "🍿", "compras": "🛍️", "cartão": "💳", "financiamento": "🏦", "carro": "🚙", "investimentos": "📈", "outros": "📦"}

def formatar_moeda(valor): return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def get_conn(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def aplicar_emoji(nome_cat):
    texto = str(nome_cat).strip()
    texto_limpo = re.sub(r'^[^\w\sÀ-ÿ]+\s*', '', texto).strip() or "Outros"
    for k, emj in EMOJI_MAP.items():
        if k in texto_limpo.lower(): return f"{emj} {texto_limpo}"
    return f"🏷️ {texto_limpo}"

# A inicialização do banco de dados (Tabelas e Seed) continua idêntica e omitida aqui para não estourar limite, 
# MAS você mantém sua função inicializar_banco() exatamente como era.
def inicializar_banco():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY AUTOINCREMENT, aba_dono TEXT, descricao TEXT, categoria TEXT, valor REAL, vencimento TEXT, status TEXT, forma_pagamento TEXT, responsavel TEXT, observacoes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS investimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, mes TEXT, pessoa TEXT, tipo_investimento TEXT, instituicao TEXT, valor_aplicado REAL, saldo_atual REAL, ganho_mes REAL, rentabilidade REAL, observacoes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS parametros (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, valor TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS ganhos (aba_dono TEXT PRIMARY KEY, ganho_mensal REAL)""")
    # Seed Básico caso vazio
    if c.execute("SELECT COUNT(*) FROM parametros").fetchone()[0] == 0:
        for v in ["Moradia", "Mercado", "Energia", "Outros"]: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('categoria', ?)", (aplicar_emoji(v),))
        for v in ["Pendente", "Pago", "Atrasado"]: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('status', ?)", (v,))
        for v in ["Pix", "Crédito", "Débito"]: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('forma_pagamento', ?)", (v,))
        c.execute("INSERT OR REPLACE INTO ganhos VALUES ('Henrique', 4000.0), ('Camila', 4000.0)")
    conn.commit()
    conn.close()

@st.cache_data(ttl=60)
def ler_dados():
    conn = get_conn()
    df_c = pd.read_sql_query("SELECT * FROM contas", conn)
    df_i = pd.read_sql_query("SELECT * FROM investimentos", conn)
    df_p = pd.read_sql_query("SELECT * FROM parametros ORDER BY id", conn)
    conn.close()
    if not df_c.empty:
        df_c["vencimento_dt"] = pd.to_datetime(df_c["vencimento"], errors="coerce")
        df_c["mes_ano"] = df_c["vencimento_dt"].dt.strftime("%Y-%m")
    return df_c, df_i, df_p

inicializar_banco()
df_c, df_i, df_p = ler_dados()
lista_categorias = df_p[df_p["tipo"] == "categoria"]["valor"].tolist()
lista_status = df_p[df_p["tipo"] == "status"]["valor"].tolist()
lista_formas = df_p[df_p["tipo"] == "forma_pagamento"]["valor"].tolist()

hoje = date.today()
mes_atual_str = hoje.strftime("%Y-%m")

# ==========================================
# DIÁLOGOS (MODAIS MOBILE-FIRST)
# ==========================================
@st.dialog("➕ Nova Despesa")
def modal_nova_despesa():
    dono = st.segmented_control("Titular", ["Henrique", "Camila"], default="Henrique", label_visibility="collapsed")
    desc = st.text_input("O que é? (Descrição)*")
    val = st.number_input("Valor (R$)*", min_value=0.0, format="%.2f")
    cat = st.selectbox("Categoria", lista_categorias)
    venc = st.date_input("Vencimento", value=hoje)
    stat = st.selectbox("Status", lista_status)
    forma = st.selectbox("Pagamento", lista_formas)
    
    if st.button("💾 Salvar Despesa", type="primary", use_container_width=True):
        if desc:
            conn = get_conn()
            conn.execute("""INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                         (dono, desc, cat, val, venc.strftime("%Y-%m-%d"), stat, forma, dono, ""))
            conn.commit()
            conn.close()
            ler_dados.clear()
            st.rerun()
        else:
            st.error("Preencha a descrição.")

@st.dialog("➕ Novo Investimento")
def modal_novo_investimento():
    tipo = st.text_input("Tipo (Ex: CDB, Tesouro)*")
    inst = st.text_input("Instituição (Ex: Nubank)*")
    ap = st.number_input("Valor Aplicado (R$)", min_value=0.0)
    sal = st.number_input("Saldo Atual (R$)", min_value=0.0)
    if st.button("💾 Adicionar Ativo", type="primary", use_container_width=True):
        if tipo and inst:
            conn = get_conn()
            conn.execute("""INSERT INTO investimentos (data, mes, pessoa, tipo_investimento, instituicao, valor_aplicado, saldo_atual, ganho_mes, rentabilidade)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                         (hoje.strftime("%Y-%m-%d"), mes_atual_str, "Casal", tipo, inst, ap, sal, sal-ap, ((sal-ap)/ap*100) if ap>0 else 0))
            conn.commit()
            conn.close()
            ler_dados.clear()
            st.rerun()

# ==========================================
# NAVEGAÇÃO PRINCIPAL (ESTILO APP)
# ==========================================
menu = st.sidebar.radio("Navegação", ["🏠 Início", "💸 Despesas", "📈 Carteira", "📊 Relatórios", "⚙️ Ajustes"])

# ==========================================
# 1. TELA INÍCIO (DASHBOARD)
# ==========================================
if menu == "🏠 Início":
    st.markdown("### 👋 Olá, Henrique & Camila!")
    
    # Filtro de Mês Rápido
    meses = sorted(df_c["mes_ano"].dropna().unique().tolist() + [mes_atual_str], reverse=True)
    mes_sel = st.selectbox("Mês de Referência", meses, index=0, label_visibility="collapsed")
    
    df_mes = df_c[df_c["mes_ano"] == mes_sel] if not df_c.empty else df_c
    tot_pago = df_mes[df_mes["status"] == "Pago"]["valor"].sum()
    tot_pend = df_mes[df_mes["status"].isin(["Pendente", "Atrasado"])]["valor"].sum()
    
    # Cards Estilo App
    st.markdown(f"""
        <div class="app-card">
            <h4>Falta Pagar ({mes_sel})</h4>
            <h2>{formatar_moeda(tot_pend)}</h2>
            <p>✅ {formatar_moeda(tot_pago)} já foram pagos</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Alertas
    alertas = df_mes[df_mes["status"].isin(["Atrasado", "Pendente"])].sort_values("vencimento_dt").head(5)
    if not alertas.empty:
        st.markdown("#### 🔔 Próximos Vencimentos")
        for _, row in alertas.iterrows():
            classe = "warning" if row["status"] == "Pendente" else "danger"
            st.markdown(f"""
                <div class="alert-card {classe}">
                    <div class="alert-info">
                        <span class="alert-title">{row['descricao']} ({row['aba_dono'][:1]})</span>
                        <span class="alert-sub">Vence dia {row['vencimento_dt'].day:02d} • {row['categoria']}</span>
                    </div>
                    <span class="alert-val">{formatar_moeda(row['valor'])}</span>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# 2. TELA DESPESAS (UNIFICADA)
# ==========================================
elif menu == "💸 Despesas":
    st.title("💸 Gestão de Despesas")
    
    if st.button("➕ Adicionar Conta", type="primary", use_container_width=True):
        modal_nova_despesa()
        
    filtro_dono = st.segmented_control("Titular", ["Todos", "Henrique", "Camila"], default="Todos")
    
    df_show = df_c.copy()
    if filtro_dono != "Todos": df_show = df_show[df_show["aba_dono"] == filtro_dono]
    
    if not df_show.empty:
        df_show["vencimento_dt"] = df_show["vencimento_dt"].dt.date
        df_show["Excluir"] = False
        
        st.markdown("#### 📋 Contas do Mês")
        # Configuração focada no celular (menos colunas, fácil edição)
        df_edit = st.data_editor(
            df_show[["id", "vencimento_dt", "descricao", "valor", "status", "aba_dono", "Excluir"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "id": None, # Esconde o ID
                "vencimento_dt": st.column_config.DateColumn("Data", format="DD/MM"),
                "descricao": "Descrição",
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "status": st.column_config.SelectboxColumn("Status", options=lista_status),
                "aba_dono": "Titular",
                "Excluir": st.column_config.CheckboxColumn("🗑️")
            }
        )
        
        if st.button("💾 Salvar Alterações da Tabela", use_container_width=True):
            conn = get_conn()
            for _, r in df_edit.iterrows():
                if r["Excluir"]:
                    conn.execute("DELETE FROM contas WHERE id = ?", (r["id"],))
                else:
                    conn.execute("UPDATE contas SET descricao=?, valor=?, status=? WHERE id=?", 
                                 (r["descricao"], float(r["valor"]), r["status"], r["id"]))
            conn.commit()
            conn.close()
            ler_dados.clear()
            st.rerun()

# ==========================================
# 3. TELA CARTEIRA (INVESTIMENTOS)
# ==========================================
elif menu == "📈 Carteira":
    st.title("📈 Carteira")
    
    tot_patrimonio = df_i["saldo_atual"].sum() if not df_i.empty else 0.0
    st.markdown(f"""
        <div class="app-card" style="border-left: 5px solid #10B981;">
            <h4>Patrimônio Total</h4>
            <h2>{formatar_moeda(tot_patrimonio)}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ Novo Aporte", type="primary", use_container_width=True):
        modal_novo_investimento()
        
    if not df_i.empty:
        st.markdown("#### 🏦 Meus Ativos")
        # Grafico Donut
        fig = px.pie(df_i, values='saldo_atual', names='instituicao', hole=0.6)
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Grid simplificado
        st.dataframe(df_i[["instituicao", "tipo_investimento", "saldo_atual"]], hide_index=True, use_container_width=True)

# ==========================================
# 4. TELA RELATÓRIOS
# ==========================================
elif menu == "📊 Relatórios":
    st.title("📊 Análises")
    if not df_c.empty:
        st.markdown("#### Despesas por Categoria (Global)")
        df_cat = df_c.groupby("categoria", as_index=False)["valor"].sum().sort_values("valor")
        fig_cat = px.bar(df_cat, x="valor", y="categoria", orientation="h", text_auto=".2s")
        fig_cat.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("#### Evolução Mensal")
        df_ev = df_c.groupby(["mes_ano"], as_index=False)["valor"].sum()
        fig_ev = px.line(df_ev, x="mes_ano", y="valor", markers=True)
        fig_ev.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_ev, use_container_width=True)
    else:
        st.info("Sem dados suficientes para gráficos.")

# ==========================================
# 5. TELA AJUSTES
# ==========================================
elif menu == "⚙️ Ajustes":
    st.title("⚙️ Configurações")
    
    with st.expander("🏷️ Gerenciar Categorias"):
        nova_cat = st.text_input("Nova Categoria")
        if st.button("Adicionar Categoria"):
            conn = get_conn()
            conn.execute("INSERT INTO parametros (tipo, valor) VALUES ('categoria', ?)", (aplicar_emoji(nova_cat),))
            conn.commit(); conn.close(); ler_dados.clear(); st.rerun()
            
    with st.expander("💾 Backup e Exportação"):
        if st.button("Gerar Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_c.to_excel(writer, sheet_name="Todas Contas", index=False)
                df_i.to_excel(writer, sheet_name="Investimentos", index=False)
            st.download_button("📥 Descarregar XLSX", output.getvalue(), file_name=f"Backup_{date.today()}.xlsx", use_container_width=True)