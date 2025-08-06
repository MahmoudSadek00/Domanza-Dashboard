import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد صفحة Streamlit
st.set_page_config(page_title="Domanza Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# === قراءة البيانات من Google Sheets بصيغة CSV ===
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/export?format=csv&gid=248237253"
df = pd.read_csv(sheet_url)

# === تنسيقات وتحضيرات ===
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['sub_total'] = pd.to_numeric(df['sub_total'], errors='coerce')
df['total_discount'] = pd.to_numeric(df['total_discount'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['invoice_type'] = df['invoice_type'].astype(str).str.strip()
df['pos'] = df['pos'].astype(str).str.strip()
df['branch_name'] = df['branch_name'].astype(str).str.strip()

# === تحديد القناة (Store / Online) ===
def detect_channel(row):
    if row['pos'].lower() == 'shopify':
        return "Online"
    elif row['branch_name'] == "Domanza Madinaty":
        return "Store"
    elif row['branch_name'] == "Domanza" and row['pos'].lower() == "main device":
        return "Store"
    else:
        return "Online"

df['channel'] = df.apply(detect_channel, axis=1)

# === تحديد نوع العملية ===
df['transaction_type'] = df['invoice_type'].apply(lambda x: "Return" if x == "Refund" else "Sale")

# === تصحيح الـ total لو فيه فرق بسبب الخصومات ===
df['calculated_total'] = (df['sub_total'] - df['total_discount']).round(2)
df['total_check'] = (df['total'] - df['calculated_total']).abs() > 1
if df['total_check'].any():
    df['total'] = df['calculated_total']

# === الشريط الجانبي للفلاتر ===
with st.sidebar:
    st.header("🧰 Filters")
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.date_input("📅 اختر الفترة", [min_date, max_date])
    branches = st.multiselect("🏢 اختر الفروع", options=df['branch_name'].unique(), default=list(df['branch_name'].unique()))
    st.markdown("---")
    st.caption("Dashboard by Mahmoud @ Domanza")

# === تطبيق الفلاتر ===
df_filtered = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['branch_name'].isin(branches))
]

# === فصل المبيعات عن المرتجعات ===
sales_df = df_filtered[df_filtered['transaction_type'] == 'Sale']
returns_df = df_filtered[df_filtered['transaction_type'] == 'Return']

# === الحسابات الرئيسية ===
total_sales = sales_df['total'].sum()
total_returns = returns_df['total'].sum()
net_sales = total_sales - total_returns
store_sales = sales_df[sales_df['channel'] == 'Store']['total'].sum()
online_sales = sales_df[sales_df['channel'] == 'Online']['total'].sum()

# === KPIs ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Net Sales", f"{net_sales:,.0f} EGP")
col2.metric("🧾 Total Returns", f"{total_returns:,.0f} EGP")
col3.metric("🏬 Store Sales", f"{store_sales:,.0f} EGP")
col4.metric("🌐 Online Sales", f"{online_sales:,.0f} EGP")

st.divider()

# === مبيعات حسب الكاشير ===
st.subheader("👥 Sales by Cashier")
cashier_sales = sales_df.groupby('cashier_name')['total'].sum().sort_values(ascending=False)
st.bar_chart(cashier_sales)

# === مبيعات حسب البراند ===
st.subheader("🏷️ Sales by Brand")
brand_sales = sales_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(brand_sales)

# === أعلى المنتجات مبيعًا ===
st.subheader("📦 Top-Selling Products")
top_products = sales_df.groupby('name_ar')['quantity'].sum().sort_values(ascending=False).head(10)
st.table(top_products)

# === مبيعات يومية ===
st.subheader("📈 Daily Sales")
daily_sales = sales_df.groupby('date')['total'].sum()
st.line_chart(daily_sales)

# === مبيعات أسبوعية ===
st.subheader("📅 Weekly Sales")
weekly_sales = sales_df.resample('W-Mon', on='date')['total'].sum().reset_index().rename(columns={'total': 'weekly_total'})
st.line_chart(weekly_sales.set_index('date'))

# === المرتجعات حسب البراند ===
st.subheader("↩️ Returns by Brand")
returns_by_brand = returns_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(returns_by_brand)

# === عرض البيانات كاملة ===
with st.expander("📄 عرض البيانات الخام"):
    st.dataframe(df_filtered)

# === تحذير لو فيه بيانات ناقصة أو مشكلة ===
if df_filtered.isnull().sum().sum() > 0:
    st.warning("⚠️ بعض البيانات تحتوي على قيم ناقصة. تأكد من تنسيق الشيت.")
