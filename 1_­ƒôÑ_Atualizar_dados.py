# -*- coding: utf-8 -*-
"""
Página de cadastro/atualização mensal do painel Evidência em Números.
Preencha o formulário e clique em Salvar — o arquivo data/dados.json
é atualizado automaticamente (cria o mês se não existir, ou substitui
os valores se o mês já existir).
"""
import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Atualizar dados — Evidência em Números", page_icon="📥", layout="wide")

DATA_PATH = Path(__file__).parent.parent / "data" / "dados.json"
MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
            "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
MES_NUM = {m: i + 1 for i, m in enumerate(MESES_PT)}


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_num(s):
    """Converte texto tipo '144.842.652,86' ou '141034659.62' em float. Vazio -> None."""
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    s = s.replace(".", "").replace(",", ".") if "," in s else s
    try:
        return float(s)
    except ValueError:
        try:
            return float(str(s).replace(",", "."))
        except ValueError:
            return None


def parse_int(s):
    v = parse_num(s)
    return int(v) if v is not None else None


def parse_pct(s):
    """Digite o número como aparece no relatório (ex: 63,14 para 63,14%). Vazio -> None."""
    v = parse_num(s)
    return v / 100 if v is not None else None


def parse_nps_block(text):
    """Cada linha 'Rótulo: valor' vira uma entrada no dicionário de NPS. Valor em % (ex: 90,35)."""
    result = {}
    for linha in text.splitlines():
        if ":" not in linha:
            continue
        rotulo, valor = linha.split(":", 1)
        v = parse_pct(valor)
        if v is not None:
            chave = rotulo.strip().lower().replace(" ", "_")
            result[chave] = v
    return result


st.title("📥 Atualizar dados do painel")

st.info(
    "**Se o painel principal estiver configurado para ler de uma Planilha Google** "
    "(veja `GOOGLE_SHEET_CSV_URL` no topo do arquivo `app.py`), edite os dados "
    "direto na planilha — é mais simples e não precisa do GitHub. Esta página "
    "aqui edita o arquivo local `data/dados.json`, útil para testar offline ou "
    "para quem não usa a Planilha Google.",
    icon="💡",
)
st.caption(
    "Preencha os campos do mês que você quer adicionar ou corrigir. "
    "Campos deixados em branco ficam marcados como 'não disponível' no painel — "
    "não precisa preencher tudo se algum número ainda não estiver fechado."
)

data = load_data()
existentes = {(d["ano"], d["mes_num"]): d for d in data}

st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    mes_nome = st.selectbox("Mês", MESES_PT)
with col_b:
    ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2026, step=1)

mes_num = MES_NUM[mes_nome]
ja_existe = (int(ano), mes_num) in existentes
if ja_existe:
    st.warning(
        f"⚠ Já existe um registro para **{mes_nome}/{int(ano)}**. "
        "Salvar vai SUBSTITUIR os valores atuais desse mês."
    )

