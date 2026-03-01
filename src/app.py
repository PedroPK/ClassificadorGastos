from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# filtra meses futuros
current_period = pd.Period.now("M").strftime("%Y-%m")
monthly = monthly[monthly["month"] <= current_period].copy()
months = monthly["month"].tolist()

# ── estado persistente do mês selecionado ──────────────────────────────────────
if "selected_month" not in st.session_state or st.session_state.selected_month not in months:
    st.session_state.selected_month = months[-1] if months else None

?# ── gráfico de barras com destaque na barra selecionada ───────────────────────
colors = [
    "#1f77b4" if m == st.session_state.selected_month else "#aec7e8"
    for m in months
]

# valores formatados em R$ para exibir no hover
hover_labels = [
    f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    for v in monthly["total"]
]

fig = go.Figure(
    go.Bar(
        x=monthly["month"],
        y=monthly["total"],
        marker_color=colors,
        customdata=hover_labels,
        hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#1f77b4",
            font=dict(size=14, color="#1f77b4"),
        ),
    )
)
fig.update_layout(
    xaxis_tickangle=-30,
    xaxis_title="Mês",
    yaxis_title="Total (R$)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=10),
    yaxis=dict(tickformat=",.0f"),
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Evolução mensal dos gastos")
    selection = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="bar_chart")

    # extrai o mês clicado — normaliza x_val para YYYY-MM pois o Plotly pode
    # devolver datas como "2025-12-01" ao interpretar o eixo como date
    clicked_month = None
    try:
        points = []
        if hasattr(selection, "selection"):
            points = getattr(selection.selection, "points", []) or []
        elif isinstance(selection, dict):
            points = selection.get("selection", {}).get("points", [])

        if points:
            point = points[0]
            x_val = str(point.get("x", ""))

            # normaliza para YYYY-MM (remove sufixos como " 00:00:00" ou "-01")
            normalized = x_val[:7]
            if normalized in months:
                clicked_month = normalized
            else:
                # fallback: usa point_index mapeado na lista de meses filtrada
                idx = point.get("point_index")
                if isinstance(idx, int) and 0 <= idx < len(months):
                    clicked_month = months[idx]
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

    cat_sum = category_summary(details)

    det_col1, det_col2 = st.columns([1, 1])

    with det_col1:
        if not cat_sum.empty:
            pie = px.pie(
                cat_sum,
                names="category",
                values="total",
                title="Distribuição por categoria",
            )
            pie.update_traces(hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>")
            st.plotly_chart(pie, use_container_width=True)

    with det_col2:
        if not cat_sum.empty:
            bar_cat = px.bar(
                cat_sum.sort_values("total"),
                x="total",
                y="category",
                orientation="h",
                title="Gastos por categoria",
                labels={"total": "R$", "category": ""},
            )
            bar_cat.update_traces(hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
            bar_cat.update_layout(margin=dict(t=40, b=10))
            st.plotly_chart(bar_cat, use_container_width=True)

    # pills de filtro — key inclui o mês para resetar automaticamente ao trocar de mês
    selected_category = None
    if not cat_sum.empty:
        cats_sorted = cat_sum.sort_values("total", ascending=False)["category"].tolist()
        selected_category = st.pills(
            "Filtrar por categoria (clique para selecionar/deselecionar):",
            options=cats_sorted,
            default=None,
            key=f"cat_pills_{st.session_state.selected_month}",
        )

    show_columns = ["date", "description", "category", "abs_amount", "source_file", "source_type"]
    details_table = details[show_columns].copy()
    details_table = details_table.rename(columns={"abs_amount": "valor"})
    details_table["date"] = details_table["date"].dt.strftime("%d/%m/%Y")

    # aplica filtro de categoria se selecionado
    if selected_category:
        st.info(f"Filtrando por categoria: **{selected_category}**")
        details_table = details_table[details_table["category"] == selected_category]

    st.dataframe(details_table, use_container_width=True, hide_index=True)

    total_amount = details_table["valor"].sum()
    total_fmt = f"R$ {total_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.dataframe(
        pd.DataFrame([{"": "TOTAL", "valor": total_fmt}]),
        use_container_width=True,
        hide_index=True,
    )
