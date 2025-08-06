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
store
