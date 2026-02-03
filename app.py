import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files
import database
# Import the new mapping
from categories import EXPENSE_TYPES 

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")
database.init_db()

# --- 2. SIDEBAR (Navigation & Upload) ---
with st.sidebar:
    st.title("💰 Finance App")
    
    # NAVIGATION MENU
    page = st.radio("Go to", ["📊 Monthly Overview", "⚖️ Fixed vs Variable"])
    st.divider()
    
    # UPLOAD SECTION
    st.header("Upload Data")
    uploaded_files = st.file_uploader("Add CSV files", type='csv', accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process & Save"):
            with st.spinner("Processing..."):
                new_df = process_files(uploaded_files)
                if not new_df.empty:
                    count = database.save_transactions(new_df)
                    if count > 0:
                        st.success(f"✅ Saved {count} new transactions!")
                        st.rerun()
                    else:
                        st.warning("⚠️ No new data (duplicates).")
                else:
                    st.error("Could not process files.")
    
    st.divider()
    if st.checkbox("Show Advanced Options"):
        if st.button("🗑️ Clear Database"):
            database.clear_database()
            st.warning("Cleared!")
            st.rerun()

# --- 3. LOAD DATA ---
df = database.load_all_transactions()

if df.empty:
    st.info("👋 Welcome! Upload your first bank/credit card CSVs in the sidebar to get started.")
    st.stop() # Stop here if no data

# --- GLOBAL PROCESSING (Add Month/Type columns) ---
df['Month_Year'] = df['Date'].dt.to_period('M')

# Add "Expense Type" column based on your new dictionary
# We use .map() to look up the category in EXPENSE_TYPES
df['Type_Tag'] = df['Category'].map(EXPENSE_TYPES).fillna('Variable') 
# Note: .fillna('Variable') assumes anything undefined is Variable by default.

# --- PAGE 1: MONTHLY OVERVIEW (Your original dashboard) ---
if page == "📊 Monthly Overview":
    st.header("📊 Monthly Cash Flow")
    
    # Month Selector
    available_months = sorted(df['Month_Year'].unique().astype(str), reverse=True)
    selected_month = st.selectbox("Select Month", ["All Time"] + available_months)
    
    # Filter Data
    if selected_month != "All Time":
        view_df = df[df['Month_Year'].astype(str) == selected_month].copy()
    else:
        view_df = df.copy()

    # Metrics Logic
    income_mask = (view_df['Amount'] > 0) & (view_df['Category'] == 'Income')
    income_df = view_df[income_mask]
    
    expense_mask = (view_df['Amount'] < 0) & (view_df['Category'] != 'Transfer') & (view_df['Category'] != 'Income')
    expenses_df = view_df[expense_mask].copy()
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    total_income = income_df['Amount'].sum()
    total_expense = expenses_df['Abs_Amount'].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    # Display Metrics
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Income", f"NOK {total_income:,.0f}")
    m2.metric("💸 Expenses", f"NOK {total_expense:,.0f}")
    m3.metric("🐷 Net Savings", f"NOK {net_savings:,.0f}", delta_color="normal")
    m4.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    st.divider()

    # Charts
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Spending by Category")
        if not expenses_df.empty:
            cat_sum = expenses_df.groupby("Category")["Abs_Amount"].sum().reset_index()
            fig = px.pie(cat_sum, values='Abs_Amount', names='Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.subheader("Monthly Trend")
        # Global trend (using full df)
        hist_exp = df[(df['Amount'] < 0) & (df['Category'] != 'Transfer') & (df['Category'] != 'Income')].copy()
        hist_exp['Abs_Amount'] = hist_exp['Amount'].abs()
        hist_exp['Month'] = hist_exp['Date'].dt.strftime('%Y-%m')
        trend = hist_exp.groupby('Month')['Abs_Amount'].sum().reset_index()
        fig = px.bar(trend, x='Month', y='Abs_Amount')
        st.plotly_chart(fig, use_container_width=True)

    # Transaction Table
    st.divider()
    with st.expander("View Transactions"):
        st.dataframe(view_df[['Date', 'Description', 'Category', 'Amount']].sort_values(by='Date', ascending=False), use_container_width=True)


# --- PAGE 2: FIXED vs VARIABLE (The New Pane) ---
elif page == "⚖️ Fixed vs Variable":
    st.header("⚖️ Fixed vs Variable Analysis")
    st.markdown("Analyze your 'Must-Haves' (Fixed) vs 'Nice-to-Haves' (Variable).")
    
    # 1. Prepare Data
    # Filter for expenses only
    exp_df = df[(df['Amount'] < 0) & (df['Category'] != 'Transfer') & (df['Category'] != 'Income')].copy()
    exp_df['Abs_Amount'] = exp_df['Amount'].abs()
    
    if exp_df.empty:
        st.info("No expenses found.")
        st.stop()

    # 2. Top Level Split
    type_sum = exp_df.groupby("Type_Tag")["Abs_Amount"].sum().reset_index()
    
    c1, c2 = st.columns(2)
    with c1:
        # Pie Chart of Fixed vs Variable
        fig_type = px.pie(
            type_sum, 
            values='Abs_Amount', 
            names='Type_Tag', 
            title="Distribution",
            color='Type_Tag',
            color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'} # Blue for Fixed, Red for Variable
        )
        st.plotly_chart(fig_type, use_container_width=True)
        
    with c2:
        # Breakdown Table
        st.subheader("Breakdown")
        total = type_sum['Abs_Amount'].sum()
        
        # Calculate percentages
        type_sum['%'] = (type_sum['Abs_Amount'] / total * 100).round(1)
        st.dataframe(
            type_sum.style.format({'Abs_Amount': "NOK {:,.2f}", '%': "{:.1f}%"}), 
            use_container_width=True, 
            hide_index=True
        )

    st.divider()
    
    # 3. Trend Over Time (Stacked Bar)
    st.subheader("Development Over Time")
    exp_df['Month'] = exp_df['Date'].dt.strftime('%Y-%m')
    
    monthly_type = exp_df.groupby(['Month', 'Type_Tag'])['Abs_Amount'].sum().reset_index()
    
    fig_bar = px.bar(
        monthly_type, 
        x='Month', 
        y='Abs_Amount', 
        color='Type_Tag', 
        title="Fixed vs Variable Spending per Month",
        barmode='stack', # Stack them on top of each other
        color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.info("💡 **Tip:** 'Fixed' expenses are usually Rent, Utilities, and Insurance. 'Variable' expenses are Dining Out, Shopping, and Fun. Try to keep Fixed expenses below 50% of your income.")