with st.form("form_mes"):
    st.subheader("💰 Financeiro")
    c1, c2, c3 = st.columns(3)
    repasse_estimado = c1.text_input("Repasse estimado SES/DF (R$)", placeholder="144.842.652,86")
    repasse_recebido = c2.text_input("Repasse recebido - Contrato de Gestão (R$)", placeholder="140.148.902,86")
    total_ingressos = c3.text_input("Total de ingressos (R$)", placeholder="141.034.659,62")

    st.markdown("**Custo mensal (em %, como aparece no relatório)**")
    c1, c2, c3, c4, c5 = st.columns(5)
    custo_pessoal = c1.text_input("Custo com pessoal", placeholder="63,14")
    servicos_terceiros = c2.text_input("Serviços de terceiros", placeholder="23,28")
    material_consumo = c3.text_input("Material de consumo", placeholder="11,85")
    concessionarias = c4.text_input("Concessionárias", placeholder="0,67")
    despesas_gerais = c5.text_input("Despesas gerais", placeholder="1,06")

    st.markdown("---")
    st.subheader("👥 Colaboradores e Força de Trabalho")
    c1, c2, c3 = st.columns(3)
    colaboradores_total = c1.text_input("Colaboradores - Total", placeholder="12.007")
    colaboradores_celetista = c2.text_input("Celetista", placeholder="11.509")
    colaboradores_estatutario = c3.text_input("Estatutário", placeholder="498")

    st.caption("Preencha 'Enfermeiros' + 'Técnicos de enfermagem' SEPARADOS, OU 'Enfermagem (não segmentada)' junto — não os dois.")
    c1, c2, c3, c4, c5 = st.columns(5)
    ft_medicos = c1.text_input("Médicos", placeholder="1.920")
    ft_enfermeiros = c2.text_input("Enfermeiros", placeholder="1.542")
    ft_tecnicos = c3.text_input("Técnicos de enfermagem", placeholder="3.817")
    ft_enfermagem_geral = c4.text_input("Enfermagem (não segmentada)", placeholder="")
    ft_multiprofissional = c5.text_input("Multiprofissional", placeholder="2.620")
    ft_administrativo = st.text_input("Administrativo", placeholder="1.610")

    st.markdown("**Rotatividade**")
    c1, c2, c3 = st.columns(3)
    turnover = c1.text_input("Turnover geral (%)", placeholder="1,26")
    admissoes = c2.text_input("Admissões", placeholder="141")
    desligamentos = c3.text_input("Desligamentos", placeholder="137")

    st.markdown("---")
    st.subheader("🩺 Dados assistenciais")
    c1, c2 = st.columns(2)
    atendimentos = c1.text_input("Atendimentos", placeholder="163.419")
    cirurgias = c2.text_input("Cirurgias realizadas", placeholder="2.184")

    st.markdown("**Hospital de Base (HBDF)**")
    c1, c2 = st.columns(2)
    hbdf_ocupacao = c1.text_input("Taxa de ocupação geral HBDF (%)", placeholder="90")
    hbdf_permanencia = c2.text_input("Média de permanência HBDF (dias)", placeholder="13,13")

    st.markdown("**Hospital Regional de Santa Maria (HRSM)**")
    c1, c2 = st.columns(2)
    hrsm_ocupacao = c1.text_input("Taxa de ocupação geral HRSM (%)", placeholder="91,96")
    hrsm_permanencia = c2.text_input("Média de permanência HRSM (dias)", placeholder="7,55")

    st.markdown("---")
    st.subheader("🎓 Eventos educativos")
    c1, c2 = st.columns(2)
    eventos_temas = c1.text_input("Temas abordados", placeholder="39")
    eventos_participantes = c2.text_input("Total de participantes", placeholder="1.928")

    st.markdown("---")
    st.subheader("💬 Ouvidoria (em %)")
    c1, c2, c3, c4, c5 = st.columns(5)
    ouv_reclamacao = c1.text_input("Reclamação", placeholder="81,9")
    ouv_elogio = c2.text_input("Elogio", placeholder="11,8")
    ouv_denuncia = c3.text_input("Denúncia", placeholder="3,8")
    ouv_solicitacao = c4.text_input("Solicitação", placeholder="2,5")
    ouv_sugestao = c5.text_input("Sugestão", placeholder="0,05")

    st.markdown("---")
    st.subheader("⭐ NPS por unidade (opcional)")
    st.caption(
        "Uma linha por unidade, formato **Rótulo: valor em %**. Exemplo:\n\n"
        "```\nhb_oncologia: 90,35\nhb_hematologia: 93,75\nhsol: 79,07\n```\n"
        "Use os mesmos rótulos de outros meses para manter consistência "
        "(hb_oncologia, hb_hematologia, hb_amb_hematologia, hb_amb_oncologia, "
        "hb_trauma, hb_pronto_socorro, hsol, hrsm_materno_infantil, "
        "hrsm_amb_nao_medico, hrsm_amb_medico, upas_porte1, upas_porte3, upas_media)."
    )
    nps_texto = st.text_area("NPS (uma linha por unidade)", height=150, placeholder="hb_oncologia: 90,35\nhsol: 79,07")
    c1, c2 = st.columns(2)
    destaque_upa = c1.text_input("Destaque do mês - nome da UPA", placeholder="UPA Planaltina")
    destaque_pct = c2.text_input("Destaque do mês - NPS (%)", placeholder="89,64")

    st.markdown("---")
    submitted = st.form_submit_button("💾 Salvar mês", use_container_width=True, type="primary")

