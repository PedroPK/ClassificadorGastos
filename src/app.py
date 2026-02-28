from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analytics import category_summary, month_details, monthly_summary, prepare_dataframe
from src.pipeline import load_transactions

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

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Evolução mensal dos gastos")
    fig = px.bar(monthly, x="month", y="total", labels={"month": "Mês", "total": "Total"})
    fig.update_layout(xaxis_tickangle=-30)
    selection = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

with col2:
    st.subheader("Resumo rápido")
    st.metric("Total de lançamentos", f"{len(df):,}".replace(",", "."))
    st.metric("Total consolidado", f"R$ {df['abs_amount'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("Meses analisados", str(df["month"].nunique()))

months = monthly["month"].tolist()
default_month = months[-1] if months else None

clicked_month = None
if isinstance(selection, dict):
    points = selection.get("selection", {}).get("points", [])
    if points:
        point_index = points[0].get("point_index")
        if isinstance(point_index, int) and 0 <= point_index < len(months):
            clicked_month = months[point_index]

selected_month = clicked_month or st.selectbox("Escolha o mês para detalhar", options=months, index=len(months) - 1)

st.subheader(f"Detalhes de {selected_month}")
details = month_details(df, selected_month)

cat_summary = category_summary(details)
if not cat_summary.empty:
    pie = px.pie(cat_summary, names="category", values="total", title="Distribuição por categoria")
    st.plotly_chart(pie, use_container_width=True)

show_columns = ["date", "description", "category", "amount", "source_file", "source_type"]
details_table = details[show_columns].copy()
details_table["date"] = details_table["date"].dt.strftime("%d/%m/%Y")
st.dataframe(details_table, use_container_width=True, hide_index=True)
