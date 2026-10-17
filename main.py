import pandas as pd

# ---------- 1. Read data ----------
all_months = pd.read_excel(
    "client_data_values.xlsx",   # fixed filename
    sheet_name=None
)
print(all_months.keys())

# ---------- 2. Combine all sheets ----------
combined_frames = []
for month, df in all_months.items():
    print(month)
    print("Rows and columns:", df.shape)
    print("Columns:", list(df.columns))
    print("First date:", df["Date"].min())
    print("Last date:", df["Date"].max())
    print()

    df = df.copy()
    df["Month"] = month
    combined_frames.append(df)

combined = pd.concat(combined_frames, ignore_index=True)
print(combined.head().to_string())
print(combined.shape)
print(combined["Month"].value_counts())
print(combined.tail())

# ---------- 3. Melt to tidy format ----------
tidy = combined.melt(
    id_vars=["Date", "Month"],
    var_name="Category",
    value_name="Amount"
)
tidy = tidy.dropna(subset=["Amount"])
print(tidy.head(35))

# ---------- 4. Classify ----------
def classify(category):
    if category == "Income":
        return "income"
    elif category in ["Savings", "Susu"]:
        return "savings"
    elif category in [
        "Offertory", "Seeds", "Tithes", "First Fruit",
        "Alms/Giving", "Contributions"
    ]:
        return "giving"
    else:
        return "expense"

tidy["Type"] = tidy["Category"].apply(classify)
tidy["Amount"] = pd.to_numeric(tidy["Amount"], errors="coerce")

print(tidy.head())
print(tidy["Type"].value_counts())
print(tidy["Category"].value_counts())
print(tidy.groupby("Type")["Amount"].sum())

# ---------- 5. Monthly totals ----------
month_order = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY",
    "JUNE", "JULY", "AUGUST", "SEPTEMBER",
    "OCTOBER", "NOVEMBER", "DECEMBER"
]

tidy["Month"] = pd.Categorical(
    tidy["Month"],
    categories=month_order,
    ordered=True
)

monthly_totals = tidy.pivot_table(
    index="Month",
    columns="Type",
    values="Amount",
    aggfunc="sum",
    fill_value=0
).reindex(month_order).dropna(how="all")

print(monthly_totals)

# ---------- 6. Category by month ----------
category_month = tidy.pivot_table(
    index="Month",
    columns="Category",
    values="Amount",
    aggfunc="sum",
    fill_value=0
).reindex(month_order).dropna(how="all")

print(category_month.to_string())

# ---------- 7. Save ----------
tidy.to_csv("finance_clean.csv", index=False)
print("Saved finance_clean.csv with", len(tidy), "rows")

