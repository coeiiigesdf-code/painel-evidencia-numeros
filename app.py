# -*- coding: utf-8 -*-
"""
Painel "Evidência em Números" - IGESDF
Reconstrução visual do painel executivo mensal em Streamlit.
"""
import base64
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Evidência em Números — IGESDF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Paleta baseada no modelo original
NAVY = "#1B3A5C"
NAVY_DARK = "#12283F"
TEAL = "#2F9AA6"
ORANGE = "#E2711A"
CARD_BG = "#E7F2F7"
PANEL_BG = "#DCEEF3"
TEXT_MUTED = "#7C8B99"
DONUT_COLORS = ["#1B3A5C", "#3E6FA6", "#7FA8CC", "#B7D3E8", "#5FA6B0"]

MESES_PT = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
            "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

ASSETS = Path(__file__).parent / "assets"
DATA_PATH = Path(__file__).parent / "data" / "dados.json"


def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


LOGO_B64 = img_b64(ASSETS / "logo_igesdf.png") if (ASSETS / "logo_igesdf.png").exists() else None

# Ícones SVG simples (em vez de emoji, evita problemas de renderização/fonte)
def svg_icon(kind, color=None):
    c = color or TEAL
    icons = {
        "coin": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v10M9 9.5a3 2.2 0 0 1 6 0c0 1.4-1.5 2-3 2.5-1.5.5-3 1.1-3 2.5a3 2.2 0 0 0 6 0"/></svg>',
        "handcoin": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><circle cx="9" cy="7" r="4"/><path d="M2 21v-2a5 5 0 0 1 5-5h3a5 5 0 0 1 4.9 4"/><circle cx="18" cy="16" r="4"/></svg>',
        "arrow": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
        "chart": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v9l7 4"/></svg>',
        "stethoscope": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M6 3v6a4 4 0 0 0 8 0V3"/><path d="M18 10v3a6 6 0 0 1-12 0v-2"/><circle cx="19" cy="17" r="2"/></svg>',
        "hospital": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><rect x="4" y="4" width="16" height="17" rx="1"/><path d="M12 8v6M9 11h6"/><path d="M9 21v-3h6v3"/></svg>',
        "grad": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M2 8l10-5 10 5-10 5-10-5z"/><path d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/></svg>',
        "star": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="{c}" stroke="{c}" stroke-width="1"><path d="M12 2l3 6.5 7 .9-5 4.9 1.2 7-6.2-3.4-6.2 3.4 1.2-7-5-4.9 7-.9z"/></svg>',
        "chat": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M21 12a8 8 0 0 1-11.2 7.3L4 21l1.8-5.6A8 8 0 1 1 21 12z"/></svg>',
        "trophy": f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{ORANGE}" stroke-width="2"><path d="M8 4h8v5a4 4 0 0 1-8 0V4z"/><path d="M8 5H4v2a4 4 0 0 0 4 4M16 5h4v2a4 4 0 0 1-4 4"/><path d="M12 13v4M9 21h6M10 17h4v4h-4z"/></svg>',
        "turnover": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><path d="M4 12a8 8 0 0 1 14-5.3M20 4v5h-5"/><path d="M20 12a8 8 0 0 1-14 5.3M4 20v-5h5"/></svg>',
        "people": f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2"><circle cx="9" cy="8" r="3"/><path d="M2 20a7 7 0 0 1 14 0"/><circle cx="18" cy="8" r="2.5"/><path d="M16.5 13a5 5 0 0 1 5.5 5"/></svg>',
    }
    return icons.get(kind, "")

