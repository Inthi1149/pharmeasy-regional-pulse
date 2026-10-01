import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


DB_FILE = "pharmeasy.db"

FLAGGED_REGIONS = {
    "Hyderabad",
    "Warangal",
    "Vijayawada",
    "Visakhapatnam",
    "Guntur",
    "Tirupati",
    "Karimnagar",
    "Bengaluru",
}


st.set_page_config(
    page_title="PharmEasy Regional Pulse",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data():
    connection = sqlite3.connect(DB_FILE)

    orders = pd.read_sql_query(
        """
        SELECT *
        FROM orders_clean
        """,
        connection,
    )

    regions = pd.read_sql_query(
        """
        SELECT *
        FROM regions_master
        """,
        connection,
    )

    connection.close()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    orders["month"] = orders[
        "order_date"
    ].dt.strftime("%b")

    return orders, regions


orders, regions = load_data()


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("PharmEasy Regional Pulse")

st.caption(
    "Regional sales and profit dashboard — "
    "April to June 2026"
)


# -------------------------------------------------
# ONE REGION FILTER CONNECTED TO ALL LEVELS
# -------------------------------------------------

region_options = [
    "All Regions"
] + regions["region"].sort_values().tolist()

selected_region = st.sidebar.selectbox(
    "Region",
    region_options,
)

if selected_region == "All Regions":
    filtered = orders.copy()
else:
    filtered = orders[
        orders["region"] == selected_region
    ].copy()


# -------------------------------------------------
# LEVEL 1 — OVERVIEW
# -------------------------------------------------

st.header("1. Overview")

total_sales = filtered["sales"].sum()
total_profit = filtered["profit"].sum()
distinct_orders = filtered[
    "order_id"
].nunique()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Sales",
    f"{total_sales:,.2f}",
)

col2.metric(
    "Total Profit",
    f"{total_profit:,.2f}",
)

col3.metric(
    "Distinct Orders",
    f"{distinct_orders:,}",
)


# -------------------------------------------------
# MONTHLY SALES
# -------------------------------------------------

month_order = [
    "Apr",
    "May",
    "Jun",
]

monthly = (
    filtered.groupby(
        ["region", "month"],
        as_index=False,
    )["sales"]
    .sum()
)

monthly["month"] = pd.Categorical(
    monthly["month"],
    categories=month_order,
    ordered=True,
)

monthly = monthly.sort_values(
    ["region", "month"]
)


fig_line = px.line(
    monthly,
    x="month",
    y="sales",
    color="region",
    markers=True,
    title=(
        "How did monthly sales change "
        "across regions?"
    ),
    labels={
        "month": "Month",
        "sales": "Sales",
        "region": "Region",
    },
)

fig_line.update_yaxes(
    rangemode="tozero"
)

st.plotly_chart(
    fig_line,
    use_container_width=True,
)


# -------------------------------------------------
# TOTAL SALES BY REGION
# -------------------------------------------------

region_sales = (
    filtered.groupby(
        "region",
        as_index=False,
    )["sales"]
    .sum()
    .sort_values(
        "sales",
        ascending=False,
    )
)

fig_bar = px.bar(
    region_sales,
    x="region",
    y="sales",
    title=(
        "Which regions contributed "
        "the most sales?"
    ),
    labels={
        "region": "Region",
        "sales": "Total Sales",
    },
)

fig_bar.update_yaxes(
    rangemode="tozero"
)

st.plotly_chart(
    fig_bar,
    use_container_width=True,
)


# -------------------------------------------------
# EXECUTIVE SUMMARY
# -------------------------------------------------

st.subheader("Executive Summary")

if len(filtered) == 0:

    st.write(
        "No order records are available for the "
        "selected region in April–June 2026. "
        "Use the detail section below to confirm "
        "the absence of matched orders."
    )

