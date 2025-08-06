import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# --- Sample Data Creation (Replace with actual Excel files later) ---
sales_data = pd.DataFrame({
    "Date": pd.date_range(start="2025-08-01", periods=30).tolist() * 3,
    "Channel": ["Branch"]*30 + ["Online"]*30 + ["Individual"]*30,
    "Branch": ["Cairo"]*15 + ["Alex"]*15 + ["Online"]*30 + ["-"]*30,  # ✅ تم تعديل مبيعات الأفراد
    "Brand": ["Nike", "Adidas", "Puma"] * 30,
    "Sales": [int(x) for x in abs(np.random.normal(2000, 800, 90))],
    "Salesperson": ["Ahmed"]*15 + ["Sara"]*15 + ["-"]*30 + ["Ahmed"]*15 + ["Sara"]*15
})

stock_data = pd.DataFrame({
    "Product": ["T-Shirt", "Hoodie", "Sneakers", "Cap", "Shorts"],
    "Brand": ["Nike", "Adidas", "Puma", "Nike", "Adidas"],
    "Available Qty": [5, 12, 0, 3, 7]
})

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_channel = st.sidebar.multiselect("Select Channel", options=sales_data["Channel"].unique(), default=sales_data["Channel"].unique())
selected_brand = st.sidebar.multiselect("Select Brand", options=sales_data["Brand"].unique(), default=sales_data["Brand"].unique())

# --- Filtered Data ---
filtered_sales = sales_data[
    (sales_data["Channel"].isin(selected_channel)) &
    (sales_data["Brand"].isin(selected_brand))
]

# --- KPIs ---
total_sales = filtered_sales["Sales"].sum()
branch_sales = filtered_sales[filtered_sales["Channel"] == "Branch"]["Sales"].sum()
online_sales = filtered_sales[filtered_sales["Channel"] == "Online"]["Sales"].sum()
individual_sales = filtered_sales[filtered_sales["Channel"] == "Individual"]["Sales"].sum()

st.subheader("📌 Sales Summary")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Total Sales", f"EGP {total_sales:,.0f}")
kpi2.metric("🏬 Branch Sales", f"EGP {branch_sales:,.0f}")
kpi3.metric("🛒 Online Sales", f"EGP {online_sales:,.0f}")
kpi4.metric("🧍 Individual Sales", f"EGP {individual_sales:,.0f}")

# --- Sales by Date ---
st.subheader("📅 Sales Trend")
sales_trend = filtered_sales.groupby(["Date", "Channel"])["Sales"].sum().reset_index()
fig1 = px.line(sales_trend, x="Date", y="Sales", color="Channel", markers=True, title="Daily Sales by Channel")
st.plotly_chart(fig1, use_container_width=True)

# --- Sales by Brand ---
st.subheader("🏷️ Sales by Brand")
brand_summary = filtered_sales.groupby("Brand")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False)
fig2 = px.bar(brand_summary, x="Brand", y="Sales", text_auto=True, title="Total Sales per Brand")
st.plotly_chart(fig2, use_container_width=True)

# --- Stock Monitoring ---
st.subheader("📦 Stock Status")
st.dataframe(stock_data, use_container_width=True)

# --- Individual Sales (if applicable) ---
st.subheader("🧍 Sales by Individual")
individual_summary = filtered_sales[filtered_sales["Channel"] == "Individual"]
if not individual_summary.empty:
    person_sales = individual_summary.groupby("Salesperson")["Sales"].sum().reset_index()
    fig3 = px.pie(person_sales, names="Salesperson", values="Sales", title="Individual Sales Distribution")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No individual sales data available for the selected filters.")
