import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import date, timedelta
import io

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E CSS PRO UI
# ==========================================
st.set_page_config(page_title="Diviapp Pro", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F4F7FE; }
    
    /* Cards Executivos */
    .pro-card {
        background: white;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EEF2F6;
        margin-bottom: 12px;
    }
    .pro-card-dark {
        background: linear-gradient(135deg, #1E2A4F 0%, #2A3F75 100%);
        color: white;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 8px 24px rgba(30, 42, 79, 0.18);
        margin-bottom: 12px;
    }
    .card-label { font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.75; margin-bottom: 6px; }
    .card-value { font-size: 1.65rem; font-weight: 700; margin: 0; line-height: 1.2; }
    .card-sub { font-size: 0.8rem; margin-top: 8px; opacity: 0.85; }
    
    /* Badges de Status */
    .badge-ok { background: #DEF7EC; color: #03543F; padding: 3px 10px; border-radius: 99px; font-weight: 600; font-size: 0.75rem; }
    .badge-warn { background: #FEF3C7; color: #92400E; padding: 3px 10px; border-radius: 99px; font-weight: 600; font-size: 0.75rem; }
    .badge-danger { background: #FDE8E8; color: #9B1C1C; padding: 3px 10px; border-radius: 99px; font-weight: 600; font-size: 0.75rem; }
    
    /* Títulos e Divisores */
    h1, h2, h3 { color: #1E2A4F !important; font-weight: 700 !important; letter-spacing: -0.3px; }
    div[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "diviapp_pro.db"
EXCEL_PADRAO = "controle_financeiro - HENRIQUE E CAMILA_2.xlsx"
EXCEL_ALT = "controle_financeiro - HENRIQUE E CAMILA.xlsx"

# ==========================================
# MAPA DE EMOJIS INTELIGENTE PARA CATEGORIAS
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
    # Se já começa com emoji, mantém como está
    if any(ord(char) > 10000 for char in texto[:2]):
        return texto
    chave = texto.lower()
    for k, emj in EMOJI_MAP.items():
        if k in chave:
            return f"{emj} {texto}"
    return f"🏷️ {texto}"

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==========================================
# BANCO DE DADOS E CACHE DE ALTA PERFORMANCE
# ==========================================
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def inicializar_banco():
    if os.path.exists(DB_FILE):
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
    else:
        df_c["vencimento_dt"] = pd.Series(dtype="datetime64[ns]")
        df_c["mes_ano"] = pd.Series(dtype="str")

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

ganhos_dict = dict(zip(df_ganhos["aba_dono"], df_ganhos["ganho_mensal"]))
ganho_h = float(ganhos_dict.get("Henrique", 3985.0))
ganho_c = float(ganhos_dict.get("Camila", 2860.0))

# ==========================================
# SIDEBAR COM LOGO COMPACTA
# ==========================================
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=110)
        elif os.path.exists("input_file_0.png"):
            st.image("input_file_0.png", width=110)
        else:
            st.markdown("<h2 style='text-align:center; margin:0;'>🌱</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; font-weight:700; color:#1E2A4F; margin-top:-5px; margin-bottom:15px;'>Diviapp • Henrique & Camila</p>", unsafe_allow_html=True)

    menu = st.radio(
        "Navegação",
        [
            "🚀 Visão Geral (Dashboard)",
            "📅 Resumo Mensal",
            "🧔🏻 Contas Henrique",
            "👩🏻 Contas Camila",
            "📈 Investimentos",
            "🏷️ Categorias & Opções"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    with st.expander("💾 Backup & Exportar Excel"):
        st.caption("Gere a planilha atualizada apenas quando desejar baixar.")
        if st.button("Preparar Arquivo Excel", use_container_width=True):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_contas[df_contas["aba_dono"] == "Henrique"].to_excel(writer, sheet_name="Contas do Mês Henrique", index=False)
                df_contas[df_contas["aba_dono"] == "Camila"].to_excel(writer, sheet_name="Contas do Mês Camila", index=False)
                df_inv.to_excel(writer, sheet_name="Investimentos", index=False)
            st.download_button(
                "📥 Clique para Baixar (.xlsx)",
                data=output.getvalue(),
                file_name=f"Diviapp_{date.today().strftime('%Y_%m_%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        if st.button("🔄 Resetar p/ Planilha Original", use_container_width=True):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            limpar_cache()
            st.rerun()

# ==========================================
# 1. DASHBOARD EXECUTIVO (TUDO VISÍVEL POR PADRÃO)
# ==========================================
if menu == "🚀 Visão Geral (Dashboard)":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.title("🚀 Visão Geral Financeira")
        st.caption("Todas as informações consolidadas do casal estão visíveis por padrão.")
    
    # Filtro opcional recolhido para não esconder nada por padrão
    df_dash = df_contas.copy()
    df_inv_dash = df_inv.copy()
    
    with st.expander("🔍 Filtrar por Mês, Período ou Pessoa (Opcional - Padrão: Tudo Visível)", expanded=False):
        f1, f2, f3 = st.columns(3)
        meses_disp = sorted(df_contas["mes_ano"].dropna().unique().tolist())
        with f1:
            tipo_f = st.selectbox("Modo de Filtro:", ["Mostrar Tudo (Padrão)", "Selecionar Mês(es)", "Intervalo de Datas"])
        with f2:
            if tipo_f == "Selecionar Mês(es)":
                m_sel = st.multiselect("Meses:", meses_disp, default=meses_disp)
                df_dash = df_dash[df_dash["mes_ano"].isin(m_sel)]
            elif tipo_f == "Intervalo de Datas" and not df_contas.empty:
                d_min, d_max = df_contas["vencimento_dt"].min().date(), df_contas["vencimento_dt"].max().date()
                per = st.date_input("Período:", value=(d_min, d_max))
                if isinstance(per, tuple) and len(per) == 2:
                    df_dash = df_dash[(df_dash["vencimento_dt"].dt.date >= per[0]) & (df_dash["vencimento_dt"].dt.date <= per[1])]
        with f3:
            p_sel = st.multiselect("Pessoa:", ["Henrique", "Camila"], default=["Henrique", "Camila"])
            df_dash = df_dash[df_dash["aba_dono"].isin(p_sel)]

    # Cálculos Executivos Prioritários
    total_geral = df_dash["valor"].sum()
    total_pago = df_dash[df_dash["status"].str.lower() == "pago"]["valor"].sum()
    total_pendente = df_dash[df_dash["status"].str.lower() == "pendente"]["valor"].sum()
    total_atrasado = df_dash[df_dash["status"].str.lower() == "atrasado"]["valor"].sum()
    total_h = df_dash[df_dash["aba_dono"] == "Henrique"]["valor"].sum()
    total_c = df_dash[df_dash["aba_dono"] == "Camila"]["valor"].sum()
    patrimonio = df_inv_dash["saldo_atual"].sum() if not df_inv_dash.empty else 0.0
    perc_quitado = (total_pago / total_geral * 100) if total_geral > 0 else 0.0

    # 1º DESTAQUE: O QUE IMPORTA PRIMEIRO (CARDS PRO)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_card("💰 Total Movimentado", formatar_moeda(total_geral), f"🧔🏻 H: {formatar_moeda(total_h)} | 👩🏻 C: {formatar_moeda(total_c)}", dark=True)
    with c2:
        render_card("✅ Total Quitado", formatar_moeda(total_pago), f"<span class='badge-ok'>{perc_quitado:.1f}% pago do total</span>")
    with c3:
        render_card("⏳ Falta Pagar (Pendente)", formatar_moeda(total_pendente), f"<span class='badge-warn'>{len(df_dash[df_dash['status'].str.lower()=='pendente'])} contas em aberto</span>")
    with c4:
        render_card("🚨 Atrasado + 📈 Investido", formatar_moeda(total_atrasado), f"Patrimônio: <b>{formatar_moeda(patrimonio)}</b>")

    # Barra de progresso de quitação
    st.progress(min(perc_quitado / 100.0, 1.0), text=f"Progresso de Quitação Geral das Contas: {perc_quitado:.1f}%")

    # 2º DESTAQUE: ALERTAS DE CONTAS PENDENTES / ATRASADAS MAIS IMPORTANTES
    df_alertas = df_dash[df_dash["status"].str.lower().isin(["atrasado", "pendente"])].sort_values(by="vencimento_dt")
    if not df_alertas.empty:
        st.markdown("### 🔔 Atenção Imediata: Próximas Contas a Pagar")
        cols_alerta = st.columns(min(4, len(df_alertas)))
        for idx, (_, row_al) in enumerate(df_alertas.head(4).iterrows()):
            with cols_alerta[idx]:
                cor_borda = "#EF4444" if str(row_al["status"]).lower() == "atrasado" else "#F59E0B"
                venc_fmt = row_al["vencimento_dt"].strftime("%d/%m/%Y") if pd.notnull(row_al["vencimento_dt"]) else "-"
                st.markdown(f"""
                    <div style="background:white; border-left: 5px solid {cor_borda}; padding: 14px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                        <div style="font-size:0.75rem; color:#64748B; font-weight:600;">{row_al['aba_dono']} • Vence {venc_fmt}</div>
                        <div style="font-size:1rem; font-weight:700; color:#1E2A4F; margin:4px 0;">{row_al['descricao']}</div>
                        <div style="font-size:0.85rem; color:#475569;">{row_al['categoria']}</div>
                        <div style="font-size:1.15rem; font-weight:700; color:{cor_borda}; margin-top:6px;">{formatar_moeda(row_al['valor'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3º DESTAQUE: GRÁFICOS VISUAIS LIMPOS
    if not df_dash.empty:
        g1, g2 = st.columns([1.4, 1])
        with g1:
            st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
            st.subheader("📊 Para onde vai o dinheiro? (Por Categoria)")
            df_cat_g = df_dash.groupby("categoria", as_index=False)["valor"].sum().sort_values(by="valor", ascending=True)
            fig_cat = px.bar(
                df_cat_g, x="valor", y="categoria", orientation="h", text_auto=".2s",
                color="valor", color_continuous_scale=["#60A5FA", "#1E2A4F"]
            )
            fig_cat.update_layout(showlegend=False, height=380, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with g2:
            st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
            st.subheader("⚖️ Evolução Mensal (Henrique vs Camila)")
            df_ev = df_dash.groupby(["mes_ano", "aba_dono"], as_index=False)["valor"].sum().sort_values("mes_ano")
            fig_ev = px.bar(
                df_ev, x="mes_ano", y="valor", color="aba_dono", barmode="group", text_auto=".2s",
                color_discrete_map={"Henrique": "#1E2A4F", "Camila": "#EC4899"}
            )
            fig_ev.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="rgba(0,0,0,0)", legend_title_text="")
            st.plotly_chart(fig_ev, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. RESUMO MENSAL (MODERNO E SEM FILTRO PRÉVIO)
# ==========================================
elif menu == "📅 Resumo Mensal":
    st.title("📅 Resumo Mensal Inteligente")
    st.caption("Visão panorâmica de todos os meses lado a lado sem cara de planilha.")

    meses_todos = sorted(df_contas["mes_ano"].dropna().unique().tolist())
    
    # Cards de cada mês em destaque no topo
    cols_mes = st.columns(max(1, len(meses_todos)))
    for i, m in enumerate(meses_todos):
        df_m = df_contas[df_contas["mes_ano"] == m]
        tot_m = df_m["valor"].sum()
        pago_m = df_m[df_m["status"].str.lower() == "pago"]["valor"].sum()
        pend_m = tot_m - pago_m
        perc_m = (pago_m / tot_m * 100) if tot_m > 0 else 0.0
        with cols_mes[i]:
            render_card(
                f"🗓️ Mês {m}",
                formatar_moeda(tot_m),
                f"✅ Pago: {formatar_moeda(pago_m)} ({perc_m:.0f}%)<br>⏳ Falta: <b>{formatar_moeda(pend_m)}</b>"
            )

    st.markdown("### 🏷️ Comparativo de Categorias em Todos os Meses")
    if not df_contas.empty:
        piv_cat = df_contas.pivot_table(index="categoria", columns="mes_ano", values="valor", aggfunc="sum", fill_value=0.0)
        piv_cat["Total Geral"] = piv_cat.sum(axis=1)
        piv_cat = piv_cat.sort_values(by="Total Geral", ascending=False).reset_index()
        
        col_cfg = {"categoria": st.column_config.TextColumn("Categoria")}
        for c_name in piv_cat.columns:
            if c_name != "categoria":
                col_cfg[c_name] = st.column_config.NumberColumn(c_name, format="R$ %.2f")

        st.dataframe(piv_cat, column_config=col_cfg, use_container_width=True, hide_index=True)

# ==========================================
# 3 e 4. CONTAS HENRIQUE E CAMILA (CRUD RÁPIDO COM @st.fragment)
# ==========================================
elif menu in ["🧔🏻 Contas Henrique", "👩🏻 Contas Camila"]:
    dono_atual = "Henrique" if "Henrique" in menu else "Camila"
    icone = "🧔🏻" if dono_atual == "Henrique" else "👩🏻"

    st.title(f"{icone} Central de Contas — {dono_atual}")

    @st.fragment
    def secao_crud_contas(dono):
        df_c_all, _, _, df_g_all = ler_dados_completos()
        df_dono = df_c_all[df_c_all["aba_dono"] == dono].sort_values(by="vencimento_dt", ascending=False).copy()
        ganho_dono = float(dict(zip(df_g_all["aba_dono"], df_g_all["ganho_mensal"])).get(dono, 0.0))

        # KPIs no Topo (Todas as contas visíveis por padrão)
        tot_geral = df_dono["valor"].sum()
        tot_pago = df_dono[df_dono["status"].str.lower() == "pago"]["valor"].sum()
        tot_pend = df_dono[df_dono["status"].str.lower().isin(["pendente", "atrasado"])]["valor"].sum()

        k1, k2, k3, k4 = st.columns(4)
        with k1: render_card(f"Total Lançado ({dono})", formatar_moeda(tot_geral), f"{len(df_dono)} lançamentos", dark=True)
        with k2: render_card("✅ Total Pago", formatar_moeda(tot_pago), "Contas quitadas")
        with k3: render_card("⏳ Pendente / Atrasado", formatar_moeda(tot_pend), "Aguardando pagamento")
        with k4: render_card("💵 Renda Base Mensal", formatar_moeda(ganho_dono), "Configurada na planilha")

        # Barra de Ações Rápidas: Novo Lançamento + Filtro Opcional
        col_act1, col_act2 = st.columns([1.2, 2])
        with col_act1:
            with st.popover(f"➕ Nova Conta para {dono}", use_container_width=True):
                with st.form(f"form_rapido_{dono}", clear_on_submit=True):
                    st.markdown(f"**Nova Conta ({dono})**")
                    in_desc = st.text_input("Descrição *", placeholder="Ex: Aluguel, Internet...")
                    c_f1, c_f2 = st.columns(2)
                    in_cat = c_f1.selectbox("Categoria", lista_categorias)
                    in_val = c_f2.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
                    c_f3, c_f4 = st.columns(2)
                    in_venc = c_f3.date_input("Vencimento", value=date.today())
                    in_stat = c_f4.selectbox("Status", lista_status)
                    c_f5, c_f6 = st.columns(2)
                    in_forma = c_f5.selectbox("Pagamento", lista_formas)
                    in_resp = c_f6.selectbox("Responsável", responsaveis_opcoes, index=responsaveis_opcoes.index(dono))
                    in_obs = st.text_input("Observações")

                    if st.form_submit_button("💾 Salvar Agora", type="primary", use_container_width=True):
                        if in_desc.strip():
                            conn = get_conn()
                            conn.execute("""INSERT INTO contas (aba_dono, descricao, categoria, valor, vencimento, status, forma_pagamento, responsavel, observacoes)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                         (dono, in_desc.strip(), in_cat, in_val, in_venc.strftime("%Y-%m-%d"), in_stat, in_forma, in_resp, in_obs.strip()))
                            conn.commit()
                            conn.close()
                            limpar_cache()
                            st.rerun()

        with col_act2:
            busca = st.text_input("🔎 Busca rápida por descrição, categoria ou mês (Ex: 2026-11, Moradia, Nubank):", placeholder="Digite para filtrar instantaneamente ou deixe vazio para ver tudo...", label_visibility="collapsed")

        if busca.strip():
            termo = busca.strip().lower()
            df_dono = df_dono[
                df_dono["descricao"].str.lower().str.contains(termo, na=False) |
                df_dono["categoria"].str.lower().str.contains(termo, na=False) |
                df_dono["mes_ano"].str.lower().str.contains(termo, na=False) |
                df_dono["status"].str.lower().str.contains(termo, na=False)
            ]

        # Editor de Dados Otimizado dentro de um Form para NÃO recarregar a cada clique na célula
        with st.form(f"form_tabela_{dono}"):
            col_h1, col_h2 = st.columns([3, 1])
            col_h1.markdown("##### 📋 Lista Completa de Contas (Edite direto na tabela)")
            btn_salvar_tab = col_h2.form_submit_button("💾 Salvar Edições / Exclusões", type="primary", use_container_width=True)

            df_prep = df_dono[["id", "descricao", "categoria", "valor", "vencimento_dt", "status", "forma_pagamento", "responsavel", "observacoes"]].copy()
            df_prep["vencimento_dt"] = df_prep["vencimento_dt"].dt.date
            df_prep["Excluir?"] = False

            df_editado = st.data_editor(
                df_prep,
                hide_index=True,
                use_container_width=True,
                disabled=["id"],
                column_config={
                    "id": None,
                    "descricao": st.column_config.TextColumn("Descrição", required=True),
                    "categoria": st.column_config.SelectboxColumn("Categoria", options=lista_categorias, required=True),
                    "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f", required=True),
                    "vencimento_dt": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY", required=True),
                    "status": st.column_config.SelectboxColumn("Status", options=lista_status, required=True),
                    "forma_pagamento": st.column_config.SelectboxColumn("Forma Pagto", options=lista_formas, required=True),
                    "responsavel": st.column_config.SelectboxColumn("Responsável", options=responsaveis_opcoes, required=True),
                    "observacoes": st.column_config.TextColumn("Observações"),
                    "Excluir?": st.column_config.CheckboxColumn("🗑️ Excluir", default=False)
                },
                key=f"grid_{dono}"
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
                st.toast("Alterações salvas instantaneamente!", icon="✅")
                st.rerun()

    secao_crud_contas(dono_atual)

# ==========================================
# 5. INVESTIMENTOS (TODOS VISÍVEIS + CRUD RÁPIDO)
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

        c1, c2, c3, c4 = st.columns(4)
        with c1: render_card("🏦 Saldo Atual Acumulado", formatar_moeda(tot_sal), "Patrimônio Total", dark=True)
        with c2: render_card("💰 Total Aplicado", formatar_moeda(tot_ap), "Saído do bolso")
        with c3: render_card("🚀 Rendimento Acumulado", formatar_moeda(tot_gan), "Lucro líquido")
        with c4: render_card("📊 Rentabilidade Geral", f"{rent_m:.2f}%", "Rendimento sobre aplicado")

        with st.popover("➕ Cadastrar Novo Investimento", use_container_width=False):
            with st.form("form_inv_fast", clear_on_submit=True):
                c_i1, c_i2 = st.columns(2)
                inv_dt = c_i1.date_input("Data", value=date.today())
                inv_pes = c_i2.selectbox("Titular", ["Casal", "Henrique", "Camila"])
                inv_tipo = c_i1.text_input("Tipo (Ex: CDB, Tesouro, Caixinha) *")
                inv_inst = c_i2.text_input("Instituição (Ex: Nubank, XP, Inter) *")
                inv_ap = c_i1.number_input("Valor Aplicado (R$)", min_value=0.0, step=100.0)
                inv_sal = c_i2.number_input("Saldo Atual (R$)", min_value=0.0, step=100.0)
                inv_obs = st.text_input("Observações")

                if st.form_submit_button("💾 Adicionar Investimento", type="primary", use_container_width=True):
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
            st.info("Sua carteira ainda está vazia. Clique em **➕ Cadastrar Novo Investimento** acima para começar!")
        else:
            with st.form("form_edit_inv"):
                ch1, ch2 = st.columns([3, 1])
                ch1.markdown("##### 📋 Carteira Completa de Investimentos")
                btn_s_inv = ch2.form_submit_button("💾 Salvar Carteira", type="primary", use_container_width=True)

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
                        "tipo_investimento": st.column_config.TextColumn("Tipo de Investimento"),
                        "instituicao": st.column_config.TextColumn("Instituição"),
                        "valor_aplicado": st.column_config.NumberColumn("Valor Aplicado", format="R$ %.2f"),
                        "saldo_atual": st.column_config.NumberColumn("Saldo Atual", format="R$ %.2f"),
                        "ganho_mes": st.column_config.NumberColumn("Ganho no Mês", format="R$ %.2f"),
                        "rentabilidade": st.column_config.NumberColumn("Rentabilidade %", format="%.2f%%"),
                        "observacoes": st.column_config.TextColumn("Observações"),
                        "Excluir?": st.column_config.CheckboxColumn("🗑️ Excluir")
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
# 6. CATEGORIAS COM EMOJIS & CONFIGURAÇÕES
# ==========================================
elif menu == "🏷️ Categorias & Opções":
    st.title("🏷️ Personalizar Categorias & Pagamentos")
    st.caption("Ao criar uma nova categoria, você pode colocar um emoji ou deixar que o Diviapp adicione automaticamente.")

    col1, col2, col3 = st.columns(3)
    for col, titulo, tipo_p in [(col1, "Categorias (com Emoji)", "categoria"), (col2, "Status", "status"), (col3, "Formas de Pagamento", "forma_pagamento")]:
        with col:
            st.markdown(f"#### {titulo}")
            with st.form(f"add_p_{tipo_p}", clear_on_submit=True):
                nv = st.text_input("Adicionar item:", placeholder="Ex: 🍕 Delivery")
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