else:

    month_totals = (
        filtered.groupby("month")["sales"]
        .sum()
        .reindex(month_order)
        .fillna(0)
    )

    top_category = (
        filtered.groupby("category")["sales"]
        .sum()
        .idxmax()
    )

    if selected_region == "All Regions":
        scope_text = "the selected portfolio"
    else:
        scope_text = selected_region

    summary = (
        f"For {scope_text}, total sales are "
        f"{total_sales:,.2f}, total profit is "
        f"{total_profit:,.2f}, across "
        f"{distinct_orders:,} distinct orders. "
        f"Monthly sales were "
        f"{month_totals['Apr']:,.2f} in April, "
        f"{month_totals['May']:,.2f} in May, and "
        f"{month_totals['Jun']:,.2f} in June. "
        f"The largest category by sales in this "
        f"view is {top_category}. "
        f"Review material month-to-month movements "
        f"before assigning a business cause, and "
        f"use the category and detail sections "
        f"below to investigate the underlying data."
    )

    st.write(summary)


# -------------------------------------------------
# LEVEL 2 — CATEGORY BREAKDOWN
# -------------------------------------------------

st.header("2. Category Breakdown")

category_sales = (
    filtered.groupby(
        "category",
        as_index=False,
    )["sales"]
    .sum()
    .sort_values(
        "sales",
        ascending=False,
    )
)

if len(category_sales) > 0:

    fig_donut = px.pie(
        category_sales,
        names="category",
        values="sales",
        hole=0.45,
        title=(
            "What share of sales came "
            "from each category?"
        ),
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
    )

    st.dataframe(
        category_sales.rename(
            columns={
                "category": "Category",
                "sales": "Sales",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No category sales are available "
        "for this selection."
    )


# -------------------------------------------------
# LEVEL 3 — REGION / MONTH DETAIL
# -------------------------------------------------

st.header("3. Region / Month Detail")

detail = (
    filtered.groupby(
        ["region", "month"],
        as_index=False,
    )
    .agg(
        sales=("sales", "sum"),
        profit=("profit", "sum"),
        distinct_orders=(
            "order_id",
            "nunique",
        ),
    )
)

detail["month"] = pd.Categorical(
    detail["month"],
    categories=month_order,
    ordered=True,
)

detail = detail.sort_values(
    ["region", "month"]
)

detail_display = detail.copy()

detail_display["sales"] = (
    detail_display["sales"]
    .round(2)
)

detail_display["profit"] = (
    detail_display["profit"]
    .round(2)
)

st.dataframe(
    detail_display.rename(
        columns={
            "region": "Region",
            "month": "Month",
            "sales": "Sales",
            "profit": "Profit",
            "distinct_orders": (
                "Distinct Orders"
            ),
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# -------------------------------------------------
# FLAGGED MOVEMENT NOTE
# -------------------------------------------------

st.subheader("Movement Review")

if selected_region == "All Regions":

    st.write(
        "The 8% absolute month-to-month change "
        "rule is used to flag material movements "
        "for review. It is a business rule and "
        "does not represent statistical significance."
    )

elif selected_region in FLAGGED_REGIONS:

    st.warning(
        f"{selected_region} crossed the 8% "
        f"month-to-month business-rule threshold "
        f"in at least one transition. Review the "
        f"underlying detail before assigning a cause."
    )

else:

    st.info(
        f"{selected_region} did not cross the "
        f"8% month-to-month business-rule threshold."
    )


# -------------------------------------------------
# GUNTUR FLAGSHIP STORY
# -------------------------------------------------

if (
    selected_region == "All Regions"
    or selected_region == "Guntur"
):

    st.subheader(
        "Flagship Finding — Guntur"
    )

    st.write(
        "Guntur sales increased from 78,000.00 "
        "in April to 173,308.20 in May 2026, "
        "a +122.19% month-to-month change. "
        "Sales then decreased to 124,527.00 "
        "in June, a -28.15% change from May. "
        "The available dataset verifies these "
        "movements but does not establish their cause."
    )