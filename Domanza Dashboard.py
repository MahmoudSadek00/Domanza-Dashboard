import streamlit as st
import pandas as pd

# === تحميل البيانات من Google Sheets بصيغة CSV ===
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/export?format=csv&gid=248237253"
df = pd.read_csv(sheet_url)

# === تنظيف وتحضير البيانات ===
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
df['sub_total'] = pd.to_numeric(df['sub_total'], errors='coerce').fillna(0)
df['total_discount'] = pd.to_numeric(df['total_discount'], errors='coerce').fillna(0)
df['cashier_name'] = df['cashier_name'].astype(str).str.strip().str.title()  # توحيد الاسماء

# === احتساب المبيعات للموظفين ===
test = df[df['quantity'] > 0].copy()
test['calculated_total'] = test['sub_total'] - test['total_discount']

summary = test.groupby('cashier_name').agg(
    total_sales=('calculated_total', 'sum'),
    records=('quantity', 'count')
).sort_values(by='total_sales', ascending=False)

# === عرض النتيجة في Streamlit ===
st.title("👤 Employee Sales Summary")
st.dataframe(summary.style.format({'total_sales': '{:,.0f}', 'records': '{:,.0f}'}))
