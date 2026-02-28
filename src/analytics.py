from __future__ import annotations

import pandas as pd


def prepare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe
    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["abs_amount"] = df["amount"].abs()
    return df


def monthly_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=["month", "total"])
    grouped = (
        dataframe.groupby("month", as_index=False)["abs_amount"]
        .sum()
        .rename(columns={"abs_amount": "total"})
        .sort_values("month")
    )
    return grouped


def month_details(dataframe: pd.DataFrame, month: str) -> pd.DataFrame:
    if dataframe.empty or not month:
        return pd.DataFrame(columns=dataframe.columns)
    return dataframe.loc[dataframe["month"] == month].sort_values("date")


def category_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=["category", "total"])
    return (
        dataframe.groupby("category", as_index=False)["abs_amount"]
        .sum()
        .rename(columns={"abs_amount": "total"})
        .sort_values("total", ascending=False)
    )
