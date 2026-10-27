import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from datetime import datetime, date, timedelta
import io

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILO
# ==========================================
st.set_page_config(page_title="Diviapp - Organização Financeira", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #F8FAFC;}
    h1, h2, h3 {color: #1E2A4F; font-weight: 700;}
    div[data-testid="stMetricValue"] {font-size: 1.6rem; color: #1E2A4F;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background-color: #E2E8F0;
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E2A4F !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "diviapp_dados.db"
EXCEL_PADRAO = "controle_financeiro - HENRIQUE E CAMILA_2.xlsx"
EXCEL_ALT = "controle_financeiro - HENRIQUE E CAMILA.xlsx"

# ==========================================
# BANCO DE DADOS E INICIALIZAÇÃO DA PLANILHA
# ==========================================
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def inicializar_banco():
    conn = get_conn()
    c = conn.cursor()
    
    # Tabela de Contas (Henrique e Camila)
    c.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aba_dono TEXT,
            descricao TEXT,
            categoria TEXT,
            valor REAL,
            vencimento TEXT,
            status TEXT,
            forma_pagamento TEXT,
            responsavel TEXT,
            observacoes TEXT
        )
    """)
    
    # Tabela de Investimentos
    c.execute("""
        CREATE TABLE IF NOT EXISTS investimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            mes TEXT,
            pessoa TEXT,
            tipo_investimento TEXT,
            instituicao TEXT,
            valor_aplicado REAL,
            saldo_atual REAL,
            ganho_mes REAL,
            rentabilidade REAL,
            observacoes TEXT
        )
    """)
    
    # Tabela de Parâmetros (Categorias, Status, Formas de Pagamento)
    c.execute("""
        CREATE TABLE IF NOT EXISTS parametros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            valor TEXT
        )
    """)
    
    # Tabela de Ganhos Mensais (Salário/Renda do mês base)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ganhos (
            aba_dono TEXT PRIMARY KEY,
            ganho_mensal REAL
        )
    """)
    conn.commit()

    # Se o banco estiver vazio, importa os dados iniciais da planilha Excel
    c.execute("SELECT COUNT(*) FROM parametros")
    if c.fetchone()[0] == 0:
        importar_dados_iniciais(conn)
    conn.close()

def importar_dados_iniciais(conn):
    arquivo = EXCEL_PADRAO if os.path.exists(EXCEL_PADRAO) else (EXCEL_ALT if os.path.exists(EXCEL_ALT) else None)
    c = conn.cursor()
    
    # Ganhos padrão da planilha (Henrique: 3985, Camila: 2860)
    c.execute("INSERT OR REPLACE INTO ganhos (aba_dono, ganho_mensal) VALUES ('Henrique', 3985.0), ('Camila', 2860.0)")
    
    if arquivo:
        try:
            xls = pd.ExcelFile(arquivo)
            
            # 1. Importar Categorias, Status e Formas de Pagamento
            if "Categorias" in xls.sheet_names:
                df_cat = pd.read_excel(xls, sheet_name="Categorias")
                for col, tipo in [("Categorias", "categoria"), ("Status", "status"), ("Formas de pagamento", "forma_pagamento")]:
                    if col in df_cat.columns:
                        for val in df_cat[col].dropna().unique():
                            val_str = str(val).strip()
                            if val_str:
                                c.execute("INSERT INTO parametros (tipo, valor) VALUES (?, ?)", (tipo, val_str))
            
            # 2. Importar Contas Henrique e Camila
            for aba, dono in [("Contas do Mês Henrique", "Henrique"), ("Contas do Mês Camila", "Camila")]:
                if aba in xls.sheet_names:
                    df_c = pd.read_excel(xls, sheet_name=aba, skiprows=6)
                    df_c = df_c.dropna(subset=["Descrição", "Valor"], how="all")
                    for _, row in df_c.iterrows():
                        venc = pd.to_datetime(row.get("Vencimento"), errors="coerce")
                        venc_str = venc.strftime("%Y-%m-%d") if pd.notnull(venc) else date.today().strftime("%Y-%m-%d")
                        obs = "" if pd.isna(row.get("Observações")) else str(row.get("Observações"))
                        c.execute("""
                            INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            dono,
                            str(row.get("Descrição", "")).strip(),
                            str(row.get("Categoria", "Outros")).strip(),
                            float(row.get("Valor", 0.0)) if pd.notnull(row.get("Valor")) else 0.0,
                            venc_str,
                            str(row.get("Status", "Pendente")).strip(),
                            str(row.get("Forma de pagamento", "Pix")).strip(),
                            str(row.get("Responsável", dono)).strip(),
                            obs
                        ))
            
            # 3. Importar Investimentos
            if "Investimentos" in xls.sheet_names:
                df_inv = pd.read_excel(xls, sheet_name="Investimentos")
                df_inv = df_inv.dropna(subset=["Tipo de investimento", "Valor aplicado", "Saldo atual"], how="all")
                for _, row in df_inv.iterrows():
                    dt = pd.to_datetime(row.get("Data"), errors="coerce")
                    dt_str = dt.strftime("%Y-%m-%d") if pd.notnull(dt) else date.today().strftime("%Y-%m-%d")
                    mes_str = dt.strftime("%Y-%m") if pd.notnull(dt) else date.today().strftime("%Y-%m")
                    v_aplic = float(row.get("Valor aplicado", 0.0)) if pd.notnull(row.get("Valor aplicado")) else 0.0
                    s_atual = float(row.get("Saldo atual", 0.0)) if pd.notnull(row.get("Saldo atual")) else 0.0
                    ganho = float(row.get("Ganho no mês", s_atual - v_aplic)) if pd.notnull(row.get("Ganho no mês")) else (s_atual - v_aplic)
                    rent = (ganho / v_aplic * 100) if v_aplic > 0 else 0.0
                    obs = "" if pd.isna(row.get("Observações")) else str(row.get("Observações"))
                    c.execute("""
                        INSERT INTO investimentos (data, mes, pessoa, tipo_investimento, instituicao, valor_aplicado, saldo_atual, ganho_mes, rentabilidade, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        dt_str, mes_str, str(row.get("Pessoa", "Casal")), str(row.get("Tipo de investimento", "")),
                        str(row.get("Instituição", "")), v_aplic, s_atual, ganho, rent, obs
                    ))
            conn.commit()
            return
        except Exception as e:
            st.error(f"Erro ao ler planilha inicial: {e}")

    # Fallback caso a planilha não esteja na pasta
    categorias_padrao = ["Moradia", "Mercado", "Energia", "Água", "Casamento", "Telefone", "Transporte", "Saúde", "Lazer", "Compras pessoais", "Cartão de crédito", "Financiamento", "Carro", "Investimentos", "Outros"]
    status_padrao = ["Pendente", "Pago", "Atrasado", "Cancelado"]
    formas_padrao = ["Pix", "Débito", "Crédito", "Boleto", "Dinheiro", "Transferência", "Débito automático"]
    for v in categorias_padrao: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('categoria', ?)", (v,))
    for v in status_padrao: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('status', ?)", (v,))
    for v in formas_padrao: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('forma_pagamento', ?)", (v,))
    conn.commit()

