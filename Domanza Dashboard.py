import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعداد الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# تحميل البيانات من الشيت
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/edit#gid=248237253"
sheet = client.open_by_url(sheet_url)
worksheet = sheet.worksheet("Sales")  # غيّر الاسم لو مختلف
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# تنظيف وتنسيق الأعمدة
df['date'] = pd.to_datetime(df['date'])
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['invoice_type'] = df['invoice_type'].str.strip()

# تحديد channel
def detect_channel(row):
    if row['pos'] == 'Shopify':
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

# Streamlit app
st.set_page_config(page_title="Domanza Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# ملخص سريع
total_sales = df[df['transaction_type'] == "Sale"]['total'].sum()
total_returns = df[df['transaction_type'] == "Return"]['total'].sum()
store_sales = df[(df['channel'] == "Store") & (df['transaction_type'] == "Sale")]['total'].sum()
online_sales = df[(df['channel'] == "Online") & (df['transaction_type'] == "Sale")]['total'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Net Sales", f"{total_sales:,.0f} EGP")
col2.metric("Total Returns", f"{total_returns:,.0f} EGP")
col3.metric("Store Sales", f"{store_sales:,.0f} EGP")
col4.metric("Online Sales", f"{online_sales:,.0f} EGP")

st.divider()

# 📈 مبيعات حسب الموظفين
st.subheader("👤 Sales by Cashier")
cashier_sales = df[df['transaction_type'] == "Sale"].groupby('cashier_name')['total'].sum().sort_values(ascending=False)
st.bar_chart(cashier_sales)

# 🏷️ مبيعات حسب البراند
st.subheader("🏷️ Sales by Brand")
brand_sales = df[df['transaction_type'] == "Sale"].groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(brand_sales)

# 🛍️ مبيعات حسب القنوات
st.subheader("📦 Sales by Channel")
channel_sales = df[df['transaction_type'] == "Sale"].groupby('channel')['total'].sum()
st.bar_chart(channel_sales)

# 🧾 جدول البيانات الخام (مع الفلاتر)
st.subheader("🔍 Raw Data")
with st.expander("عرض البيانات كاملة"):
    st.dataframe(df)