# ----------------------------------------------------------------------
# CSS global
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        .stApp {{ background-color: #FFFFFF; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem; max-width: 1300px; }}

        .top-gradient {{
            height: 6px; width: 100%; border-radius: 3px; margin-bottom: 22px;
            background: linear-gradient(90deg, {TEAL} 0%, #9BC53D 45%, {ORANGE} 100%);
        }}
        .header-row {{ display:flex; justify-content:space-between; align-items:flex-start; }}
        .main-title {{ font-size: 40px; font-weight: 800; color: {NAVY}; margin: 0; line-height:1.1; }}
        .month-box {{
            display:inline-block; margin-top:6px; padding:4px 14px;
            background:{PANEL_BG}; border-radius:8px;
            font-size:20px; font-weight:700; color:{TEAL};
        }}
        .logo-box img {{ height: 88px; object-fit: contain; }}

        .section-title {{
            font-size:14px; font-weight:800; color:{NAVY}; text-transform:none;
            margin: 2px 0 10px 0;
        }}
        .section-title .icon, .kpi-label .icon {{
            display:inline-flex; vertical-align:middle; margin-right: 7px;
            position:relative; top:-1px;
        }}
        .section-title .txt {{ display:inline-block; vertical-align:middle; }}

        @keyframes piscar {{
            0%   {{ opacity: 1; }}
            50%  {{ opacity: 0.45; }}
            100% {{ opacity: 1; }}
        }}
        .destaque-box {{
            animation: piscar 1.6s ease-in-out infinite;
        }}
        .kpi-card {{
            background:{CARD_BG}; border-radius:10px; padding:14px 16px; margin-bottom:12px;
        }}
        .kpi-label {{ font-size:12.5px; color:{NAVY}; font-weight:600; line-height:1.3; display:flex; align-items:center; }}
        .kpi-value {{ font-size:22px; color:{TEAL}; font-weight:800; margin-top:3px; }}
        .kpi-value-sm {{ font-size:18px; color:{NAVY}; font-weight:800; margin-top:2px; }}

        .left-panel {{ background:{PANEL_BG}; border-radius:14px; padding:18px; }}
        .left-panel .kpi-card {{ background:#FFFFFF; }}
        .footnote {{ font-size:10.5px; color:{TEXT_MUTED}; margin-top:10px; line-height:1.4; }}

        .simple-row {{ display:flex; justify-content:space-between; font-size:13px;
                        color:{NAVY}; padding:3px 0; border-bottom:1px solid #EEF3F6; }}
        .simple-row b {{ font-weight:700; }}

        .footer-bar {{
            background:{NAVY}; color:white; text-align:center; padding:10px;
            border-radius:6px; font-size:12px; margin-top:26px;
        }}

        div[data-testid="stSelectbox"] > label {{
            font-weight:700; color:{NAVY}; font-size:13px;
        }}
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color:{PANEL_BG}; border-radius:20px; border:1px solid {TEAL};
            font-weight:700; color:{NAVY};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Carregar dados
# ----------------------------------------------------------------------
# Cole aqui o link da sua Planilha Google publicada como CSV (Arquivo > Compartilhar >
# Publicar na Web > selecione a aba "dados" > formato CSV > Publicar > copie o link).
# Deixe como None para usar só o arquivo local data/dados.json.
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQo-quEAJGTPF_01Di6nL5C3Lzs0oLhpOxoY_QsitaOWoRzbTv0pF_D_P90ED_4wE8Gm_9H23k3DIQy/pub?gid=839282212&single=true&output=csv"
# Exemplo: "https://docs.google.com/spreadsheets/d/SEU_ID/pub?gid=0&single=true&output=csv"

NPS_KEYS = ["hb_oncologia", "hb_hematologia", "hb_amb_hematologia", "hb_amb_oncologia",
            "hb_trauma", "hb_pronto_socorro", "hsol", "hrsm_materno_infantil",
            "hrsm_amb_nao_medico", "hrsm_amb_medico", "upas_media", "upas_porte1",
            "upas_porte3"]


def _nps_from_flat_row(row_dict):
    nps = {}
    for k in NPS_KEYS:
        v = row_dict.get(f"nps_{k}")
        if v is not None and not pd.isna(v):
            nps[k] = float(v)
    dp = row_dict.get("nps_destaque_pct")
    if dp is not None and not pd.isna(dp):
        nps["destaque_pct"] = float(dp)
        nps["destaque_upa"] = row_dict.get("nps_destaque_upa")
    return nps


@st.cache_data(ttl=300)
def load_data():
    if GOOGLE_SHEET_CSV_URL:
        try:
            raw_df = pd.read_csv(GOOGLE_SHEET_CSV_URL, decimal=",", thousands=None)
            registros = raw_df.to_dict(orient="records")
            for r in registros:
                r["nps"] = _nps_from_flat_row(r)
            df = pd.DataFrame(registros)
        except Exception as e:
            st.warning(f"Não consegui ler a Planilha Google ({e}). Usando o arquivo local de reserva.")
            with open(DATA_PATH, encoding="utf-8") as f:
                df = pd.DataFrame(json.load(f))
    else:
        with open(DATA_PATH, encoding="utf-8") as f:
            df = pd.DataFrame(json.load(f))

    df["mes_ano"] = df["ano"].astype(str) + "-" + df["mes_num"].astype(str).str.zfill(2)
    df["rotulo"] = df["mes_nome"] + " " + df["ano"].astype(str)
    df = df.sort_values(["ano", "mes_num"]).reset_index(drop=True)
    return df

df = load_data()

# ----------------------------------------------------------------------
# Cabeçalho + filtro
# ----------------------------------------------------------------------
st.markdown('<div class="top-gradient"></div>', unsafe_allow_html=True)

h_left, h_mid, h_right = st.columns([3, 2, 1])
with h_left:
    st.markdown('<div class="main-title">Evidência em Números</div>', unsafe_allow_html=True)
with h_mid:
    PLACEHOLDER = "— Selecione um mês —"
    opcoes = [PLACEHOLDER] + df["rotulo"].tolist()
    escolha = st.selectbox(
        "Selecione o mês",
        opcoes,
        index=0,
        label_visibility="collapsed",
    )
with h_right:
    if LOGO_B64:
        st.markdown(
            f'<div class="logo-box" style="text-align:right;">'
            f'<img src="data:image/png;base64,{LOGO_B64}"/></div>',
            unsafe_allow_html=True,
        )

if escolha == PLACEHOLDER:
    st.info("👆 Selecione um mês no campo acima para ver os dados do painel.")
    st.stop()

st.markdown(f'<div class="month-box">{escolha}</div>', unsafe_allow_html=True)
st.write("")

row = df[df["rotulo"] == escolha].iloc[0]

# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------
def _to_float(v):
    """Converte v para float com segurança. Aceita texto tipo '144.842.652,86',
    'R$ 140,50', ou já vir como número. Retorna None se não der para converter,
    em vez de quebrar o painel inteiro por causa de uma célula mal digitada."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return None if pd.isna(v) else float(v)
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "none", "—", "-"):
        return None
    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def fmt_money(v):
    v = _to_float(v)
    if v is None:
        return "— (verifique o valor na planilha)"
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(v, casas=2):
    v = _to_float(v)
    if v is None:
        return "—"
    return f"{v*100:.{casas}f}%".replace(".", ",")

def fmt_int(v):
    v = _to_float(v)
    if v is None:
        return "—"
    return f"{int(v):,}".replace(",", ".")

def fmt_dias(v):
    v = _to_float(v)
    if v is None:
        return "—"
    return f"{v:.2f}".replace(".", ",") + " dias"

def kpi(label, value, small=False, icon_kind=None):
    cls = "kpi-value-sm" if small else "kpi-value"
    icon_html = f'<span class="icon">{svg_icon(icon_kind, color=NAVY)}</span>' if icon_kind else ""
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{icon_html}{label}</div>'
        f'<div class="{cls}">{value}</div></div>',
        unsafe_allow_html=True,
    )

def section_title(text, icon_kind=""):
    icon_html = svg_icon(icon_kind, color=NAVY) if icon_kind else ""
    st.markdown(
        f'<div class="section-title"><span class="icon">{icon_html}</span>'
        f'<span class="txt">{text}</span></div>',
        unsafe_allow_html=True,
    )

def simple_row(label, value):
    st.markdown(
        f'<div class="simple-row"><span>{label}</span><b>{value}</b></div>',
        unsafe_allow_html=True,
    )

def donut(labels, values, height=250):
    vals = [_to_float(v) or 0 for v in values]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=vals, hole=0.58,
        marker=dict(colors=DONUT_COLORS, line=dict(color="#FFFFFF", width=2)),
        textinfo="none", sort=False,
    )])
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20), height=height,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def svg_gauge(value, size=140):
    import math
    v = _to_float(value) or 0
    pct = max(0, min(100, v * 100))
    cx, cy, r = size / 2, size * 0.62, size * 0.42
    stroke_w = size * 0.11

    def point(angle_deg):
        a = math.radians(angle_deg)
        return cx + r * math.cos(a), cy - r * math.sin(a)

    x0, y0 = point(180)   # início (esquerda)
    x1, y1 = point(0)     # fim (direita) - trilho completo

    sweep_angle = 180 - (pct / 100) * 180
    xv, yv = point(sweep_angle)
    # o arco nunca passa de 180°, então a flag de "arco grande" é sempre 0
    large_arc = 0

    track_path = f"M {x0:.1f} {y0:.1f} A {r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}"
    value_path = f"M {x0:.1f} {y0:.1f} A {r:.1f} {r:.1f} 0 {large_arc} 1 {xv:.1f} {yv:.1f}"

    pct_txt = f"{pct:.2f}".replace(".", ",")

    return f"""
    <svg width="{size}" height="{size*0.72:.0f}" viewBox="0 0 {size} {size*0.72:.0f}">
        <path d="{track_path}" fill="none" stroke="#DCE6EC" stroke-width="{stroke_w:.1f}" stroke-linecap="round"/>
        <path d="{value_path}" fill="none" stroke="{TEAL}" stroke-width="{stroke_w:.1f}" stroke-linecap="round"/>
        <text x="{cx}" y="{cy - size*0.02:.0f}" text-anchor="middle" font-size="{size*0.155:.0f}"
              font-weight="700" fill="{NAVY}" font-family="sans-serif">{pct_txt}%</text>
    </svg>
    """

def kpi_card_html(label, value, icon_kind=None, bg="#FFFFFF"):
    icon_html = f'<span class="icon">{svg_icon(icon_kind, color=NAVY)}</span>' if icon_kind else ""
    return (
        f'<div class="kpi-card" style="background:{bg};">'
        f'<div class="kpi-label">{icon_html}{label}</div>'
        f'<div class="kpi-value">{value}</div></div>'
    )

def missing_note(fields_labels):
    st.caption("⚠ Não disponível na fonte deste mês: " + ", ".join(fields_labels))

# ----------------------------------------------------------------------
# Linha 1
# ----------------------------------------------------------------------
col_left, col_custo, col_colab, col_turn = st.columns([1.05, 1.25, 1.35, 1.05])

with col_left:
    left_html = (
        '<div class="left-panel">'
        + kpi_card_html("Repasse estimado da SES/DF ao IgesDF", fmt_money(row["repasse_estimado"]), "coin")
        + kpi_card_html("Repasse recebido - Contrato de Gestão", fmt_money(row["repasse_recebido_contrato_gestao"]), "handcoin")
        + kpi_card_html("Total de ingressos", fmt_money(row["total_ingressos"]), "arrow")
        + '<div class="footnote">* Ingressos: repasse + convênios federais; rendimentos; '
          'convênios de pesquisas; convênios de programa de estágios; inscrições/mensalidades '
          'programas de treinamento; receita da biblioteca; 2ª via de documentos '
          '(crachá/estacionamento); estornos de RH; juros recebidos.</div>'
        '</div>'
    )
    st.markdown(left_html, unsafe_allow_html=True)

with col_custo:
    section_title("Custo mensal", "chart")
    labels = ["Custo com pessoal", "Serviços de terceiros", "Material de consumo",
              "Concessionárias", "Despesas gerais"]
    values = [row["custo_pessoal_pct"], row["servicos_terceiros_pct"], row["material_consumo_pct"],
              row["concessionarias_pct"], row["despesas_gerais_pct"]]
    if all(v is None or pd.isna(v) for v in values):
        st.info("Sem dados de custo mensal para este mês.")
    else:
        st.plotly_chart(donut(labels, values, height=230), use_container_width=True,
                         config={"displayModeBar": False})
        for lab, val in zip(labels, values):
            simple_row(lab, fmt_pct(val))

with col_colab:
    section_title("Colaboradores", "people")
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("Total", fmt_int(row["colaboradores_total"]), small=True)
    with c2:
        kpi("Celetista", fmt_int(row["colaboradores_celetista"]), small=True)
    with c3:
        kpi("Estatutário", fmt_int(row["colaboradores_estatutario"]), small=True)

    section_title("Força de Trabalho - Celetista", "people")
    ft_rows = [
        ("Médicos", row.get("ft_medicos")),
        ("Enfermeiros", row.get("ft_enfermeiros")),
        ("Técnicos de enfermagem", row.get("ft_tecnicos_enfermagem")),
        ("Enfermagem (não segmentada)", row.get("ft_enfermagem_geral")),
        ("Multiprofissional", row.get("ft_multiprofissional")),
        ("Administrativo", row.get("ft_administrativo")),
    ]
    for nome, val in ft_rows:
        if val is not None and not pd.isna(val):
            simple_row(nome, fmt_int(val))

with col_turn:
    section_title("Turnover*", "turnover")
    kpi("Turnover geral", fmt_pct(row["turnover_geral_pct"]))
    kpi("Admissões", fmt_int(row["admissoes_geral"]), small=True)
    kpi("Desligamentos", fmt_int(row["desligamentos_geral"]), small=True)
    st.markdown('<div class="footnote">*Taxa de rotatividade dos colaboradores.</div>', unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #E5EBEF;margin:18px 0;'>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Linha 2 — Dados assistenciais | HBDF | HRSM | Eventos
# ----------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    section_title("Dados assistenciais", "stethoscope")
    simple_row("Atendimentos", fmt_int(row["atendimentos"]))
    simple_row("Cirurgias realizadas", fmt_int(row["cirurgias_realizadas"]))

with col2:
    section_title("Hospital de Base", "hospital")
    simple_row("Taxa de ocupação geral", fmt_pct(row["hbdf_taxa_ocupacao_pct"], casas=0))
    simple_row("Média de permanência", fmt_dias(row["hbdf_media_permanencia_dias"]))

with col3:
    section_title("Hospital Regional de Santa Maria", "hospital")
    simple_row("Taxa de ocupação geral", fmt_pct(row["hrsm_taxa_ocupacao_pct"], casas=2))
    simple_row("Média de permanência", fmt_dias(row["hrsm_media_permanencia_dias"]))

with col4:
    section_title("Inovação, Ensino e Pesquisa", "grad")
    simple_row("Temas", fmt_int(row["eventos_temas"]))
    simple_row("Total de participantes", fmt_int(row["eventos_participantes"]))

faltando = []
if _to_float(row["atendimentos"]) is None:
    faltando.append("Atendimentos/Cirurgias")
if _to_float(row["hbdf_taxa_ocupacao_pct"]) is None:
    faltando.append("Ocupação/Permanência HBDF e HRSM")
if faltando:
    missing_note(faltando)

st.markdown("<hr style='border:none;border-top:1px solid #E5EBEF;margin:18px 0;'>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Linha 3 — NPS por unidade | Ouvidoria
# ----------------------------------------------------------------------
col_nps, col_ouv = st.columns([2.3, 1])

with col_nps:
    section_title("Satisfação do usuário", "star")
    st.caption(
        "**Net Promoter Score (NPS):** indicador de satisfação dos usuários com os "
        "serviços de saúde, apurado por média mensal por unidade."
    )
    nps = row.get("nps") or {}
    nps_labels = {
        "hb_oncologia": "HBDF · Centro de Infusão Oncologia",
        "hb_hematologia": "HBDF · Centro de Infusão Hematologia",
        "hb_amb_hematologia": "HBDF · Ambulatório Hematologia",
        "hb_amb_oncologia": "HBDF · Ambulatório Oncologia",
        "hb_trauma": "HBDF · Trauma",
        "hb_pronto_socorro": "HBDF · Pronto Socorro",
        "hsol": "HSol",
        "hrsm_materno_infantil": "HRSM · Linha Materno-Infantil",
        "hrsm_amb_nao_medico": "HRSM · Ambulatório não médico",
        "hrsm_amb_medico": "HRSM · Ambulatório médico",
        "upas_media": "UPAs · Média geral (13 UPAs)",
        "upas_porte1": "UPAs · Porte I (média)",
        "upas_porte3": "UPAs · Porte III (média)",
    }
    itens = [(nps_labels[k], v) for k, v in nps.items() if k in nps_labels and v is not None]
    if not itens:
        st.info("NPS por unidade não disponível para este mês nesta fonte.")
    else:
        n_cols = 6
        for i in range(0, len(itens), n_cols):
            chunk = itens[i:i + n_cols]
            gcols = st.columns(n_cols)
            for gc, (label, val) in zip(gcols, chunk):
                with gc:
                    st.markdown(
                        f'<div style="text-align:center;">{svg_gauge(val)}'
                        f'<div style="font-size:11px;color:{NAVY};font-weight:700;'
                        f'margin-top:2px;">{label}</div></div>',
                        unsafe_allow_html=True,
                    )

    if nps.get("destaque_pct"):
        st.markdown(
            f"""
            <div style="text-align:center;margin-top:18px;">
                <div class="destaque-box" style="background:{PANEL_BG};border-radius:12px;
                            padding:18px 28px;display:inline-block;text-align:center;min-width:220px;">
                    <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
                        {svg_icon('trophy')}
                        <b style="color:{NAVY};font-size:16px;">Destaque do mês</b>
                    </div>
                    <div style="color:{NAVY};font-weight:700;font-size:16px;margin-top:4px;">
                        {nps.get('destaque_upa', '')}
                    </div>
                    <div style="color:{TEAL};font-weight:800;font-size:28px;margin-top:4px;">
                        {fmt_pct(nps['destaque_pct'])}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_ouv:
    section_title("Ouvidoria", "chat")
    ouv_labels = ["Reclamação", "Elogio", "Denúncia", "Solicitação", "Sugestão"]
    ouv_values = [row.get("ouv_reclamacao_pct"), row.get("ouv_elogio_pct"), row.get("ouv_denuncia_pct"),
                  row.get("ouv_solicitacao_pct"), row.get("ouv_sugestao_pct")]
    if all(v is None or pd.isna(v) for v in ouv_values):
        st.info("Ouvidoria não disponível para este mês nesta fonte.")
    else:
        st.plotly_chart(donut(ouv_labels, ouv_values, height=260), use_container_width=True,
                         config={"displayModeBar": False})
        for lab, val in zip(ouv_labels, ouv_values):
            simple_row(lab, fmt_pct(val, casas=2))

st.markdown(
    '<div class="footer-bar">COEII - Coordenação Estratégica de Informação Institucional</div>',
    unsafe_allow_html=True,
)
