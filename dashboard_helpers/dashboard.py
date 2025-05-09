import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config("📊 Peepalytics Dashboard", layout="wide")
st.title("📊 Peepalytics Transaction Dashboard")

# --- Upload CSV ---
st.sidebar.header("📁 Upload Redacted CSV")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv"])

if not uploaded_file:
    st.info("Please upload a redacted transaction CSV file to begin.")
    st.stop()

# --- Load Data ---
df = pd.read_csv(uploaded_file)
df.fillna(0, inplace=True)
df.iloc[9,3] =  df.iloc[9,2]
df.iloc[9,2] = 0
df.iloc[11,3] =  df.iloc[11,2]
df.iloc[11,2] = 0
df.iloc[-8,3] =  df.iloc[-8,2]
df.iloc[-8,2] = 0


# Step 1: Replace slashes with dashes if appears
df['date'] = df['date'].astype(str).str.replace('/', '-', regex=False)
# Step 2: Parse to datetime
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
df['description'] = df['description'].fillna("")

# --- Clean unwanted rows ---
non_transaction_keywords = ['opening balance', 'closing balance', 'statement balance']
df = df[~df['description'].str.lower().isin(non_transaction_keywords)]

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Set the date range for the slicer
min_date, max_date = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Amount range slicer
min_amt = float(df[['money_in', 'money_out']].min().min())
max_amt = float(df[['money_in', 'money_out']].max().max())
amount_range = st.sidebar.slider("Amount Range", min_amt, max_amt, (min_amt, max_amt), step=100.0)

# Description filter
text_query = st.sidebar.text_input("Search Description", placeholder="e.g. POS, ATM")

# --- Determine Start and End Period for Transaction ---
# Find the first non-zero money_in or money_out date (Transaction Start Period)
first_non_zero = df[(df['money_in'] != 0) | (df['money_out'] != 0)].iloc[0]

# Find the last non-zero money_in or money_out date (Transaction End Period)
last_non_zero = df[(df['money_in'] != 0) | (df['money_out'] != 0)].iloc[-1]

# Transaction start and end date
transaction_start_date = first_non_zero['date']
transaction_end_date = last_non_zero['date']

# --- Apply Filters for Visualizations ---
# Filter data based on the user's date range, amount range, and description filter
filtered_df = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]

# Visualizations will use this filtered_df based on date range, amount, and text query
visualized_df = filtered_df.copy()

# Apply amount filter
if amount_range[0] != min_amt or amount_range[1] != max_amt:
    visualized_df = visualized_df[
        (visualized_df['money_in'].between(amount_range[0], amount_range[1])) |
        (visualized_df['money_out'].between(amount_range[0], amount_range[1]))
    ]

# Apply description filter
if text_query:
    visualized_df = visualized_df[visualized_df['description'].str.contains(text_query, case=False, na=False)]

# --- KPIs --- (Reduced columns for compact display)
st.markdown("### 📈 Key Performance Indicators")

# Reduced the number of columns from 5 to 3
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Inflow", f"₦{visualized_df['money_in'].sum():,.2f}")
col2.metric("💸 Total Outflow", f"₦{visualized_df['money_out'].sum():,.2f}")
col3.metric("🔄 Avg Txn Amt", f"₦{(visualized_df['money_in'] + visualized_df['money_out']).sum() / max(len(visualized_df), 1):,.2f}")

col1, col2 = st.columns(2)
col1.metric("🧾 Transactions", len(visualized_df))
col2.metric("🗓️ Period", f"{transaction_start_date.strftime('%d %b %Y')} → {transaction_end_date.strftime('%d %b %Y')}")

st.divider()

# --- Charts ---
st.markdown("### 📊 Transaction Visualizations")

# Bar Chart: Daily Spend
daily_spend = visualized_df.groupby(visualized_df['date'].dt.date)['money_out'].sum().reset_index()
fig_bar = px.bar(daily_spend, x='date', y='money_out', title="💸 Daily Spend", labels={'money_out': 'Money Out ($)'})
st.plotly_chart(fig_bar, use_container_width=True)

# Line Chart: Running Balance
sorted_df = visualized_df.sort_values(by='date')
sorted_df['net'] = sorted_df['money_in'] - sorted_df['money_out']
sorted_df['running_balance'] = sorted_df['net'].cumsum()
fig_line = px.line(sorted_df, x='date', y='running_balance', title="📈 Running Balance Over Time")
st.plotly_chart(fig_line, use_container_width=True)

# Pie Chart: Category Breakdown (optional)
st.markdown("### 🧁 Transaction Categories (Optional)")
visualized_df['category'] = visualized_df['description'].str.extract(r'(POS|ATM|Loan|Transfer|Bill)', expand=False).fillna('Other')
cat_data = visualized_df['category'].value_counts().reset_index()
cat_data.columns = ['Category', 'Count']
fig_pie = px.pie(cat_data, names='Category', values='Count', title="Transaction Category Distribution", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- Transaction Table (All Data, No Slice) ---
st.markdown("### 📋 Transactions Table")
# Show all rows regardless of slicer filters (table is not affected by the slicer)
st.dataframe(df, use_container_width=True)

# --- Export Filtered Data ---
csv = visualized_df.to_csv(index=False).encode()
st.download_button("📥 Download Filtered CSV", csv, "filtered_transactions.csv", "text/csv")
