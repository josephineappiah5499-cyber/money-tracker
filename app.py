import pandas as pd


tidy = pd.read_csv("finance_clean.csv", parse_dates=["Date"])
month_order = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY",
    "JUNE", "JULY", "AUGUST", "SEPTEMBER"
]

tidy["Month"] = pd.Categorical(
    tidy["Month"],
    categories=month_order,
    ordered=True
)

import streamlit as st

st.title("Money Tracker")

st.sidebar.header("Filters")

selected_month = st.sidebar.selectbox(
    "Choose a month",
    ["All months"] + month_order
)

if selected_month == "All months":
    filtered = tidy
else:
    filtered = tidy[tidy["Month"] == selected_month]

total_income = filtered.loc[filtered["Type"] == "income", "Amount"].sum()
total_expenses = filtered.loc[filtered["Type"] == "expense", "Amount"].sum()
total_giving = filtered.loc[filtered["Type"] == "giving", "Amount"].sum()
total_savings = filtered.loc[filtered["Type"] == "savings", "Amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Income", f"{total_income:,.2f}")
col2.metric("Expenses", f"{total_expenses:,.2f}")
col3.metric("Giving", f"{total_giving:,.2f}")
col4.metric("Savings", f"{total_savings:,.2f}")

monthly_totals = filtered.pivot_table(
    index="Month",
    columns="Type",
    values="Amount",
    aggfunc="sum",
    fill_value=0
)

st.subheader("Monthly overview")
st.bar_chart(monthly_totals[["income", "expense", "giving", "savings"]])

st.subheader("Monthly totals")
st.dataframe(monthly_totals)

st.subheader("Individual category tracker")

selected_category = st.selectbox(
    "Choose a category",
    sorted(filtered["Category"].unique())
)

category_data = filtered[filtered["Category"] == selected_category]

category_by_month = category_data.pivot_table(
    index="Month",
    values="Amount",
    aggfunc="sum",
    fill_value=0
)

st.metric(
    f"Total {selected_category}",
    f"{category_by_month['Amount'].sum():,.2f}"
)

st.bar_chart(category_by_month)
st.dataframe(category_by_month)

st.subheader("Download report")

csv_data = monthly_totals.to_csv().encode("utf-8")

st.download_button(
    label="Download monthly summary",
    data=csv_data,
    file_name="money_tracker_summary.csv",
    mime="text/csv"
)

@st.cache_data
def load_data():
    return pd.read_csv("finance_clean.csv", parse_dates=["Date"])

tidy = load_data()

selected_categories = st.multiselect(
    "Choose categories to compare",
    sorted(filtered["Category"].unique()),
    default=["Transport", "Food"]
)

category_data = filtered[filtered["Category"].isin(selected_categories)]

category_by_month = category_data.pivot_table(
    index="Month",
    columns="Category",
    values="Amount",
    aggfunc="sum",
    fill_value=0
)

st.bar_chart(category_by_month)
st.dataframe(category_by_month)

st.subheader("Key insights")

highest_expense_month = monthly_totals["expense"].idxmax()
highest_expense_amount = monthly_totals["expense"].max()

st.write(
    f"The highest expenses were in **{highest_expense_month}**: "
    f"**{highest_expense_amount:,.2f}**."
)

if "income" in monthly_totals.columns:
    lowest_income_month = monthly_totals["income"].idxmin()
    st.write(
        f"The lowest income was in **{lowest_income_month}**."
    )