if submitted:
    nps_dict = parse_nps_block(nps_texto)
    if destaque_pct:
        nps_dict["destaque_pct"] = parse_pct(destaque_pct)
        nps_dict["destaque_upa"] = destaque_upa.strip()

    novo_registro = {
        "ano": int(ano),
        "mes_num": mes_num,
        "mes_nome": mes_nome,
        "fonte": "cadastro_manual",
        "repasse_estimado": parse_num(repasse_estimado),
        "repasse_recebido_contrato_gestao": parse_num(repasse_recebido),
        "total_ingressos": parse_num(total_ingressos),
        "custo_pessoal_pct": parse_pct(custo_pessoal),
        "servicos_terceiros_pct": parse_pct(servicos_terceiros),
        "material_consumo_pct": parse_pct(material_consumo),
        "concessionarias_pct": parse_pct(concessionarias),
        "despesas_gerais_pct": parse_pct(despesas_gerais),
        "colaboradores_total": parse_int(colaboradores_total),
        "colaboradores_celetista": parse_int(colaboradores_celetista),
        "colaboradores_estatutario": parse_int(colaboradores_estatutario),
        "ft_medicos": parse_int(ft_medicos),
        "ft_enfermeiros": parse_int(ft_enfermeiros),
        "ft_tecnicos_enfermagem": parse_int(ft_tecnicos),
        "ft_enfermagem_geral": parse_int(ft_enfermagem_geral),
        "ft_multiprofissional": parse_int(ft_multiprofissional),
        "ft_administrativo": parse_int(ft_administrativo),
        "turnover_geral_pct": parse_pct(turnover),
        "admissoes_geral": parse_int(admissoes),
        "desligamentos_geral": parse_int(desligamentos),
        "atendimentos": parse_int(atendimentos),
        "cirurgias_realizadas": parse_int(cirurgias),
        "hbdf_taxa_ocupacao_pct": parse_pct(hbdf_ocupacao),
        "hbdf_media_permanencia_dias": parse_num(hbdf_permanencia),
        "hrsm_taxa_ocupacao_pct": parse_pct(hrsm_ocupacao),
        "hrsm_media_permanencia_dias": parse_num(hrsm_permanencia),
        "eventos_temas": parse_int(eventos_temas),
        "eventos_participantes": parse_int(eventos_participantes),
        "ouv_reclamacao_pct": parse_pct(ouv_reclamacao),
        "ouv_elogio_pct": parse_pct(ouv_elogio),
        "ouv_denuncia_pct": parse_pct(ouv_denuncia),
        "ouv_solicitacao_pct": parse_pct(ouv_solicitacao),
        "ouv_sugestao_pct": parse_pct(ouv_sugestao),
        "nps": nps_dict,
    }

    data = [d for d in data if not (d["ano"] == int(ano) and d["mes_num"] == mes_num)]
    data.append(novo_registro)
    save_data(data)

    st.success(f"✅ {mes_nome}/{int(ano)} salvo com sucesso! Volte para a página principal do painel para ver.")
    st.balloons()

st.markdown("---")
with st.expander("Ver todos os meses já cadastrados"):
    resumo = sorted(
        [(d["ano"], d["mes_num"], d["mes_nome"], d.get("fonte", "")) for d in load_data()]
    )
    for ano_r, mes_r, nome_r, fonte_r in resumo:
        st.write(f"- {nome_r}/{ano_r}  _(fonte: {fonte_r})_")