# ==========================================
# FUNÇÕES DE LEITURA E APOIO
# ==========================================
def carregar_parametros(tipo):
    conn = get_conn()
    df = pd.read_sql_query("SELECT id, valor FROM parametros WHERE tipo = ? ORDER BY id", conn, params=(tipo,))
    conn.close()
    return df["valor"].tolist(), df

def carregar_contas():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM contas", conn)
    conn.close()
    if not df.empty:
        df["vencimento_dt"] = pd.to_datetime(df["vencimento"], errors="coerce")
        df["mes_ano"] = df["vencimento_dt"].dt.strftime("%Y-%m")
    else:
        df["vencimento_dt"] = pd.Series(dtype="datetime64[ns]")
        df["mes_ano"] = pd.Series(dtype="str")
    return df

def carregar_investimentos():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM investimentos", conn)
    conn.close()
    if not df.empty:
        df["data_dt"] = pd.to_datetime(df["data"], errors="coerce")
    return df

def obter_ganho(dono):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT ganho_mensal FROM ganhos WHERE aba_dono = ?", (dono,))
    res = c.fetchone()
    conn.close()
    return float(res[0]) if res else 0.0

def atualizar_ganho(dono, valor):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO ganhos (aba_dono, ganho_mensal) VALUES (?, ?)", (dono, valor))
    conn.commit()
    conn.close()

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_excel_download():
    df_contas = carregar_contas()
    df_inv = carregar_investimentos()
    _, df_cat = carregar_parametros("categoria")
    _, df_stat = carregar_parametros("status")
    _, df_form = carregar_parametros("forma_pagamento")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_h = df_contas[df_contas["aba_dono"] == "Henrique"][["descricao", "categoria", "valor", "vencimento", "status", "forma_pagamento", "responsavel", "observacoes"]]
        df_h.columns = ["Descrição", "Categoria", "Valor", "Vencimento", "Status", "Forma de pagamento", "Responsável", "Observações"]
        df_h.to_excel(writer, sheet_name="Contas do Mês Henrique", index=False)
        
        df_c = df_contas[df_contas["aba_dono"] == "Camila"][["descricao", "categoria", "valor", "vencimento", "status", "forma_pagamento", "responsavel", "observacoes"]]
        df_c.columns = ["Descrição", "Categoria", "Valor", "Vencimento", "Status", "Forma de pagamento", "Responsável", "Observações"]
        df_c.to_excel(writer, sheet_name="Contas do Mês Camila", index=False)
        
        if not df_inv.empty:
            df_i = df_inv[["data", "mes", "pessoa", "tipo_investimento", "instituicao", "valor_aplicado", "saldo_atual", "ganho_mes", "rentabilidade", "observacoes"]]
            df_i.columns = ["Data", "Mês", "Pessoa", "Tipo de investimento", "Instituição", "Valor aplicado", "Saldo atual", "Ganho no mês", "Rentabilidade %", "Observações"]
        else:
            df_i = pd.DataFrame(columns=["Data", "Mês", "Pessoa", "Tipo de investimento", "Instituição", "Valor aplicado", "Saldo atual", "Ganho no mês", "Rentabilidade %", "Observações"])
        df_i.to_excel(writer, sheet_name="Investimentos", index=False)
        
        df_p = pd.DataFrame({
            "Categorias": pd.Series(df_cat["valor"].tolist()),
            "Status": pd.Series(df_stat["valor"].tolist()),
            "Formas de pagamento": pd.Series(df_form["valor"].tolist())
        })
        df_p.to_excel(writer, sheet_name="Categorias", index=False)
        
    return output.getvalue()

