import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files
import database  # <--- Import the new DB module

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Monthly Cash Flow", page_icon="💰", layout="wide")

# Initialize DB on startup
database.init_db()

# --- 2. HEADER ---
st.title("💰 Our Finance Dashboard")
st.markdown("_Tracking our monthly spending together_")

# --- 3. SIDEBAR (Data Input) ---
with st.sidebar:
    st.header("Upload New Data")
    uploaded_files = st.file_uploader("Add CSV files to History", type='csv', accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process & Save to Database"):
            with st.spinner("Processing..."):
                # 1. Process files using your engine
                new_df = process_files(uploaded_files)
                
                if not new_df.empty:
                    # 2. Save to SQLite
                    count = database.save_transactions(new_df)
                    if count > 0:
                        st.success(f"✅ Saved {count} new transactions!")
                        st.rerun() # Refresh to show new data
                    else:
                        st.warning("⚠️ No new data found (duplicates skipped).")
                else:
                    st.error("Could not process files.")

    st.divider()
    
    # Danger Zone
    if st.checkbox("Show Advanced Options"):
        if st.button("🗑️ Clear All History"):
            database.clear_database()
            st.warning("Database cleared!")
            st.rerun()

# --- 4. LOAD DATA FROM DATABASE ---
# The app now always loads from the DB, not the file uploader
df = database.load_all_transactions()

# --- 5. DASHBOARD LAYOUT ---
if not df.empty:
    
    # --- GLOBAL FILTER: MONTH SELECTOR ---
    # Since we have history now, we need to choose which month to view
    df['Month_Year'] = df['Date'].dt.to_period('M')
    available_months = sorted(df['Month_Year'].unique().astype(str), reverse=True)
    
    # Add "All Time" option
    selected_month = st.selectbox("📅 Select Month", ["All Time"] + available_months)
    
    # Filter the DataFrame based on selection
    if selected_month != "All Time":
        mask = df['Month_Year'].astype(str) == selected_month
        view_df = df[mask].copy()
    else:
        view_df = df.copy()

    st.divider()
    
    # --- LOGIC: SPLIT INCOME/EXPENSE (Same as Sprint 5) ---
    income_mask = (view_df['Amount'] > 0) & (view_df['Category'] == 'Income')
    income_df = view_df[income_mask]
    
    expense_mask = (view_df['Amount'] < 0) & (view_df['Category'] != 'Transfer') & (view_df['Category'] != 'Income')
    expenses_df = view_df[expense_mask].copy()
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    # --- METRICS ---
    total_income = income_df['Amount'].sum()
    total_expense = expenses_df['Abs_Amount'].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Income", f"NOK {total_income:,.0f}")
    m2.metric("💸 Expenses", f"NOK {total_expense:,.0f}")
    m3.metric("🐷 Net Savings", f"NOK {net_savings:,.0f}", delta_color="normal")
    m4.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    
    st.divider()

    # --- CHARTS ---
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Spending by Category")
        if not expenses_df.empty:
            category_sum = expenses_df.groupby("Category")["Abs_Amount"].sum().reset_index()
            fig_pie = px.pie(category_sum, values='Abs_Amount', names='Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses in this period.")

    with c2:
        st.subheader("Monthly Trend")
        # Now that we have a DB, we can show history!
        # We group the ORIGINAL full 'df' (not the filtered view_df) to show context
        
        # Filter for expenses only for the trend
        history_exp = df[(df['Amount'] < 0) & (df['Category'] != 'Transfer') & (df['Category'] != 'Income')].copy()
        history_exp['Abs_Amount'] = history_exp['Amount'].abs()
        history_exp['Month'] = history_exp['Date'].dt.strftime('%Y-%m')
        
        monthly_trend = history_exp.groupby('Month')['Abs_Amount'].sum().reset_index()
        
        fig_bar = px.bar(monthly_trend, x='Month', y='Abs_Amount', title="Expenses over Time", color_discrete_sequence=['#EF553B'])
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TRANSACTION TABLE ---
    st.divider()
    with st.expander("📄 View Transaction Details"):
        st.dataframe(
            view_df[['Date', 'Description', 'Category', 'Amount', 'Source']].sort_values(by='Date', ascending=False), 
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("The database is empty. Upload your first CSVs in the sidebar!")