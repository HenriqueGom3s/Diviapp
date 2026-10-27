import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import re
from datetime import date
import io

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E CSS UI/UX MOBILE-FIRST PROFISSIONAL
# ==========================================
st.set_page_config(page_title="Diviapp Pro", page_icon="💎", layout="wide", initial_sidebar_state="auto")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap');

    :root {
        --bg-main: #F4F7F6;
        --bg-surface: #FFFFFF;
        --bg-sidebar: #0E1626;
        --bg-sidebar-hover: rgba(56, 189, 248, 0.12);
        --color-primary: #0F172A;
        --color-accent: #059669;
        --color-accent-hover: #047857;
        --color-secondary: #3B82F6;
        --text-primary: #1E293B;
        --text-secondary: #64748B;
        --text-on-dark: #F8FAFC;
        --status-ok-bg: #D1FAE5;
        --status-ok-text: #065F46;
        --status-warn-bg: #FEF3C7;
        --status-warn-text: #92400E;
        --status-danger-bg: #FEE2E2;
        --status-danger-text: #991B1B;
        --border-subtle: #E2E8F0;
        --radius-md: 10px;
        --radius-lg: 16px;
        --shadow-soft: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        --shadow-hover: 0 12px 28px -6px rgba(15, 23, 42, 0.1);
        --transition-fast: all 0.2s ease-in-out;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-main);
        color: var(--text-primary);
        -webkit-font-smoothing: antialiased;
    }

    .main {
        background-color: var(--bg-main) !important;
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1, h2, h3, .card-value {
        font-family: 'Outfit', sans-serif !important;
        color: var(--color-primary) !important;
        letter-spacing: -0.02em;
    }

    /* Otimizações Mobile Responsivas */
    @media (max-width: 768px) {
        .main {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            padding-top: 0.5rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        .card-value {
            font-size: 1.35rem !important;
        }
        .pro-card, .pro-card-dark {
            padding: 16px 18px !important;
            margin-bottom: 10px !important;
        }
    }
    
    /* Cards Executivos */
    .pro-card {
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        padding: 22px 24px;
        border: 1px solid var(--border-subtle);
        box-shadow: var(--shadow-soft);
        transition: var(--transition-fast);
        margin-bottom: 14px;
    }
    .pro-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
        border-color: #CBD5E1;
    }
    .pro-card-dark {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 70%, #312E81 100%);
        color: var(--text-on-dark);
        border-radius: var(--radius-lg);
        padding: 22px 24px;
        box-shadow: 0 10px 24px -6px rgba(15, 23, 42, 0.2);
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .pro-card-dark .card-value {
        color: #FFFFFF !important;
    }
    .card-label {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-bottom: 6px;
    }
    .pro-card-dark .card-label {
        color: #94A3B8;
    }
    .card-value {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.15;
        font-variant-numeric: tabular-nums;
    }
    .card-sub {
        font-size: 0.82rem;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(226, 232, 240, 0.6);
        color: var(--text-secondary);
    }
    .pro-card-dark .card-sub {
        border-top-color: rgba(255, 255, 255, 0.12);
        color: #CBD5E1;
    }
    
    /* Badges de Status Modernos */
    .badge-ok { background: var(--status-ok-bg); color: var(--status-ok-text); padding: 3px 10px; border-radius: 999px; font-weight: 600; font-size: 0.74rem; display: inline-block; }
    .badge-warn { background: var(--status-warn-bg); color: var(--status-warn-text); padding: 3px 10px; border-radius: 999px; font-weight: 600; font-size: 0.74rem; display: inline-block; }
    .badge-danger { background: var(--status-danger-bg); color: var(--status-danger-text); padding: 3px 10px; border-radius: 999px; font-weight: 600; font-size: 0.74rem; display: inline-block; }
    
    /* Sidebar Redesenhada */
    div[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid #1E293B;
    }
    div[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    div[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-md);
        padding: 12px 16px !important;
        margin-bottom: 8px !important;
        transition: var(--transition-fast);
        cursor: pointer;
    }
    div[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: var(--bg-sidebar-hover);
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateX(3px);
    }
    div[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.1px;
    }
    div[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "diviapp_pro.db"
EXCEL_PADRAO = "controle_financeiro - HENRIQUE E CAMILA_2.xlsx"
EXCEL_ALT = "controle_financeiro - HENRIQUE E CAMILA.xlsx"

# ==========================================
# DATAS E ABREVIAÇÕES DE MESES (/JAN, /FEV...)
# ==========================================
MESES_ABREV = {
    1: "/JAN", 2: "/FEV", 3: "/MAR", 4: "/ABR",
    5: "/MAI", 6: "/JUN", 7: "/JUL", 8: "/AGO",
    9: "/SET", 10: "/OUT", 11: "/NOV", 12: "/DEZ"
}

def formatar_mes_abrev(mes_ano_str):
    if not mes_ano_str or not isinstance(mes_ano_str, str) or "-" not in mes_ano_str:
        return str(mes_ano_str)
    try:
        ano, mes = mes_ano_str.split("-")
        return f"{MESES_ABREV.get(int(mes), '/MÊS')} {ano}"
    except Exception:
        return mes_ano_str

def formatar_data_abrev(dt):
    if pd.isna(dt):
        return "-"
    try:
        return f"{dt.day:02d}{MESES_ABREV.get(dt.month, '')}"
    except Exception:
        return str(dt)

def calcular_mes_adjacente(ano, mes, delta):
    total_meses = (ano * 12 + (mes - 1)) + delta
    novo_ano = total_meses // 12
    novo_mes = (total_meses % 12) + 1
    return f"{novo_ano:04d}-{novo_mes:02d}"

# ==========================================
# MAPA DE EMOJIS INTELIGENTE
# ==========================================
EMOJI_MAP = {
    "moradia": "🏠", "aluguel": "🏠", "casa": "🏠",
    "mercado": "🛒", "alimentação": "🛒", "feira": "🛒",
    "energia": "⚡", "luz": "⚡", "cemig": "⚡",
    "água": "💧", "agua": "💧", "saneamento": "💧",
    "casamento": "💍", "noivado": "💍", "festa": "💍",
    "telefone": "📱", "celular": "📱", "internet": "🌐",
    "transporte": "🚗", "uber": "🚗", "combustível": "⛽", "gasolina": "⛽",
    "saúde": "🩺", "saude": "🩺", "farmácia": "💊", "remédio": "💊",
    "lazer": "🍿", "streaming": "🎬", "viagem": "✈️", "restaurante": "🍽️",
    "compras pessoais": "🛍️", "compras": "🛍️", "roupas": "👕",
    "cartão de crédito": "💳", "cartao de credito": "💳", "cartão": "💳", "nubank": "💳",
    "financiamento": "🏦", "empréstimo": "🏦",
    "carro": "🚙", "ipva": "🚙", "oficina": "🔧",
    "investimentos": "📈", "reserva": "💰", "poupança": "💰",
    "outros": "📦", "educação": "📚", "pet": "🐾"
}

def aplicar_emoji(nome_cat):
    if not nome_cat:
        return "📦 Outros"
    texto = str(nome_cat).strip()
    texto_limpo = re.sub(r'^[^\w\sÀ-ÿ]+\s*', '', texto).strip()
    if not texto_limpo:
        texto_limpo = "Outros"
    chave = texto_limpo.lower()
    for k, emj in EMOJI_MAP.items():
        if k in chave:
            return f"{emj} {texto_limpo}"
    return f"🏷️ {texto_limpo}"

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==========================================
# BANCO DE DADOS E SANITIZAÇÃO
# ==========================================
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def sanitizar_emojis_banco():
    conn = get_conn()
    c = conn.cursor()
    try:
        for tabela, col in [("contas", "categoria"), ("parametros", "valor")]:
            if tabela == "parametros":
                rows = c.execute("SELECT id, valor FROM parametros WHERE tipo='categoria'").fetchall()
            else:
                rows = c.execute("SELECT id, categoria FROM contas").fetchall()
            for r_id, val in rows:
                novo_val = aplicar_emoji(val)
                if novo_val != val:
                    c.execute(f"UPDATE {tabela} SET {col} = ? WHERE id = ?", (novo_val, r_id))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def inicializar_banco():
    if os.path.exists(DB_FILE):
        sanitizar_emojis_banco()
        return
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, aba_dono TEXT, descricao TEXT, categoria TEXT,
        valor REAL, vencimento TEXT, status TEXT, forma_pagamento TEXT, responsavel TEXT, observacoes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS investimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, mes TEXT, pessoa TEXT, tipo_investimento TEXT,
        instituicao TEXT, valor_aplicado REAL, saldo_atual REAL, ganho_mes REAL, rentabilidade REAL, observacoes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS parametros (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, valor TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS ganhos (aba_dono TEXT PRIMARY KEY, ganho_mensal REAL)""")
    c.execute("INSERT OR REPLACE INTO ganhos VALUES ('Henrique', 3985.0), ('Camila', 2860.0)")

    arquivo = EXCEL_PADRAO if os.path.exists(EXCEL_PADRAO) else (EXCEL_ALT if os.path.exists(EXCEL_ALT) else None)
    if arquivo:
        try:
            xls = pd.ExcelFile(arquivo)
            if "Categorias" in xls.sheet_names:
                df_cat = pd.read_excel(xls, sheet_name="Categorias")
                for col, tipo in [("Categorias", "categoria"), ("Status", "status"), ("Formas de pagamento", "forma_pagamento")]:
                    if col in df_cat.columns:
                        for val in df_cat[col].dropna().unique():
                            val_s = str(val).strip()
                            if val_s:
                                valor_final = aplicar_emoji(val_s) if tipo == "categoria" else val_s
                                c.execute("INSERT INTO parametros (tipo, valor) VALUES (?, ?)", (tipo, valor_final))

            for aba, dono in [("Contas do Mês Henrique", "Henrique"), ("Contas do Mês Camila", "Camila")]:
                if aba in xls.sheet_names:
                    df_c = pd.read_excel(xls, sheet_name=aba, skiprows=6).dropna(subset=["Descrição", "Valor"], how="all")
                    for _, row in df_c.iterrows():
                        venc = pd.to_datetime(row.get("Vencimento"), errors="coerce")
                        venc_str = venc.strftime("%Y-%m-%d") if pd.notnull(venc) else date.today().strftime("%Y-%m-%d")
                        obs = "" if pd.isna(row.get("Observações")) else str(row.get("Observações"))
                        cat_emj = aplicar_emoji(row.get("Categoria", "Outros"))
                        c.execute("""INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                            dono, str(row.get("Descrição", "")).strip(), cat_emj,
                            float(row.get("Valor", 0.0)) if pd.notnull(row.get("Valor")) else 0.0,
                            venc_str, str(row.get("Status", "Pendente")).strip(),
                            str(row.get("Forma de pagamento", "Pix")).strip(), str(row.get("Responsável", dono)).strip(), obs
                        ))

            if "Investimentos" in xls.sheet_names:
                df_inv = pd.read_excel(xls, sheet_name="Investimentos").dropna(subset=["Tipo de investimento", "Valor aplicado", "Saldo atual"], how="all")
                for _, row in df_inv.iterrows():
                    dt = pd.to_datetime(row.get("Data"), errors="coerce")
                    dt_str = dt.strftime("%Y-%m-%d") if pd.notnull(dt) else date.today().strftime("%Y-%m-%d")
                    mes_str = dt.strftime("%Y-%m") if pd.notnull(dt) else date.today().strftime("%Y-%m")
                    v_ap = float(row.get("Valor aplicado", 0.0)) if pd.notnull(row.get("Valor aplicado")) else 0.0
                    s_at = float(row.get("Saldo atual", 0.0)) if pd.notnull(row.get("Saldo atual")) else 0.0
                    ganho = float(row.get("Ganho no mês", s_at - v_ap)) if pd.notnull(row.get("Ganho no mês")) else (s_at - v_ap)
                    rent = (ganho / v_ap * 100) if v_ap > 0 else 0.0
                    obs = "" if pd.isna(row.get("Observações")) else str(row.get("Observações"))
                    c.execute("""INSERT INTO investimentos (data, mes, pessoa, tipo_investimento, instituicao, valor_aplicado, saldo_atual, ganho_mes, rentabilidade, observacoes)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                        dt_str, mes_str, str(row.get("Pessoa", "Casal")), str(row.get("Tipo de investimento", "")),
                        str(row.get("Instituição", "")), v_ap, s_at, ganho, rent, obs
                    ))
            conn.commit()
            conn.close()
            return
        except Exception:
            pass

    cats_default = ["Moradia", "Mercado", "Energia", "Água", "Casamento", "Telefone", "Transporte", "Saúde", "Lazer", "Compras pessoais", "Cartão de crédito", "Financiamento", "Carro", "Investimentos", "Outros"]
    for v in cats_default: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('categoria', ?)", (aplicar_emoji(v),))
    for v in ["Pendente", "Pago", "Atrasado", "Cancelado"]: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('status', ?)", (v,))
    for v in ["Pix", "Débito", "Crédito", "Boleto", "Dinheiro", "Transferência", "Débito automático"]: c.execute("INSERT INTO parametros (tipo, valor) VALUES ('forma_pagamento', ?)", (v,))
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def ler_dados_completos():
    conn = get_conn()
    df_c = pd.read_sql_query("SELECT * FROM contas", conn)
    df_i = pd.read_sql_query("SELECT * FROM investimentos", conn)
    df_p = pd.read_sql_query("SELECT * FROM parametros ORDER BY id", conn)
    df_g = pd.read_sql_query("SELECT * FROM ganhos", conn)
    conn.close()

    if not df_c.empty:
        df_c["categoria"] = df_c["categoria"].apply(aplicar_emoji)
        df_c["vencimento_dt"] = pd.to_datetime(df_c["vencimento"], errors="coerce")
        df_c["mes_ano"] = df_c["vencimento_dt"].dt.strftime("%Y-%m")
        df_c["mes_abrev"] = df_c["mes_ano"].apply(formatar_mes_abrev)
    else:
        df_c["vencimento_dt"] = pd.Series(dtype="datetime64[ns]")
        df_c["mes_ano"] = pd.Series(dtype="str")
        df_c["mes_abrev"] = pd.Series(dtype="str")

    if not df_i.empty:
        df_i["data_dt"] = pd.to_datetime(df_i["data"], errors="coerce")

    return df_c, df_i, df_p, df_g

def limpar_cache():
    ler_dados_completos.clear()

def render_card(label, valor, sub="", dark=False):
    classe = "pro-card-dark" if dark else "pro-card"
    st.markdown(f"""
        <div class="{classe}">
            <div class="card-label">{label}</div>
            <div class="card-value">{valor}</div>
            <div class="card-sub">{sub}</div>
        </div>
    """, unsafe_allow_html=True)

inicializar_banco()
df_contas, df_inv, df_param, df_ganhos = ler_dados_completos()

lista_categorias = df_param[df_param["tipo"] == "categoria"]["valor"].apply(aplicar_emoji).drop_duplicates().tolist()
lista_status = df_param[df_param["tipo"] == "status"]["valor"].drop_duplicates().tolist()
lista_formas = df_param[df_param["tipo"] == "forma_pagamento"]["valor"].drop_duplicates().tolist()
responsaveis_opcoes = ["Casal", "Henrique", "Camila"]

hoje = date.today()
mes_atual_str = hoje.strftime("%Y-%m")

# ==========================================
# SIDEBAR COM LOGO MODERNA E RECOLHIMENTO AUTOMÁTICO EM MOBILE
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px 8px 18px 8px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px;">
            <div style="background: linear-gradient(135deg, #3B82F6 0%, #059669 100%); width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3); flex-shrink: 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div>
                <div style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.4px; color: #FFFFFF; line-height: 1.1;">Diviapp<span style="color:#38BDF8;">Pro</span></div>
                <div style="font-size: 0.78rem; font-weight: 500; color: #94A3B8; margin-top: 2px;">Henrique & Camila</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navegação Principal",
        [
            "🚀 Visão Geral",
            "📅 Resumo Mensal",
            "🧔🏻 Contas Henrique",
            "👩🏻 Contas Camila",
            "📈 Investimentos",
            "🏷️ Categorias & Opções"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("💾 Backup & Exportar Excel"):
        if st.button("Preparar Ficheiro Excel", use_container_width=True):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_contas[df_contas["aba_dono"] == "Henrique"].to_excel(writer, sheet_name="Contas do Mês Henrique", index=False)
                df_contas[df_contas["aba_dono"] == "Camila"].to_excel(writer, sheet_name="Contas do Mês Camila", index=False)
                df_inv.to_excel(writer, sheet_name="Investimentos", index=False)
            st.download_button(
                "📥 Descarregar Planilha (.xlsx)",
                data=output.getvalue(),
                file_name=f"Diviapp_{date.today().strftime('%Y_%m_%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        if st.button("🔄 Repor Planilha Original", use_container_width=True):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            limpar_cache()
            st.rerun()

# ==========================================
# 1. VISÃO GERAL (MÊS ATUAL POR PADRÃO)
# ==========================================
if menu == "🚀 Visão Geral":
    st.title("🚀 Visão Geral Financeira")

    meses_disp = sorted(list(set(df_contas["mes_ano"].dropna().unique().tolist() + [mes_atual_str])))
    opcoes_mapa = {m: formatar_mes_abrev(m) for m in meses_disp}

    f_col1, f_col2 = st.columns([2.2, 1])
    with f_col1:
        meses_sel = st.multiselect(
            "📅 Mês de Referência:",
            options=meses_disp,
            default=[mes_atual_str],
            format_func=lambda x: opcoes_mapa.get(x, x)
        )
    with f_col2:
        pessoas_sel = st.multiselect(
            "👥 Titular:",
            options=["Henrique", "Camila"],
            default=["Henrique", "Camila"]
        )

    df_dash = df_contas.copy()
    if meses_sel:
        df_dash = df_dash[df_dash["mes_ano"].isin(meses_sel)]
    if pessoas_sel:
        df_dash = df_dash[df_dash["aba_dono"].isin(pessoas_sel)]

    total_geral = df_dash["valor"].sum()
    total_pago = df_dash[df_dash["status"].str.lower() == "pago"]["valor"].sum()
    total_pendente = df_dash[df_dash["status"].str.lower() == "pendente"]["valor"].sum()
    total_atrasado = df_dash[df_dash["status"].str.lower() == "atrasado"]["valor"].sum()
    total_h = df_dash[df_dash["aba_dono"] == "Henrique"]["valor"].sum()
    total_c = df_dash[df_dash["aba_dono"] == "Camila"]["valor"].sum()
    patrimonio = df_inv["saldo_atual"].sum() if not df_inv.empty else 0.0
    perc_quitado = (total_pago / total_geral * 100) if total_geral > 0 else 0.0

    # Layout responsivo em colunas adaptadas para mobile via Streamlit grid nativo
    c1, c2 = st.columns(2)
    with c1:
        render_card("💰 Total no Período", formatar_moeda(total_geral), f"🧔🏻 H: {formatar_moeda(total_h)} | 👩🏻 C: {formatar_moeda(total_c)}", dark=True)
    with c2:
        render_card("✅ Total Quitado", formatar_moeda(total_pago), f"<span class='badge-ok'>{perc_quitado:.1f}% pago do total</span>")

    c3, c4 = st.columns(2)
    with c3:
        render_card("⏳ Falta Pagar (Pendente)", formatar_moeda(total_pendente), f"<span class='badge-warn'>{len(df_dash[df_dash['status'].str.lower()=='pendente'])} contas em aberto</span>")
    with c4:
        render_card("🚨 Atrasado + 📈 Investido", formatar_moeda(total_atrasado), f"Patrimônio: <b>{formatar_moeda(patrimonio)}</b>")

    st.progress(min(perc_quitado / 100.0, 1.0), text=f"Progresso de Quitação do Período: {perc_quitado:.1f}%")

    df_alertas = df_dash[df_dash["status"].str.lower().isin(["atrasado", "pendente"])].sort_values(by="vencimento_dt")
    if not df_alertas.empty:
        st.markdown("### 🔔 Atenção Imediata: Próximas Contas a Pagar")
        cols_alerta = st.columns(min(2, len(df_alertas)))
        for idx, (_, row_al) in enumerate(df_alertas.head(4).iterrows()):
            with cols_alerta[idx % 2]:
                cor_borda = "#EF4444" if str(row_al["status"]).lower() == "atrasado" else "#F59E0B"
                venc_fmt = f"{row_al['vencimento_dt'].day:02d}{MESES_ABREV.get(row_al['vencimento_dt'].month, '')}" if pd.notnull(row_al["vencimento_dt"]) else "-"
                st.markdown(f"""
                    <div style="background:white; border-left: 4px solid {cor_borda}; padding: 12px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; margin-bottom: 8px;">
                        <div style="font-size:0.72rem; color:#64748B; font-weight:600;">{row_al['aba_dono']} • Vence {venc_fmt}</div>
                        <div style="font-size:0.95rem; font-weight:700; color:#1E293B; margin:4px 0;">{row_al['descricao']}</div>
                        <div style="font-size:0.8rem; color:#475569;">{row_al['categoria']}</div>
                        <div style="font-size:1.05rem; font-weight:700; color:{cor_borda}; margin-top:4px;">{formatar_moeda(row_al['valor'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not df_dash.empty:
        g1, g2 = st.columns([1, 1])
        with g1:
            st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
            st.subheader("📊 Despesas por Categoria")
            df_cat_g = df_dash.groupby("categoria", as_index=False)["valor"].sum().sort_values(by="valor", ascending=True)
            fig_cat = px.bar(
                df_cat_g, x="valor", y="categoria", orientation="h", text_auto=".2s",
                color="valor", color_continuous_scale=["#93C5FD", "#1E293B"]
            )
            fig_cat.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with g2:
            st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
            st.subheader("⚖️ Divisão Henrique vs Camila")
            df_ev = df_dash.groupby(["mes_abrev", "aba_dono"], as_index=False)["valor"].sum()
            fig_ev = px.bar(
                df_ev, x="mes_abrev", y="valor", color="aba_dono", barmode="group", text_auto=".2s",
                color_discrete_map={"Henrique": "#1E293B", "Camila": "#EC4899"}
            )
            fig_ev.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="rgba(0,0,0,0)", legend_title_text="")
            st.plotly_chart(fig_ev, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum lançamento encontrado para o mês selecionado.")

# ==========================================
# 2. RESUMO MENSAL (PASSADO, ATUAL, PRÓXIMO)
# ==========================================
elif menu == "📅 Resumo Mensal":
    st.title("📅 Resumo Mensal Inteligente")

    mes_passado = calcular_mes_adjacente(hoje.year, hoje.month, -1)
    mes_atual = calcular_mes_adjacente(hoje.year, hoje.month, 0)
    proximo_mes = calcular_mes_adjacente(hoje.year, hoje.month, 1)

    meses_foco = [
        ("⏪ Mês Passado", mes_passado, False),
        ("📍 Mês Atual", mes_atual, True),
        ("⏩ Próximo Mês", proximo_mes, False)
    ]

    for rotulo, m_cod, destaque_escuro in meses_foco:
        df_m = df_contas[df_contas["mes_ano"] == m_cod]
        tot_m = df_m["valor"].sum()
        pago_m = df_m[df_m["status"].str.lower() == "pago"]["valor"].sum()
        pend_m = tot_m - pago_m
        perc_m = (pago_m / tot_m * 100) if tot_m > 0 else 0.0
        render_card(
            f"{rotulo} ({formatar_mes_abrev(m_cod)})",
            formatar_moeda(tot_m),
            f"✅ Pago: {formatar_moeda(pago_m)} ({perc_m:.0f}%) | ⏳ Falta: <b>{formatar_moeda(pend_m)}</b>",
            dark=destaque_escuro
        )

    st.markdown("### 🏷️ Comparativo de Categorias por Mês")
    if not df_contas.empty:
        piv_cat = df_contas.pivot_table(index="categoria", columns="mes_ano", values="valor", aggfunc="sum", fill_value=0.0)
        colunas_ordenadas = sorted(piv_cat.columns.tolist())
        piv_cat = piv_cat[colunas_ordenadas]
        piv_cat.columns = [formatar_mes_abrev(c) for c in colunas_ordenadas]
        piv_cat["Total Geral"] = piv_cat.sum(axis=1)
        piv_cat = piv_cat.sort_values(by="Total Geral", ascending=False).reset_index()
        
        col_cfg = {"categoria": st.column_config.TextColumn("Categoria")}
        for c_name in piv_cat.columns:
            if c_name != "categoria":
                col_cfg[c_name] = st.column_config.NumberColumn(c_name, format="R$ %.2f")

        st.dataframe(piv_cat, column_config=col_cfg, use_container_width=True, hide_index=True)

# ==========================================
# 3 e 4. CENTRAL DE CONTAS (HENRIQUE & CAMILA)
# ==========================================
elif menu in ["🧔🏻 Contas Henrique", "👩🏻 Contas Camila"]:
    dono_atual = "Henrique" if "Henrique" in menu else "Camila"
    icone = "🧔🏻" if dono_atual == "Henrique" else "👩🏻"

    st.title(f"{icone} Central de Contas — {dono_atual}")

    @st.fragment
    def secao_crud_contas(dono):
        df_c_all, _, _, df_g_all = ler_dados_completos()
        df_dono_total = df_c_all[df_c_all["aba_dono"] == dono].sort_values(by="vencimento_dt", ascending=False).copy()
        ganho_dono = float(dict(zip(df_g_all["aba_dono"], df_g_all["ganho_mensal"])).get(dono, 0.0))

        chave_limite = f"limite_linhas_{dono}"
        if chave_limite not in st.session_state:
            st.session_state[chave_limite] = 20

        meses_dono = sorted(list(set(df_dono_total["mes_ano"].dropna().unique().tolist() + [mes_atual_str])))
        opcoes_mes_dono = ["TODOS"] + meses_dono
        idx_padrao = opcoes_mes_dono.index(mes_atual_str) if mes_atual_str in opcoes_mes_dono else 0

        col_f_mes, col_f_busca, col_btn_mais = st.columns([1.2, 2, 0.6])
        with col_f_mes:
            mes_escolhido = st.selectbox(
                "📅 Mês",
                options=opcoes_mes_dono,
                index=idx_padrao,
                format_func=lambda x: "🗓️ Todos" if x == "TODOS" else formatar_mes_abrev(x),
                label_visibility="collapsed",
                key=f"sel_mes_{dono}"
            )
        with col_f_busca:
            busca = st.text_input(
                "🔎 Filtrar",
                placeholder="🔎 Buscar...",
                label_visibility="collapsed",
                key=f"busca_{dono}"
            )
        with col_btn_mais:
            with st.popover("➕ Nova", use_container_width=True):
                with st.form(f"form_rapido_{dono}", clear_on_submit=True):
                    st.markdown(f"**Nova Conta ({dono})**")
                    in_desc = st.text_input("Descrição *", placeholder="Ex: Energia...")
                    in_cat = st.selectbox("Categoria", lista_categorias)
                    in_val = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
                    in_venc = st.date_input("Vencimento", value=date.today())
                    in_stat = st.selectbox("Status", lista_status)
                    in_forma = st.selectbox("Pagamento", lista_formas)
                    in_resp = st.selectbox("Responsável", responsaveis_opcoes, index=responsaveis_opcoes.index(dono))
                    in_obs = st.text_input("Observações")

                    if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                        if in_desc.strip():
                            conn = get_conn()
                            conn.execute("""INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                         (dono, in_desc.strip(), aplicar_emoji(in_cat), in_val, in_venc.strftime("%Y-%m-%d"), in_stat, in_forma, in_resp, in_obs.strip()))
                            conn.commit()
                            conn.close()
                            limpar_cache()
                            st.rerun()

        df_dono = df_dono_total.copy()
        if mes_escolhido != "TODOS":
            df_dono = df_dono[df_dono["mes_ano"] == mes_escolhido]

        if busca.strip():
            termo = busca.strip().lower()
            df_dono = df_dono[
                df_dono["descricao"].str.lower().str.contains(termo, na=False) |
                df_dono["categoria"].str.lower().str.contains(termo, na=False) |
                df_dono["status"].str.lower().str.contains(termo, na=False)
            ]

        tot_geral = df_dono["valor"].sum()
        tot_pago = df_dono[df_dono["status"].str.lower() == "pago"]["valor"].sum()
        tot_pend = df_dono[df_dono["status"].str.lower().isin(["pendente", "atrasado"])]["valor"].sum()

        k1, k2 = st.columns(2)
        with k1:
            sub_mes = formatar_mes_abrev(mes_escolhido) if mes_escolhido != "TODOS" else "Geral"
            render_card(f"Total ({sub_mes})", formatar_moeda(tot_geral), f"{len(df_dono)} contas", dark=True)
        with k2:
            render_card("✅ Total Pago", formatar_moeda(tot_pago), "Quitadas")

        k3, k4 = st.columns(2)
        with k3:
            render_card("⏳ Pendente", formatar_moeda(tot_pend), "Em aberto")
        with k4:
            render_card("💵 Renda", formatar_moeda(ganho_dono), "Livre: " + formatar_moeda(ganho_dono - tot_geral))
            with st.popover("✏️ Alterar Renda", use_container_width=True):
                novo_ganho = st.number_input("Renda Mensal (R$):", value=ganho_dono, step=100.0, format="%.2f", key=f"in_renda_{dono}")
                if st.button("💾 Salvar Renda", type="primary", use_container_width=True, key=f"btn_renda_{dono}"):
                    conn = get_conn()
                    conn.execute("INSERT OR REPLACE INTO ganhos (aba_dono, ganho_mensal) VALUES (?, ?)", (dono, float(novo_ganho)))
                    conn.commit()
                    conn.close()
                    limpar_cache()
                    st.rerun()

        total_registros = len(df_dono)
        limite_atual = st.session_state[chave_limite]
        df_paginado = df_dono.head(limite_atual).copy()

        col_t1, col_t2 = st.columns([1.5, 1])
        col_t1.markdown(f"##### 📋 Contas ({len(df_paginado)}/{total_registros})")
        btn_salvar_tab = col_t2.button("💾 Salvar", type="primary", use_container_width=True, key=f"save_top_{dono}")

        df_prep = df_paginado[["id", "vencimento_dt", "descricao", "categoria", "valor", "status", "forma_pagamento", "responsavel", "observacoes"]].copy()
        df_prep["mes_ref"] = df_prep["vencimento_dt"].apply(formatar_data_abrev)
        df_prep["vencimento_dt"] = df_prep["vencimento_dt"].dt.date
        df_prep["Excluir?"] = False

        altura_livre = max(140, (len(df_prep) + 1) * 36 + 12)

        df_editado = st.data_editor(
            df_prep[["id", "mes_ref", "vencimento_dt", "descricao", "categoria", "valor", "status", "forma_pagamento", "responsavel", "observacoes", "Excluir?"]],
            hide_index=True,
            use_container_width=True,
            height=altura_livre,
            disabled=["id", "mes_ref"],
            column_config={
                "id": None,
                "mes_ref": st.column_config.TextColumn("Data", width="small"),
                "vencimento_dt": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY", required=True),
                "descricao": st.column_config.TextColumn("Descrição", required=True),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=lista_categorias, required=True),
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f", required=True),
                "status": st.column_config.SelectboxColumn("Status", options=lista_status, required=True),
                "forma_pagamento": st.column_config.SelectboxColumn("Pagto", options=lista_formas, required=True),
                "responsavel": st.column_config.SelectboxColumn("Resp.", options=responsaveis_opcoes, required=True),
                "observacoes": st.column_config.TextColumn("Obs"),
                "Excluir?": st.column_config.CheckboxColumn("🗑️", default=False)
            },
            key=f"grid_{dono}_{mes_escolhido}_{limite_atual}"
        )

        if btn_salvar_tab:
            conn = get_conn()
            c = conn.cursor()
            for _, row in df_editado.iterrows():
                rec_id = int(row["id"])
                if row["Excluir?"]:
                    c.execute("DELETE FROM contas WHERE id = ?", (rec_id,))
                else:
                    v_dt = row["vencimento_dt"].strftime("%Y-%m-%d") if pd.notnull(row["vencimento_dt"]) else date.today().strftime("%Y-%m-%d")
                    c.execute("""UPDATE contas SET descricao=?, categoria=?, valor=?, vencimento=?, status=?, forma_pagamento=?, responsavel=?, observacoes=?
                                 WHERE id=?""", (
                        str(row["descricao"]), aplicar_emoji(row["categoria"]), float(row["valor"]), v_dt,
                        str(row["status"]), str(row["forma_pagamento"]), str(row["responsavel"]),
                        "" if pd.isna(row["observacoes"]) else str(row["observacoes"]), rec_id
                    ))
            conn.commit()
            conn.close()
            limpar_cache()
            st.toast("Alterações salvas!", icon="✅")
            st.rerun()

        if total_registros > limite_atual:
            restantes = total_registros - limite_atual
            if st.button(f"🔽 Mais {min(20, restantes)} ({restantes} restantes)", use_container_width=True, key=f"more_{dono}"):
                st.session_state[chave_limite] += 20
                st.rerun()

    secao_crud_contas(dono_atual)

# ==========================================
# 5. INVESTIMENTOS
# ==========================================
elif menu == "📈 Investimentos":
    st.title("📈 Patrimônio & Investimentos")

    @st.fragment
    def secao_investimentos():
        _, df_i_all, _, _ = ler_dados_completos()
        tot_ap = df_i_all["valor_aplicado"].sum() if not df_i_all.empty else 0.0
        tot_sal = df_i_all["saldo_atual"].sum() if not df_i_all.empty else 0.0
        tot_gan = df_i_all["ganho_mes"].sum() if not df_i_all.empty else 0.0
        rent_m = (tot_gan / tot_ap * 100) if tot_ap > 0 else 0.0

        c1, c2 = st.columns(2)
        with c1: render_card("🏦 Saldo Atual", formatar_moeda(tot_sal), "Patrimônio", dark=True)
        with c2: render_card("💰 Aplicado", formatar_moeda(tot_ap), "Investido")

        c3, c4 = st.columns(2)
        with c3: render_card("🚀 Rendimento", formatar_moeda(tot_gan), "Lucro líquido")
        with c4: render_card("📊 Rentabilidade", f"{rent_m:.2f}%", "Retorno")

        with st.popover("➕ Novo Investimento", use_container_width=True):
            with st.form("form_inv_fast", clear_on_submit=True):
                inv_dt = st.date_input("Data", value=date.today())
                inv_pes = st.selectbox("Titular", ["Casal", "Henrique", "Camila"])
                inv_tipo = st.text_input("Tipo (Ex: CDB, Tesouro) *")
                inv_inst = st.text_input("Instituição (Ex: Nubank) *")
                inv_ap = st.number_input("Valor Aplicado (R$)", min_value=0.0, step=100.0)
                inv_sal = st.number_input("Saldo Atual (R$)", min_value=0.0, step=100.0)
                inv_obs = st.text_input("Observações")

                if st.form_submit_button("💾 Salvar Investimento", type="primary", use_container_width=True):
                    if inv_tipo.strip():
                        ganho = inv_sal - inv_ap
                        rent = (ganho / inv_ap * 100) if inv_ap > 0 else 0.0
                        conn = get_conn()
                        conn.execute("""INSERT INTO investimentos (data, mes, pessoa, tipo_investimento, instituicao, valor_aplicado, saldo_atual, ganho_mes, rentabilidade, observacoes)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (inv_dt.strftime("%Y-%m-%d"), inv_dt.strftime("%Y-%m"), inv_pes, inv_tipo.strip(), inv_inst.strip(), inv_ap, inv_sal, ganho, rent, inv_obs.strip()))
                        conn.commit()
                        conn.close()
                        limpar_cache()
                        st.rerun()

        if df_i_all.empty:
            st.info("Sua carteira está vazia. Clique acima para cadastrar!")
        else:
            with st.form("form_edit_inv"):
                ch1, ch2 = st.columns([1.5, 1])
                ch1.markdown("##### 📋 Carteira")
                btn_s_inv = ch2.form_submit_button("💾 Salvar", type="primary", use_container_width=True)

                df_ip = df_i_all[["id", "data_dt", "mes", "pessoa", "tipo_investimento", "instituicao", "valor_aplicado", "saldo_atual", "ganho_mes", "rentabilidade", "observacoes"]].copy()
                df_ip["data_dt"] = df_ip["data_dt"].dt.date
                df_ip["Excluir?"] = False

                df_ie = st.data_editor(
                    df_ip, hide_index=True, use_container_width=True, disabled=["id", "rentabilidade"],
                    column_config={
                        "id": None,
                        "data_dt": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "mes": st.column_config.TextColumn("Mês"),
                        "pessoa": st.column_config.SelectboxColumn("Pessoa", options=["Casal", "Henrique", "Camila"]),
                        "tipo_investimento": st.column_config.TextColumn("Tipo"),
                        "instituicao": st.column_config.TextColumn("Inst."),
                        "valor_aplicado": st.column_config.NumberColumn("Aplicado", format="R$ %.2f"),
                        "saldo_atual": st.column_config.NumberColumn("Atual", format="R$ %.2f"),
                        "ganho_mes": st.column_config.NumberColumn("Ganho", format="R$ %.2f"),
                        "rentabilidade": st.column_config.NumberColumn("Rent. %", format="%.2f%%"),
                        "observacoes": st.column_config.TextColumn("Obs"),
                        "Excluir?": st.column_config.CheckboxColumn("🗑️")
                    }
                )
                if btn_s_inv:
                    conn = get_conn()
                    for _, r in df_ie.iterrows():
                        if r["Excluir?"]:
                            conn.execute("DELETE FROM investimentos WHERE id=?", (int(r["id"]),))
                        else:
                            v_a, s_a, g_m = float(r["valor_aplicado"]), float(r["saldo_atual"]), float(r["ganho_mes"])
                            rt = (g_m / v_a * 100) if v_a > 0 else 0.0
                            conn.execute("""UPDATE investimentos SET data=?, mes=?, pessoa=?, tipo_investimento=?, instituicao=?, valor_aplicado=?, saldo_atual=?, ganho_mes=?, rentabilidade=?, observacoes=? WHERE id=?""",
                                         (r["data_dt"].strftime("%Y-%m-%d"), str(r["mes"]), str(r["pessoa"]), str(r["tipo_investimento"]), str(r["instituicao"]), v_a, s_a, g_m, rt, str(r["observacoes"]), int(r["id"])))
                    conn.commit()
                    conn.close()
                    limpar_cache()
                    st.rerun()

    secao_investimentos()

# ==========================================
# 6. CATEGORIAS & OPÇÕES
# ==========================================
elif menu == "🏷️ Categorias & Opções":
    st.title("🏷️ Configurações")

    for titulo, tipo_p in [("Categorias (com Emoji)", "categoria"), ("Status", "status"), ("Formas de Pagamento", "forma_pagamento")]:
        st.markdown(f"#### {titulo}")
        with st.form(f"add_p_{tipo_p}", clear_on_submit=True):
            nv = st.text_input("Novo item:", placeholder="Ex: Delivery")
            if st.form_submit_button("➕ Adicionar", use_container_width=True) and nv.strip():
                val_f = aplicar_emoji(nv.strip()) if tipo_p == "categoria" else nv.strip()
                conn = get_conn()
                conn.execute("INSERT INTO parametros (tipo, valor) VALUES (?, ?)", (tipo_p, val_f))
                conn.commit()
                conn.close()
                limpar_cache()
                st.rerun()

        df_sub = df_param[df_param["tipo"] == tipo_p][["id", "valor"]].copy()
        df_sub["Excluir?"] = False
        with st.form(f"edit_p_{tipo_p}"):
            df_pe = st.data_editor(
                df_sub, hide_index=True, use_container_width=True,
                column_config={"id": None, "valor": st.column_config.TextColumn("Nome"), "Excluir?": st.column_config.CheckboxColumn("🗑️")}
            )
            if st.form_submit_button("💾 Salvar Lista", use_container_width=True):
                conn = get_conn()
                for _, r in df_pe.iterrows():
                    if r["Excluir?"]:
                        conn.execute("DELETE FROM parametros WHERE id=?", (int(r["id"]),))
                    else:
                        vf = aplicar_emoji(r["valor"]) if tipo_p == "categoria" else str(r["valor"]).strip()
                        conn.execute("UPDATE parametros SET valor=? WHERE id=?", (vf, int(r["id"])))
                conn.commit()
                conn.close()
                limpar_cache()
                st.rerun()