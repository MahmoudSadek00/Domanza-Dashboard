# نشوف عدد السطور لكل كاشير ومجموع مبيعاته
test = df[df['quantity'] > 0].copy()
test['sub_total'] = pd.to_numeric(test['sub_total'], errors='coerce').fillna(0)
test['total_discount'] = pd.to_numeric(test['total_discount'], errors='coerce').fillna(0)
test['calculated_total'] = test['sub_total'] - test['total_discount']
test['cashier_name'] = test['cashier_name'].astype(str).str.strip()

# تجميع بيانات الموظفين
summary = test.groupby('cashier_name').agg({
    'calculated_total': 'sum',
    'cashier_name': 'count'
}).rename(columns={'cashier_name': 'records'}).sort_values(by='calculated_total', ascending=False)

st.dataframe(summary)