# Inicializa o banco na primeira execução
inicializar_banco()

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)
elif os.path.exists("input_file_0.png"):
    st.sidebar.image("input_file_0.png", use_container_width=True)
else:
    st.sidebar.title("🌱 Diviapp")

st.sidebar.markdown("**Gestão Financeira: Henrique & Camila**")

menu = st.sidebar.radio(
    "Menu Principal",
    [
        "📊 Dashboard do Casal",
        "📅 Resumo Mensal",
        "🧔🏻 Contas Henrique",
        "👩🏻 Contas Camila",
        "📈 Investimentos",
        "🏷️ Categorias & Opções"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup & Planilha")
st.sidebar.download_button(
    label="📥 Baixar Planilha Atualizada (.xlsx)",
    data=gerar_excel_download(),
    file_name=f"Diviapp_Henrique_Camila_{date.today().strftime('%Y_%m_%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

with st.sidebar.expander("🔄 Restaurar da Planilha Original"):
    st.caption("Apaga as edições atuais e recarrega os dados originais da planilha enviada.")
    if st.button("Recarregar Planilha Original", use_container_width=True):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        inicializar_banco()
        st.rerun()

# Carregamento global de dados
df_contas = carregar_contas()
df_inv = carregar_investimentos()
lista_categorias, _ = carregar_parametros("categoria")
lista_status, _ = carregar_parametros("status")
lista_formas, _ = carregar_parametros("forma_pagamento")
responsaveis_opcoes = ["Casal", "Henrique", "Camila"]

# ==========================================
# 1. DASHBOARD DO CASAL
# ==========================================
if menu == "📊 Dashboard do Casal":
    st.title("📊 Dashboard Financeiro do Casal")
    
    # Barra de Filtros Inteligente (Mês, Múltiplos Meses ou Período de Datas)
    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns([1.2, 2, 1.2])
        with col_f1:
            modo_filtro = st.radio(
                "Modo de Visualização:",
                ["Por Mês(es)", "Por Período (Datas)", "Todo o Histórico"],
                horizontal=False
            )
        
        meses_disponiveis = sorted(df_contas["mes_ano"].dropna().unique().tolist())
        if not meses_disponiveis:
            meses_disponiveis = [date.today().strftime("%Y-%m")]
            
        with col_f2:
            if modo_filtro == "Por Mês(es)":
                padrao_mes = ["2026-11"] if "2026-11" in meses_disponiveis else [meses_disponiveis[-1]]
                meses_sel = st.multiselect("Selecione o(s) Mês(es) de Referência:", meses_disponiveis, default=padrao_mes)
                df_dash = df_contas[df_contas["mes_ano"].isin(meses_sel)] if meses_sel else df_contas.iloc[0:0]
                df_inv_dash = df_inv[df_inv["mes"].isin(meses_sel)] if (not df_inv.empty and meses_sel) else df_inv
            elif modo_filtro == "Por Período (Datas)":
                min_dt = df_contas["vencimento_dt"].min().date() if not df_contas.empty else date(2026, 1, 1)
                max_dt = df_contas["vencimento_dt"].max().date() if not df_contas.empty else date(2026, 12, 31)
                intervalo = st.date_input("Selecione o Período Inicial e Final:", value=(min_dt, max_dt))
                if isinstance(intervalo, tuple) and len(intervalo) == 2:
                    dt_ini, dt_fim = intervalo
                    df_dash = df_contas[(df_contas["vencimento_dt"].dt.date >= dt_ini) & (df_contas["vencimento_dt"].dt.date <= dt_fim)]
                    df_inv_dash = df_inv[(df_inv["data_dt"].dt.date >= dt_ini) & (df_inv["data_dt"].dt.date <= dt_fim)] if not df_inv.empty else df_inv
                else:
                    df_dash = df_contas
                    df_inv_dash = df_inv
            else:
                st.info("Exibindo todo o histórico de lançamentos da planilha.")
                df_dash = df_contas
                df_inv_dash = df_inv

        with col_f3:
            filtro_dono = st.multiselect("Filtrar Aba/Pessoa:", ["Henrique", "Camila"], default=["Henrique", "Camila"])
            df_dash = df_dash[df_dash["aba_dono"].isin(filtro_dono)]
            filtro_resp = st.multiselect("Responsável:", responsaveis_opcoes, default=responsaveis_opcoes)
            df_dash = df_dash[df_dash["responsavel"].isin(filtro_resp)]

    # Cálculo de Indicadores Principais
    total_mes = df_dash["valor"].sum()
    total_henrique = df_dash[df_dash["aba_dono"] == "Henrique"]["valor"].sum()
    total_camila = df_dash[df_dash["aba_dono"] == "Camila"]["valor"].sum()
    total_pago = df_dash[df_dash["status"].str.lower() == "pago"]["valor"].sum()
    total_pendente = df_dash[df_dash["status"].str.lower() == "pendente"]["valor"].sum()
    total_atrasado = df_dash[df_dash["status"].str.lower() == "atrasado"]["valor"].sum()
    
    total_investido = df_inv_dash["saldo_atual"].sum() if not df_inv_dash.empty else 0.0
    ganho_inv = df_inv_dash["ganho_mes"].sum() if not df_inv_dash.empty else 0.0

    # Linha 1 de KPIs (Contas)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("💰 Total do Período", formatar_moeda(total_mes))
    k2.metric("🧔🏻 Total Henrique", formatar_moeda(total_henrique))
    k3.metric("👩🏻 Total Camila", formatar_moeda(total_camila))
    k4.metric("✅ Total Pago", formatar_moeda(total_pago))
    k5.metric("⏳ Total Pendente", formatar_moeda(total_pendente))
    k6.metric("🚨 Total Atrasado", formatar_moeda(total_atrasado))

    # Linha 2 de KPIs (Renda vs Despesas e Investimentos)
    ganho_h = obter_ganho("Henrique")
    ganho_c = obter_ganho("Camila")
    renda_casal = ganho_h + ganho_c
    saldo_livre = renda_casal - total_mes

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("💵 Renda Mensal Casal (Base)", formatar_moeda(renda_casal), f"H: {formatar_moeda(ganho_h)} | C: {formatar_moeda(ganho_c)}")
    r2.metric("⚖️ Saldo Livre (Renda - Contas)", formatar_moeda(saldo_livre), delta=formatar_moeda(saldo_livre))
    r3.metric("📈 Patrimônio Investido", formatar_moeda(total_investido))
    r4.metric("🚀 Ganho Investimentos", formatar_moeda(ganho_inv))

    st.markdown("---")

    if df_dash.empty:
        st.warning("Nenhuma conta encontrada para os filtros selecionados.")
    else:
        # Gráficos Principais
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Despesas por Categoria")
            df_cat_g = df_dash.groupby("categoria", as_index=False)["valor"].sum().sort_values(by="valor", ascending=True)
            fig_cat = px.bar(
                df_cat_g, x="valor", y="categoria", orientation="h", text_auto=".2s",
                color="valor", color_continuous_scale="Tealgrn", labels={"valor": "Valor (R$)", "categoria": "Categoria"}
            )
            fig_cat.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_cat, use_container_width=True)

        with g2:
            st.subheader("Divisão por Pessoa & Status")
            df_pes_stat = df_dash.groupby(["aba_dono", "status"], as_index=False)["valor"].sum()
            cores_status = {"Pago": "#10B981", "Pendente": "#F59E0B", "Atrasado": "#EF4444", "Cancelado": "#94A3B8"}
            fig_ps = px.bar(
                df_pes_stat, x="aba_dono", y="valor", color="status", barmode="group", text_auto=".2s",
                color_discrete_map=cores_status, labels={"aba_dono": "Conta de", "valor": "Valor (R$)", "status": "Status"}
            )
            fig_ps.update_layout(height=400)
            st.plotly_chart(fig_ps, use_container_width=True)

        g3, g4 = st.columns(2)
        with g3:
            st.subheader("Evolução Mensal do Casal")
            df_evol = df_contas.groupby(["mes_ano", "aba_dono"], as_index=False)["valor"].sum().sort_values("mes_ano")
            fig_evol = px.line(
                df_evol, x="mes_ano", y="valor", color="aba_dono", markers=True,
                labels={"mes_ano": "Mês", "valor": "Total (R$)", "aba_dono": "Pessoa"}
            )
            st.plotly_chart(fig_evol, use_container_width=True)

        with g4:
            st.subheader("Despesas por Responsável (Casal vs Individual)")
            df_resp = df_dash.groupby("responsavel", as_index=False)["valor"].sum()
            fig_resp = px.pie(df_resp, names="responsavel", values="valor", hole=0.45, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_resp, use_container_width=True)

# ==========================================
# 2. RESUMO MENSAL (CLARO E OBJETIVO)
# ==========================================
elif menu == "📅 Resumo Mensal":
    st.title("📅 Resumo Mensal Consolidado")
    st.markdown("Visão clara e objetiva mês a mês e detalhamento por categoria, espelhando a aba **Resumo Mensal** da sua planilha.")

    # Tabela 1: Visão Anual Mês a Mês (Henrique vs Camila vs Casal)
    st.subheader("1. Consolidado Mês a Mês (Contas Pagas vs Pendentes)")
    
    meses_todos = sorted(df_contas["mes_ano"].dropna().unique().tolist())
    linhas_resumo = []
    for m in meses_todos:
        df_m = df_contas[df_contas["mes_ano"] == m]
        df_h = df_m[df_m["aba_dono"] == "Henrique"]
        df_c = df_m[df_m["aba_dono"] == "Camila"]
        
        tot_h = df_h["valor"].sum()
        pago_h = df_h[df_h["status"].str.lower() == "pago"]["valor"].sum()
        pend_h = df_h[df_h["status"].str.lower().isin(["pendente", "atrasado"])]["valor"].sum()
        
        tot_c = df_c["valor"].sum()
        pago_c = df_c[df_c["status"].str.lower() == "pago"]["valor"].sum()
        pend_c = df_c[df_c["status"].str.lower().isin(["pendente", "atrasado"])]["valor"].sum()
        
        tot_casal = tot_h + tot_c
        pago_casal = pago_h + pago_c
        pend_casal = pend_h + pend_c
        perc_pago = (pago_casal / tot_casal * 100) if tot_casal > 0 else 0.0
        
        linhas_resumo.append({
            "Mês": m,
            "Total Henrique": tot_h,
            "Pago Henrique": pago_h,
            "Pendente Henrique": pend_h,
            "Total Camila": tot_c,
            "Pago Camila": pago_c,
            "Pendente Camila": pend_c,
            "Total Casal": tot_casal,
            "Total Pago": pago_casal,
            "Total Pendente": pend_casal,
            "% Quitado": f"{perc_pago:.1f}%"
        })
    
    df_resumo_anual = pd.DataFrame(linhas_resumo)
    if not df_resumo_anual.empty:
        st.dataframe(
            df_resumo_anual.style.format({
                "Total Henrique": "R$ {:,.2f}", "Pago Henrique": "R$ {:,.2f}", "Pendente Henrique": "R$ {:,.2f}",
                "Total Camila": "R$ {:,.2f}", "Pago Camila": "R$ {:,.2f}", "Pendente Camila": "R$ {:,.2f}",
                "Total Casal": "R$ {:,.2f}", "Total Pago": "R$ {:,.2f}", "Total Pendente": "R$ {:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Ainda não há dados mensais cadastrados.")

    st.markdown("---")
    
    # Tabela 2: Detalhamento por Categoria do Mês Selecionado
    col_rm1, col_rm2 = st.columns([1, 2.5])
    with col_rm1:
        st.subheader("2. Raio-X do Mês")
        mes_foco = st.selectbox("Escolha o Mês de Referência:", meses_todos if meses_todos else ["2026-11"], index=len(meses_todos)-1 if meses_todos else 0)
        df_foco = df_contas[df_contas["mes_ano"] == mes_foco]
        
        tot_foco = df_foco["valor"].sum()
        pago_foco = df_foco[df_foco["status"].str.lower() == "pago"]["valor"].sum()
        pend_foco = tot_foco - pago_foco
        
        st.metric(f"Total em {mes_foco}", formatar_moeda(tot_foco))
        st.metric("Já Quitado", formatar_moeda(pago_foco))
        st.metric("Falta Pagar", formatar_moeda(pend_foco))

    with col_rm2:
        st.subheader(f"Gastos por Categoria em {mes_foco}")
        resumo_cat = []
        for cat in lista_categorias:
            df_cat_mes = df_foco[df_foco["categoria"] == cat]
            val_h = df_cat_mes[df_cat_mes["aba_dono"] == "Henrique"]["valor"].sum()
            val_c = df_cat_mes[df_cat_mes["aba_dono"] == "Camila"]["valor"].sum()
            val_tot = val_h + val_c
            perc = (val_tot / tot_foco * 100) if tot_foco > 0 else 0.0
            resumo_cat.append({
                "Categoria": cat,
                "Henrique": val_h,
                "Camila": val_c,
                "Total no Mês": val_tot,
                "% do Mês": f"{perc:.1f}%"
            })
        df_res_cat = pd.DataFrame(resumo_cat).sort_values(by="Total no Mês", ascending=False)
        st.dataframe(
            df_res_cat.style.format({"Henrique": "R$ {:,.2f}", "Camila": "R$ {:,.2f}", "Total no Mês": "R$ {:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# 3 e 4. CONTAS HENRIQUE E CAMILA (CRUD COMPLETO)
# ==========================================
elif menu in ["🧔🏻 Contas Henrique", "👩🏻 Contas Camila"]:
    dono_atual = "Henrique" if "Henrique" in menu else "Camila"
    icone = "🧔🏻" if dono_atual == "Henrique" else "👩🏻"
    
    st.title(f"{icone} Contas do Mês - {dono_atual}")
    
    # Filtro superior de Mês e Configuração de Ganho do Mês (igual ao cabeçalho da planilha)
    df_dono = df_contas[df_contas["aba_dono"] == dono_atual].copy()
    meses_dono = sorted(df_dono["mes_ano"].dropna().unique().tolist())
    if not meses_dono:
        meses_dono = [date.today().strftime("%Y-%m")]
        
    col_topo1, col_topo2, col_topo3 = st.columns([1.5, 1.5, 1])
    with col_topo1:
        opcoes_mes_crud = ["Todos os Meses"] + meses_dono
        padrao_idx = opcoes_mes_crud.index("2026-11") if "2026-11" in opcoes_mes_crud else len(opcoes_mes_crud) - 1
        mes_crud = st.selectbox("📅 Mês Base de Visualização:", opcoes_mes_crud, index=padrao_idx)
    with col_topo2:
        status_filtro = st.multiselect("Filtrar Status:", lista_status, default=lista_status)
    with col_topo3:
        ganho_atual = obter_ganho(dono_atual)
        novo_ganho = st.number_input(f"💵 Ganho do Mês ({dono_atual}):", min_value=0.0, value=ganho_atual, step=100.0)
        if novo_ganho != ganho_atual:
            atualizar_ganho(dono_atual, novo_ganho)
            st.toast(f"Ganho de {dono_atual} atualizado!")
            st.rerun()

    if mes_crud != "Todos os Meses":
        df_dono_mes = df_dono[df_dono["mes_ano"] == mes_crud]
    else:
        df_dono_mes = df_dono
    df_dono_mes = df_dono_mes[df_dono_mes["status"].isin(status_filtro)]

    # Cabeçalho de Indicadores (Igual às células A3:H4 da aba de Contas da Planilha)
    tot_pagar = df_dono_mes["valor"].sum()
    tot_pago = df_dono_mes[df_dono_mes["status"].str.lower() == "pago"]["valor"].sum()
    tot_pend = df_dono_mes[df_dono_mes["status"].str.lower() == "pendente"]["valor"].sum()
    tot_atras = df_dono_mes[df_dono_mes["status"].str.lower() == "atrasado"]["valor"].sum()
    
    hoje = date.today()
    prox_7d = df_dono_mes[
        (df_dono_mes["status"].str.lower() != "pago") &
        (df_dono_mes["vencimento_dt"].dt.date >= hoje) &
        (df_dono_mes["vencimento_dt"].dt.date <= hoje + timedelta(days=7))
    ]["valor"].sum()
    saldo_restante = novo_ganho - tot_pagar

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total a Pagar", formatar_moeda(tot_pagar))
    c2.metric("Total Pago", formatar_moeda(tot_pago))
    c3.metric("Total Pendente", formatar_moeda(tot_pend))
    c4.metric("Total Atrasado", formatar_moeda(tot_atras))
    c5.metric("Próximos 7 dias", formatar_moeda(prox_7d))
    c6.metric("Saldo (Ganho - Contas)", formatar_moeda(saldo_restante))

    st.markdown("---")

    # FORMULÁRIO PARA ADICIONAR NOVA CONTA (CREATE)
    with st.expander(f"➕ Adicionar Nova Conta para {dono_atual}", expanded=False):
        with st.form(f"form_add_conta_{dono_atual}", clear_on_submit=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                in_desc = st.text_input("Descrição *", placeholder="Ex: Aluguel, Cemig, Cartão...")
                in_cat = st.selectbox("Categoria *", lista_categorias)
            with f2:
                in_val = st.number_input("Valor (R$) *", min_value=0.0, step=10.0, format="%.2f")
                in_venc = st.date_input("Data de Vencimento *", value=date.today())
            with f3:
                in_stat = st.selectbox("Status *", lista_status)
                in_forma = st.selectbox("Forma de Pagamento *", lista_formas)
            with f4:
                in_resp = st.selectbox("Responsável *", responsaveis_opcoes, index=responsaveis_opcoes.index(dono_atual) if dono_atual in responsaveis_opcoes else 0)
                in_obs = st.text_input("Observações", placeholder="Opcional...")
                
            btn_salvar_conta = st.form_submit_button("💾 Cadastrar Conta", use_container_width=True)
            if btn_salvar_conta:
                if not in_desc.strip():
                    st.error("Por favor, preencha a Descrição da conta.")
                else:
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (dono_atual, in_desc.strip(), in_cat, in_val, in_venc.strftime("%Y-%m-%d"), in_stat, in_forma, in_resp, in_obs.strip()))
                    conn.commit()
                    conn.close()
                    st.success(f"Conta '{in_desc}' adicionada com sucesso!")
                    st.rerun()

    # TABELA INTERATIVA PARA EDITAR E EXCLUIR (READ, UPDATE, DELETE)
    st.subheader("📋 Lançamentos (Clique duas vezes em qualquer célula para editar)")
    st.caption("Você pode alterar Status, Valores, Datas ou marcar a caixa **Excluir?** e clicar em **Salvar Alterações**.")

    if df_dono_mes.empty:
        st.info("Nenhuma conta encontrada neste filtro. Adicione uma nova conta acima!")
    else:
        df_edit_prep = df_dono_mes[["id", "descricao", "categoria", "valor", "vencimento_dt", "status", "forma_pagamento", "responsavel", "observacoes"]].copy()
        df_edit_prep["vencimento_dt"] = df_edit_prep["vencimento_dt"].dt.date
        df_edit_prep["Excluir?"] = False

        df_editado = st.data_editor(
            df_edit_prep,
            hide_index=True,
            use_container_width=True,
            disabled=["id"],
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "descricao": st.column_config.TextColumn("Descrição", required=True),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=lista_categorias, required=True),
                "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f", min_value=0.0, required=True),
                "vencimento_dt": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY", required=True),
                "status": st.column_config.SelectboxColumn("Status", options=lista_status, required=True),
                "forma_pagamento": st.column_config.SelectboxColumn("Forma de Pagamento", options=lista_formas, required=True),
                "responsavel": st.column_config.SelectboxColumn("Responsável", options=responsaveis_opcoes, required=True),
                "observacoes": st.column_config.TextColumn("Observações"),
                "Excluir?": st.column_config.CheckboxColumn("🗑️ Excluir?", default=False)
            },
            key=f"editor_contas_{dono_atual}"
        )

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("💾 Salvar Alterações / Exclusões", type="primary", use_container_width=True):
                conn = get_conn()
                c = conn.cursor()
                excluidos = 0
                atualizados = 0
                for _, row in df_editado.iterrows():
                    rec_id = int(row["id"])
                    if row["Excluir?"]:
                        c.execute("DELETE FROM contas WHERE id = ?", (rec_id,))
                        excluidos += 1
                    else:
                        venc_s = row["vencimento_dt"].strftime("%Y-%m-%d") if pd.notnull(row["vencimento_dt"]) else date.today().strftime("%Y-%m-%d")
                        obs_s = "" if pd.isna(row["observacoes"]) else str(row["observacoes"])
                        c.execute("""
                            UPDATE contas
                            SET descricao=?, categoria=?, valor=?, vencimento=?, status=?, forma_pagamento=?, responsavel=?, observacoes=?
                            WHERE id=?
                        """, (str(row["descricao"]), str(row["categoria"]), float(row["valor"]), venc_s, str(row["status"]), str(row["forma_pagamento"]), str(row["responsavel"]), obs_s, rec_id))
                        atualizados += 1
                conn.commit()
                conn.close()
                st.success(f"Pronto! {atualizados} registro(s) atualizado(s) e {excluidos} excluído(s).")
                st.rerun()

# ==========================================
# 5. INVESTIMENTOS (CRUD COMPLETO)
# ==========================================
elif menu == "📈 Investimentos":
    st.title("📈 Controle de Investimentos do Casal")
    st.markdown("Cadastre e acompanhe seus aportes com os mesmos campos da planilha (**Data, Mês, Pessoa, Tipo de investimento, Instituição, Valor aplicado, Saldo atual, Ganho no mês, Rentabilidade % e Observações**).")

    tot_aplicado = df_inv["valor_aplicado"].sum() if not df_inv.empty else 0.0
    tot_saldo = df_inv["saldo_atual"].sum() if not df_inv.empty else 0.0
    tot_ganho = df_inv["ganho_mes"].sum() if not df_inv.empty else 0.0
    rent_media = (tot_ganho / tot_aplicado * 100) if tot_aplicado > 0 else 0.0

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("💰 Total Aplicado", formatar_moeda(tot_aplicado))
    i2.metric("🏦 Saldo Atual Total", formatar_moeda(tot_saldo))
    i3.metric("🚀 Ganho Acumulado", formatar_moeda(tot_ganho))
    i4.metric("📊 Rentabilidade Geral", f"{rent_media:.2f}%")

    st.markdown("---")

    with st.expander("➕ Adicionar Novo Investimento", expanded=df_inv.empty):
        with st.form("form_add_investimento", clear_on_submit=True):
            ci1, ci2, ci3 = st.columns(3)
            with ci1:
                inv_data = st.date_input("Data da Aplicação *", value=date.today())
                inv_mes = st.text_input("Mês de Referência (AAAA-MM)", value=date.today().strftime("%Y-%m"))
                inv_pessoa = st.selectbox("Pessoa *", ["Henrique", "Camila", "Casal"])
            with ci2:
                inv_tipo = st.text_input("Tipo de Investimento *", placeholder="Ex: CDB, Tesouro Selic, FIIs, Caixinha...")
                inv_inst = st.text_input("Instituição *", placeholder="Ex: Nubank, XP, Itaú, Inter...")
                inv_obs = st.text_input("Observações", placeholder="Ex: Reserva de emergência / Casamento")
            with ci3:
                inv_val_ap = st.number_input("Valor Aplicado (R$) *", min_value=0.0, step=100.0, format="%.2f")
                inv_saldo = st.number_input("Saldo Atual (R$) *", min_value=0.0, step=100.0, format="%.2f")
                inv_ganho_manual = st.number_input("Ganho no Mês (R$) (Deixe 0 p/ calcular automático)", value=0.0, step=10.0, format="%.2f")

            if st.form_submit_button("💾 Salvar Investimento", use_container_width=True):
                if not inv_tipo.strip() or not inv_inst.strip():
                    st.error("Preencha o Tipo de Investimento e a Instituição.")
                else:
                    ganho_calc = inv_ganho_manual if inv_ganho_manual != 0.0 else (inv_saldo - inv_val_ap)
                    rent_calc = (ganho_calc / inv_val_ap * 100) if inv_val_ap > 0 else 0.0
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO investimentos (data, mes, pessoa, tipo_investimento, instituicao, valor_aplicado, saldo_atual, ganho_mes, rentabilidade, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (inv_data.strftime("%Y-%m-%d"), inv_mes.strip(), inv_pessoa, inv_tipo.strip(), inv_inst.strip(), inv_val_ap, inv_saldo, ganho_calc, rent_calc, inv_obs.strip()))
                    conn.commit()
                    conn.close()
                    st.success("Investimento cadastrado com sucesso!")
                    st.rerun()

    st.subheader("📋 Carteira de Investimentos (Editável)")
    if df_inv.empty:
        st.info("Nenhum investimento cadastrado ainda. Use o formulário acima para começar!")
    else:
        df_inv_prep = df_inv[["id", "data_dt", "mes", "pessoa", "tipo_investimento", "instituicao", "valor_aplicado", "saldo_atual", "ganho_mes", "rentabilidade", "observacoes"]].copy()
        df_inv_prep["data_dt"] = df_inv_prep["data_dt"].dt.date
        df_inv_prep["Excluir?"] = False

        df_inv_edit = st.data_editor(
            df_inv_prep,
            hide_index=True,
            use_container_width=True,
            disabled=["id", "rentabilidade"],
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "data_dt": st.column_config.DateColumn("Data", format="DD/MM/YYYY", required=True),
                "mes": st.column_config.TextColumn("Mês (AAAA-MM)", required=True),
                "pessoa": st.column_config.SelectboxColumn("Pessoa", options=["Henrique", "Camila", "Casal"], required=True),
                "tipo_investimento": st.column_config.TextColumn("Tipo de Investimento", required=True),
                "instituicao": st.column_config.TextColumn("Instituição", required=True),
                "valor_aplicado": st.column_config.NumberColumn("Valor Aplicado", format="R$ %.2f", required=True),
                "saldo_atual": st.column_config.NumberColumn("Saldo Atual", format="R$ %.2f", required=True),
                "ganho_mes": st.column_config.NumberColumn("Ganho no Mês", format="R$ %.2f", required=True),
                "rentabilidade": st.column_config.NumberColumn("Rentabilidade %", format="%.2f%%"),
                "observacoes": st.column_config.TextColumn("Observações"),
                "Excluir?": st.column_config.CheckboxColumn("🗑️ Excluir?", default=False)
            },
            key="editor_investimentos"
        )

        if st.button("💾 Salvar Alterações nos Investimentos", type="primary"):
            conn = get_conn()
            c = conn.cursor()
            for _, row in df_inv_edit.iterrows():
                rec_id = int(row["id"])
                if row["Excluir?"]:
                    c.execute("DELETE FROM investimentos WHERE id = ?", (rec_id,))
                else:
                    dt_s = row["data_dt"].strftime("%Y-%m-%d") if pd.notnull(row["data_dt"]) else date.today().strftime("%Y-%m-%d")
                    v_ap = float(row["valor_aplicado"])
                    s_at = float(row["saldo_atual"])
                    g_m = float(row["ganho_mes"])
                    rent_nova = (g_m / v_ap * 100) if v_ap > 0 else 0.0
                    obs_s = "" if pd.isna(row["observacoes"]) else str(row["observacoes"])
                    c.execute("""
                        UPDATE investimentos
                        SET data=?, mes=?, pessoa=?, tipo_investimento=?, instituicao=?, valor_aplicado=?, saldo_atual=?, ganho_mes=?, rentabilidade=?, observacoes=?
                        WHERE id=?
                    """, (dt_s, str(row["mes"]), str(row["pessoa"]), str(row["tipo_investimento"]), str(row["instituicao"]), v_ap, s_at, g_m, rent_nova, obs_s, rec_id))
            conn.commit()
            conn.close()
            st.success("Carteira de investimentos atualizada!")
            st.rerun()

# ==========================================
# 6. CRUD DE CATEGORIAS, STATUS E PAGAMENTOS
# ==========================================
elif menu == "🏷️ Categorias & Opções":
    st.title("🏷️ Gerenciar Categorias, Status e Formas de Pagamento")
    st.markdown("Edite as listas abaixo para atualizar automaticamente os menus suspensos das abas de contas (assim como na aba **Categorias** da sua planilha).")

    col_p1, col_p2, col_p3 = st.columns(3)

    def renderizar_crud_parametro(coluna, titulo, tipo_param):
        with coluna:
            st.subheader(titulo)
            _, df_p = carregar_parametros(tipo_param)
            
            with st.form(f"form_add_{tipo_param}", clear_on_submit=True):
                novo_val = st.text_input(f"Nova opção de {titulo}:")
                if st.form_submit_button("➕ Adicionar", use_container_width=True):
                    if novo_val.strip():
                        conn = get_conn()
                        c = conn.cursor()
                        c.execute("INSERT INTO parametros (tipo, valor) VALUES (?, ?)", (tipo_param, novo_val.strip()))
                        conn.commit()
                        conn.close()
                        st.rerun()

            if not df_p.empty:
                df_p["Excluir?"] = False
                df_p_edit = st.data_editor(
                    df_p,
                    hide_index=True,
                    use_container_width=True,
                    disabled=["id"],
                    column_config={
                        "id": None,
                        "valor": st.column_config.TextColumn("Nome", required=True),
                        "Excluir?": st.column_config.CheckboxColumn("🗑️", width="small")
                    },
                    key=f"editor_param_{tipo_param}"
                )
                if st.button(f"💾 Salvar {titulo}", key=f"btn_save_{tipo_param}", use_container_width=True):
                    conn = get_conn()
                    c = conn.cursor()
                    for _, r in df_p_edit.iterrows():
                        if r["Excluir?"]:
                            c.execute("DELETE FROM parametros WHERE id = ?", (int(r["id"]),))
                        else:
                            c.execute("UPDATE parametros SET valor = ? WHERE id = ?", (str(r["valor"]).strip(), int(r["id"])))
                    conn.commit()
                    conn.close()
                    st.success(f"{titulo} atualizados!")
                    st.rerun()

    renderizar_crud_parametro(col_p1, "Categorias", "categoria")
    renderizar_crud_parametro(col_p2, "Status", "status")
    renderizar_crud_parametro(col_p3, "Formas de Pagamento", "forma_pagamento")