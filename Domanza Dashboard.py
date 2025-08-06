import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="Domanza Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# رابط الشيت (تأكد إنه Shared as: Anyone with link - Viewer)
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/export?format=csv&gid=248237253"
df = pd.read_csv(sheet_url)

# تنسيقات الأعمدة
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['sub_total'] = pd.to_numeric(df['sub_total'], errors='coerce')
df['total_discount'] = pd.to_numeric(df['total_discount'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['invoice_type'] = df['invoice_type'].astype(str).str.strip()
df['pos'] = df['pos'].astype(str).str.strip()
df['branch_name'] = df['branch_name'].astype(str).str.strip()
df['cashier_name'] = df['cashier_name'].astype(str).str.strip()
df['brand'] = df['brand'].astype(str).str.strip()
df['name_ar'] = df['name_ar'].astype(str).str.strip()

# حساب القناة (channel)
def detect_channel(row):
    if row['pos'].lower() == 'shopify':
        return "Online"
    elif row['branch_name'] == "Domanza Madinaty":
        return "Store - Madinaty"
    elif row['branch_name'] == "Domanza" and row['pos'].lower() == "main device":
        return "Store - Maadi"
    else:
        return "Online"

df['channel'] = df.apply(detect_channel, axis=1)

# نوع العملية
df['transaction_type'] = df['invoice_type'].apply(lambda x: "Return" if x == "Refund" else "Sale")

# تصحيح المبالغ
df['calculated_total'] = (df['sub_total'] - df['total_discount']).round(2)
wrong_totals = df[abs(df['total'] - df['calculated_total']) > 1]
if not wrong_totals.empty:
    st.warning(f"🔧 {len(wrong_totals)} عملية تم فيها تصحيح المبلغ الإجمالي بسبب فرق في الحساب.")
df['total'] = df['calculated_total']

# تصنيف الفروع
def classify_branch(branch):
    if branch == "Domanza":
        return "Maadi"
    elif branch == "Domanza Madinaty":
        return "Madinaty"
    else:
        return "Other"

df['location'] = df['branch_name'].apply(classify_branch)

# ⏱️ الفلاتر الجانبية
with st.sidebar:
    st.header("🎛️ Filters")
    date_range = st.date_input("📅 تاريخ المبيعات", [df['date'].min(), df['date'].max()])
    selected_location = st.multiselect("📍 الفروع", df['location'].unique(), default=df['location'].unique())
    st.markdown("---")
    st.caption("Dashboard by Mahmoud @ Domanza")

# تطبيق الفلاتر
df_filtered = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['location'].isin(selected_location))
]

# مبيعات ومبالغ
sales_df = df_filtered[df_filtered['transaction_type'] == "Sale"]
returns_df = df_filtered[df_filtered['transaction_type'] == "Return"]

total_sales = sales_df['total'].sum()
total_returns = returns_df['total'].sum()
net_sales = total_sales - total_returns

store_sales = sales_df[sales_df['channel'].str.contains("Store")]['total'].sum()
online_sales = sales_df[sales_df['channel'] == 'Online']['total'].sum()

# KPIs
st.subheader("📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Net Sales", f"{net_sales:,.0f} EGP")
col2.metric("↩️ Returns", f"{total_returns:,.0f} EGP")
col3.metric("🏪 Store Sales", f"{store_sales:,.0f} EGP")
col4.metric("🌐 Online Sales", f"{online_sales:,.0f} EGP")

# ----------------------------
# 📊 مبيعات الموظفين حسب الفرع
st.subheader("👥 Sales by Employee & Branch")
cashier_location_sales = sales_df.groupby(['location', 'cashier_name'])['total'].sum().reset_index()
pivot_cashiers = cashier_location_sales.pivot(index='cashier_name', columns='location', values='total').fillna(0)
st.dataframe(pivot_cashiers.style.format("{:,.0f}"))

# ----------------------------
# 🏷️ مبيعات حسب البراند
st.subheader("🏷️ Sales by Brand")
brand_sales = sales_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(brand_sales)

# ----------------------------
# 🔝 أعلى المنتجات مبيعًا
st.subheader("🔥 Top-Selling Products")
top_products = sales_df.groupby('name_ar')['quantity'].sum().sort_values(ascending=False).head(10)
st.table(top_products)

# ----------------------------
# 🗓️ تحليل يومي / أسبوعي
st.subheader("📅 Daily Sales")
daily_sales = sales_df.groupby('date')['total'].sum()
st.line_chart(daily_sales)

st.subheader("📆 Weekly Sales")
weekly_sales = sales_df.resample('W-Mon', on='date')['total'].sum().reset_index()
st.line_chart(weekly_sales.set_index('date'))

# ----------------------------
# ↩️ المرتجعات حسب البراند
st.subheader("🔁 Returns by Brand")
returns_by_brand = returns_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(returns_by_brand)

# ----------------------------
# 🗃️ البيانات الخام
with st.expander("🗃️ عرض البيانات الخام"):
    st.dataframe(df_filtered)
