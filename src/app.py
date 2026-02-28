from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from analytics import category_summary, month_details, monthly_summary, prepare_dataframe
from pipeline import load_transactions

st.set_page_config(page_title="Classificador de Gastos", page_icon="💳", layout="wide")

st.title("💳 Classificador de Gastos")
st.caption("Importação de faturas PDF/CSV/OFX, classificação automática e análise mensal.")

input_dir = st.text_input("Pasta de entrada", value="Input")

dataframe = load_transactions(input_dir)

if dataframe.empty:
    st.warning("Nenhum lançamento encontrado. Coloque arquivos PDF/CSV/OFX na pasta Input e recarregue.")
    st.stop()

df = prepare_dataframe(dataframe)
monthly = monthly_summary(df)
months = monthly["month"].tolist()

# ── estado persistente do mês selecionado ──────────────────────────────────────
if "selected_month" not in st.session_state or st.session_state.selected_month not in months:
    st.session_state.selected_month = months[-1] if months else None

# ── gráfico de barras com destaque na barra selecionada ───────────────────────
colors = [
    "#1f77b4" if m == st.session_state.selected_month else "#aec7e8"
    for m in months
]
fig = go.Figure(
    go.Bar(
        x=monthly["month"],
        y=monthly["total"],
        marker_color=colors,
        hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
    )
)
fig.update_layout(
    xaxis_tickangle=-30,
    xaxis_title="Mês",
    yaxis_title="Total (R$)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=10),
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Evolução mensal dos gastos")
    selection = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="bar_chart")

    # extrai o mês clicado pelo valor de x (mais confiável que point_index)
    clicked_month = None
    try:
        points = []
        if hasattr(selection, "selection"):
            points = getattr(selection.selection, "points", []) or []
        elif isinstance(selection, dict):
            points = selection.get("selection", {}).get("points", [])

        if points:
            x_val = points[0].get("x")
            if x_val in months:
                clicked_month = x_val
    except Exception:
        pass

    if clicked_month and clicked_month != st.session_state.selected_month:
        st.session_state.selected_month = clicked_month
        st.rerun()

with col2:
    st.subheader("Resumo rápido")
    st.metric("Total de lançamentos", f"{len(df):,}".replace(",", "."))
    st.metric(
        "Total consolidado",
        f"R$ {df['abs_amount'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )
    st.metric("Meses analisados", str(df["month"].nunique()))

# ── seletor de mês sincronizado com o clique ──────────────────────────────────
st.divider()
selected_month = st.selectbox(
    "Mês selecionado",
    options=months,
    index=months.index(st.session_state.selected_month),
    key="month_selectbox",
)
if selected_month != st.session_state.selected_month:
    st.session_state.selected_month = selected_month
    st.rerun()

# ── detalhes do mês selecionado ───────────────────────────────────────────────
st.subheader(f"Detalhes de {st.session_state.selected_month}")
details = month_details(df, st.session_state.selected_month)

if details.empty:
    st.info("Sem lançamentos para o mês selecionado.")
else:
    month_total = details["abs_amount"].sum()
    st.caption(
        f"{len(details)} lançamentos · "
        f"Total: R$ {month_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    det_col1, det_col2 = st.columns([1, 1])

    with det_col1:
        cat_sum = category_summary(details)
        if not cat_sum.empty:
            pie = px.pie(
                cat_sum,
                names="category",
                values="total",
                title="Distribuição por categoria",
            )
            st.plotly_chart(pie, use_container_width=True)

    with det_col2:
        cat_bar = category_summary(details)
        if not cat_bar.empty:
            bar_cat = px.bar(
                cat_bar.sort_values("total"),
                x="total",
                y="category",
                orientation="h",
                title="Categorias por valor",
                labels={"total": "R$", "category": ""},
            )
            bar_cat.update_layout(margin=dict(t=40, b=10))
            st.plotly_chart(bar_cat, use_container_width=True)

    show_columns = ["date", "description", "category", "amount", "source_file", "source_type"]
    details_table = details[show_columns].copy()
    details_table["date"] = details_table["date"].dt.strftime("%d/%m/%Y")
    st.dataframe(details_table, use_container_width=True, hide_index=True)
