import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Monthly Cash Flow",
    page_icon="💰",
    layout="wide"
)

# --- 2. HEADER ---
st.title("💰 Our Finance Dashboard")
st.markdown("_Tracking our monthly spending together_")
st.divider()

# --- 3. SIDEBAR (The Control Panel) ---
with st.sidebar:
    st.header("Upload Data")
    st.write("Upload your Bank and Credit Card CSVs here.")
    
    uploaded_files = st.file_uploader("Choose CSV files", type='csv', accept_multiple_files=True)
    
    st.info("ℹ️ You can select multiple files at once (e.g. Bank.csv and Amex.csv).")

# --- 4. DATA LOADING & PROCESSING ---
df = pd.DataFrame()

if uploaded_files:
    try:
        # Process the files using our engine
        df = process_files(uploaded_files)
        
        if not df.empty:
            st.toast(f"Successfully merged {len(uploaded_files)} files!", icon="✅")
        else:
            st.error("No valid data found in the uploaded files.")
            st.stop()
            
    except Exception as e:
        st.error(f"Error merging files: {e}")
        st.stop()

# --- 5. DASHBOARD LAYOUT ---
if not df.empty:
    st.divider()
    
    # --- LOGIC: SPLIT DATA ---
    # 1. Income: Positive Amounts AND Category is 'Income'
    income_mask = (df['Amount'] > 0) & (df['Category'] == 'Income')
    income_df = df[income_mask]
    
    # 2. Expenses: Negative Amounts AND Category is NOT 'Transfer' AND NOT 'Income'
    # We explicitly exclude transfers to avoid double counting
    expense_mask = (df['Amount'] < 0) & (df['Category'] != 'Transfer') & (df['Category'] != 'Income')
    expenses_df = df[expense_mask].copy()
    
    # Make positive for charts
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    # --- TOP METRICS ---
    total_income = income_df['Amount'].sum()
    total_expense = expenses_df['Abs_Amount'].sum()
    net_savings = total_income - total_expense
    
    # Avoid division by zero
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    # Display Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total Income", f"NOK {total_income:,.0f}")
    m2.metric("💸 Total Expenses", f"NOK {total_expense:,.0f}")
    m3.metric("🐷 Net Savings", f"NOK {net_savings:,.0f}", delta_color="normal")
    m4.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    
    st.divider()

    # --- CHARTS ROW ---
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Spending by Category")
        if not expenses_df.empty:
            category_sum = expenses_df.groupby("Category")["Abs_Amount"].sum().reset_index()
            fig_pie = px.pie(
                category_sum, 
                values='Abs_Amount', 
                names='Category', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses categorized yet.")

    with c2:
        st.subheader("Income vs Expenses")
        # Simple Bar Chart Comparison
        summary_data = pd.DataFrame({
            'Type': ['Income', 'Expenses'],
            'Amount': [total_income, total_expense]
        })
        fig_bar = px.bar(
            summary_data, 
            x='Type', 
            y='Amount', 
            color='Type',
            color_discrete_map={'Income': '#00CC96', 'Expenses': '#EF553B'},
            text_auto='.2s'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- DETAILED TRANSACTIONS ---
    st.divider()
    st.subheader("📄 Transaction Log")
    
    # Filter for debugging or deep dives
    filter_cat = st.multiselect("Filter by Category", options=df['Category'].unique(), default=[])
    
    view_df = df.copy()
    if filter_cat:
        view_df = view_df[view_df['Category'].isin(filter_cat)]
    
    # Show the table
    st.dataframe(
        view_df[['Date', 'Description', 'Category', 'Amount', 'Source']], 
        use_container_width=True,
        hide_index=True
    )

else:
    # --- ZERO STATE (Before Upload) ---
    st.info("Upload your Bank and Credit Card CSV files to generate the dashboard.")