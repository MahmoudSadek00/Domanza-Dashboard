import streamlit as st
import pandas as pd

# إعداد صفحة التطبيق
st.set_page_config(page_title="Domanza Sales Dashboard", layout="wide")
st.title("📊 Domanza Sales Dashboard")

# رابط جوجل شيت كـ CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1EmMJMcK3AL2sVLSqbJM9S8Re2l0U1pqGvFZca_2NruU/export?format=csv&gid=248237253"
df = pd.read_csv(sheet_url)

# تنسيق الأعمدة بشكل جيد
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['sub_total'] = pd.to_numeric(df['sub_total'], errors='coerce')
df['total_discount'] = pd.to_numeric(df['total_discount'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['invoice_type'] = df['invoice_type'].astype(str).str.strip()
df['pos'] = df['pos'].astype(str).str.strip().str.lower()
df['branch_name'] = df['branch_name'].astype(str).str.strip()
df['cashier_name'] = df['cashier_name'].astype(str).str.strip()
df['brand'] = df['brand'].astype(str).str.strip()
df['name_ar'] = df['name_ar'].astype(str).str.strip()

# تصنيف القناة بناءً على pos و branch_name
def detect_channel(row):
    if row['pos'] == 'shopify':
        return "Online"
    elif row['branch_name'] == "Domanza Madinaty":
        return "Store - Madinaty"
    elif row['branch_name'] == "Domanza" and row['pos'] == "main device":
        return "Store - Maadi"
    else:
        return "Online"

df['channel'] = df.apply(detect_channel, axis=1)

# ميز نوع العملية
df['transaction_type'] = df['invoice_type'].apply(lambda x: "Return" if x.lower() == "refund" else "Sale")

# تصنيف الفرع (معادي مقابل مدينتي)
def classify_branch(branch):
    if branch == "Domanza":
        return "Maadi"
    elif branch == "Domanza Madinaty":
        return "Madinaty"
    else:
        return "Other"

df['location'] = df['branch_name'].apply(classify_branch)

# شريط جانبي للفلاتر
with st.sidebar:
    st.header("🎛️ Filters")
    date_range = st.date_input("📅 الفترة الزمنية", [df['date'].min(), df['date'].max()])
    selected_locations = st.multiselect("📍 قم باختيار الفرع", df['location'].unique(), default=df['location'].unique())
    st.markdown("---")
    st.caption("Dashboard by Mahmoud @ Domanza")

# تطبيق الفلاتر
df_filtered = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['location'].isin(selected_locations))
]

sales_df = df_filtered[df_filtered['transaction_type'] == "Sale"]
returns_df = df_filtered[df_filtered['transaction_type'] == "Return"]

# حساب مؤشرات الأداء
total_sales = sales_df['total'].sum()
total_returns = returns_df['total'].sum()
net_sales = total_sales - total_returns
store_sales = sales_df[sales_df['channel'].str.contains("Store")]['total'].sum()
online_sales = sales_df[sales_df['channel'] == 'Online']['total'].sum()

# عرض KPIs
st.subheader("📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Net Sales", f"{net_sales:,.0f} EGP")
col2.metric("↩️ Returns", f"{total_returns:,.0f} EGP")
col3.metric("🏪 Store Sales", f"{store_sales:,.0f} EGP")
col4.metric("🌐 Online Sales", f"{online_sales:,.0f} EGP")

# مبيعات الموظفين حسب الفرع
st.subheader("👤 Employee Sales by Branch")
cashier_sales = sales_df.groupby(['location', 'cashier_name'])['total'].sum().reset_index()
pivot_cashier = cashier_sales.pivot(index='cashier_name', columns='location', values='total').fillna(0)
st.dataframe(pivot_cashier.style.format("{:,.0f}"))

# مبيعات البراندات
st.subheader("🏷️ Sales by Brand")
brand_sales = sales_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(brand_sales)

# المنتجات الأكثر بيعاً
st.subheader("🔥 Top Selling Products")
top_products = sales_df.groupby('name_ar')['quantity'].sum().sort_values(ascending=False).head(10)
st.table(top_products)

# مبيعات يومية
st.subheader("📈 Daily Sales")
daily_sales = sales_df.groupby('date')['total'].sum()
st.line_chart(daily_sales)

# مبيعات أسبوعية
st.subheader("📆 Weekly Sales")
weekly_sales = sales_df.resample('W-Mon', on='date')['total'].sum().reset_index()
st.line_chart(weekly_sales.set_index('date'))

# تحليل المرتجعات حسب البراند
st.subheader("↩️ Returns by Brand")
returns_by_brand = returns_df.groupby('brand')['total'].sum().sort_values(ascending=False)
st.bar_chart(returns_by_brand)

# عرض البيانات الكاملة
with st.expander("📂 Raw Data"):
    st.dataframe(df_filtered)

# تحذير لو فيه قيم مفقودة
if df_filtered.isnull().sum().sum() > 0:
    st.warning("⚠️ بعض الصفوف تحتوي على بيانات ناقصة. تأكد من تنسيق الشيت.")
