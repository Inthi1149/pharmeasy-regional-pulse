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
    "Regional sales and profit dashboard - "
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
# LEVEL 1 - OVERVIEW
# -------------------------------------------------

st.header("1. Overview")

total_sales = filtered["sales_inr"].sum()
total_profit = filtered["profit_inr"].sum()
distinct_orders = filtered[
    "order_id"
].nunique()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Sales (INR)",
    f"{total_sales:,.2f}",
)

col2.metric(
    "Total Profit (INR)",
    f"{total_profit:,.2f}",
)

col3.metric(
    "Distinct Orders",
    f"{distinct_orders:,}",
)


# -------------------------------------------------
# EXECUTIVE SUMMARY
# -------------------------------------------------

st.subheader("Executive Summary")

month_order = [
    "Apr",
    "May",
    "Jun",
]

if len(filtered) == 0:
    st.write(
        "No order records are available for the selected "
        "region in April-June 2026. "
        "Sales, profit, and distinct-order KPIs are therefore zero. "
        "Use the region/month detail section below to confirm the "
        "absence of matched orders. "
        "No business cause should be inferred from an empty result."
    )
else:
    month_totals = (
        filtered.groupby("month")["sales_inr"]
        .sum()
        .reindex(month_order)
        .fillna(0)
    )

    top_category = (
        filtered.groupby("category")["sales_inr"]
        .sum()
        .idxmax()
    )

    if selected_region == "All Regions":
        scope_text = "the selected portfolio"
    else:
        scope_text = selected_region

    summary = (
        f"For {scope_text}, {distinct_orders:,} distinct orders "
        f"generated INR {total_sales:,.2f} in sales and "
        f"INR {total_profit:,.2f} in profit. "
        f"Monthly sales were INR {month_totals['Apr']:,.2f} "
        f"in April, INR {month_totals['May']:,.2f} in May, and "
        f"INR {month_totals['Jun']:,.2f} in June. "
        f"The largest category by sales in this view is "
        f"{top_category}. "
        f"Review material month-to-month movements before assigning "
        f"a business cause, using the category and region/month "
        f"detail below to investigate the underlying data."
    )

    st.write(summary)


# -------------------------------------------------
# MONTHLY SALES
# -------------------------------------------------

monthly = (
    filtered.groupby(
        ["region", "month"],
        as_index=False,
    )["sales_inr"]
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
    y="sales_inr",
    color="region",
    markers=True,
    title="How did monthly sales change across regions?",
    labels={
        "month": "Month",
        "sales_inr": "Sales (INR)",
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
    )["sales_inr"]
    .sum()
    .sort_values(
        "sales_inr",
        ascending=False,
    )
)

fig_bar = px.bar(
    region_sales,
    x="region",
    y="sales_inr",
    title="Which regions contributed the most sales?",
    labels={
        "region": "Region",
        "sales_inr": "Total Sales (INR)",
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
# LEVEL 2 - CATEGORY BREAKDOWN
# -------------------------------------------------

st.header("2. Category Breakdown")

category_sales = (
    filtered.groupby(
        "category",
        as_index=False,
    )["sales_inr"]
    .sum()
    .sort_values(
        "sales_inr",
        ascending=False,
    )
)

if len(category_sales) > 0:
    fig_donut = px.pie(
        category_sales,
        names="category",
        values="sales_inr",
        hole=0.45,
        title="What share of sales came from each category?",
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
    )

    category_display = category_sales.copy()
    category_display["sales_inr"] = (
        category_display["sales_inr"].round(2)
    )

    st.dataframe(
        category_display.rename(
            columns={
                "category": "Category",
                "sales_inr": "Sales (INR)",
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
# LEVEL 3 - REGION / MONTH DETAIL
# -------------------------------------------------

st.header("3. Region / Month Detail")

detail = (
    filtered.groupby(
        ["region", "month"],
        as_index=False,
    )
    .agg(
        sales_inr=("sales_inr", "sum"),
        profit_inr=("profit_inr", "sum"),
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

detail_display["sales_inr"] = (
    detail_display["sales_inr"]
    .round(2)
)

detail_display["profit_inr"] = (
    detail_display["profit_inr"]
    .round(2)
)

st.dataframe(
    detail_display.rename(
        columns={
            "region": "Region",
            "month": "Month",
            "sales_inr": "Sales (INR)",
            "profit_inr": "Profit (INR)",
            "distinct_orders": "Distinct Orders",
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
        "The 8% absolute month-to-month change rule is used "
        "to flag material movements for review. It is a "
        "business rule and does not represent statistical "
        "significance."
    )
elif selected_region in FLAGGED_REGIONS:
    st.warning(
        f"{selected_region} crossed the 8% month-to-month "
        f"business-rule threshold in at least one transition. "
        f"Review the underlying detail before assigning a cause."
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
        "Flagship Finding - Guntur"
    )

    st.write(
        "Guntur sales increased from INR 62,442.27 "
        "in April to INR 138,738.93 in May 2026, "
        "a +122.19% month-to-month change. "
        "Sales then decreased to INR 99,745.18 "
        "in June, a -28.11% change from May. "
        "The available dataset verifies these movements "
        "but does not establish their cause."
    )

    st.subheader("CII Narrative")

    st.markdown("**Context**")
    st.write(
        "Guntur recorded sales of INR 62,442.27 in April 2026, "
        "INR 138,738.93 in May 2026, and "
        "INR 99,745.18 in June 2026."
    )

    st.markdown("**Insight**")
    st.write(
        "Guntur sales increased by +122.19% from April to May "
        "and then decreased by -28.11% from May to June. "
        "Both movements crossed the 8% operational-alert threshold."
    )

    st.markdown("**Implication**")
    st.write(
        "The movement should be reviewed alongside the underlying "
        "order mix and available operational or commercial records "
        "before any cause or business action is concluded."
    )