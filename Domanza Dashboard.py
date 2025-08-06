import streamlit as st
import pandas as pd

st.set_page_config(page_title="Domanza Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# قراءة الداتا من Google Sheets كـ CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/export?format=csv&gid=248237253"
df = pd.read_csv(sheet_url)

# تنسيقات مبدئية
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['invoice_type'] = df['invoice_type'].astype(str).str.strip()
df['pos'] = df['pos'].astype(str).str.strip()
df['branch_name'] = df['branch_name'].astype(str).str.strip()

# تحديد channel
def detect_channel(row):
    if row['pos'].lower() == 'shopify':
        return "Online"
    elif row['branch_name'] == "Domanza Madinaty":
        return "Store"
    elif row['branch_name'] == "Domanza" and row['pos'] == "main device":
        return "Store"
    else:
        return "Online"

df['channel'] = df.apply(detect_channel, axis=1)

# تحديد نوع العملية
df['transaction_type'] = df['invoice_type'].apply(lambda x: "Return" if x == "Refund" else "Sale")

# حساب المؤشرات الأساسية
total_sales = df[df['transaction_type'] == "Sale"]['total'].sum()
total_returns = df[df['transaction_type'] == "Return"]['total'].sum()
store_sales = df[(df['channel'] == "Store") & (df['transaction_type'] == "Sale")]['total'].sum()
online_sales = df[(df['channel'] == "Online") & (df['transaction_type'] == "Sale")]['total'].sum()

# عرض الـ KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Net Sales", f"{total_sales:,.0f} EGP")
col2.metric("Total Returns", f"{total_returns:,.0f} EGP")
col3.metric("Store Sales", f"{store_sales:,.0f} EGP")
col4.metric("Online Sales", f"{online_sales:,.0f} EGP")

st.divider()

# 👤 مبيعات حسب الكاشير
st.subheader("👥 Sales by Cashier")
cashier_sales = df[df['transaction_type'] == "Sale"].groupby('cashier_name')['total'].sum().sort_values(ascending=False)
st.bar_chart(cashier_sales)

# 🏷️ مبيعات حسب البراند
st.subheader("🏷️ Sales by Brand")
brand_sales = df[df['transaction_type'] == "Sale"].groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(brand_sales)

# 📦 مبيعات حسب القنوات
st.subheader("📦 Sales by Channel")
channel_sales = df[df['transaction_type'] == "Sale"].groupby('channel')['total'].sum()
st.bar_chart(channel_sales)

# 🔍 عرض البيانات الخام
with st.expander("📄 عرض البيانات"):
    st.dataframe(df)
