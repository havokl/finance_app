import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Monthly Expenditure Tracker",
    page_icon="💰",
    layout="wide"
)

# --- 2. HEADER ---
st.title("💰 Regnskap dashboard 2026")
st.markdown("_Tracking our monthly spending together_")
st.divider()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("Upload Data")
    st.write("Upload your Bank and Credit Card CSVs here.")
    
    # Enable multiple files!
    uploaded_files = st.file_uploader("Choose CSV files", type='csv', accept_multiple_files=True)
    
    st.info("ℹ️ You can select multiple files at once (e.g. Bank.csv and Amex.csv).")
    
# --- 4. DATA LOADING ---
if uploaded_files: # Check if the list is not empty
    try:
        # We pass the LIST of files to the processor
        df = process_files(uploaded_files)
        
        if not df.empty:
            st.toast(f"Successfully merged {len(uploaded_files)} files!", icon="✅")
        else:
            st.error("No valid data found in the uploaded files.")
            st.stop()
            
    except Exception as e:
        st.error(f"Error merging files: {e}")
        st.stop()
else:
    # Keep the mock data for now so the UI doesn't look empty before upload
    data = {
        'Date': ['2023-10-01', '2023-10-02', '2023-10-05'],
        'Description': ['REMA 1000', 'CIRCLE K', 'Netflix'],
        'Category': ['Groceries', 'Transport', 'Entertainment'],
        'Amount': [-450.50, -600.00, -159.00], # Notice negative for expenses
        'Type': ['Betaling', 'Betaling', 'Betaling']
    }
    df = pd.DataFrame(data)

# --- 5. DASHBOARD LAYOUT ---
# Create two columns: Main stats on left, Charts on right
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📄 Transaction History")
    # Streamlit has a powerful interactive dataframe widget
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("📊 Spending by Category")
    
    if 'Category' in df.columns and 'Amount' in df.columns:
        # 1. Filter for Expenses only (Negative values)
        # We don't want Income (positive numbers) to mess up the expense chart
        expenses_df = df[df['Amount'] < 0].copy()
        
        # 2. Convert to Absolute Values (Positive) so the Pie Chart can render
        expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
        
        if not expenses_df.empty:
            # 3. Group by Category
            category_sum = expenses_df.groupby("Category")["Abs_Amount"].sum().reset_index()
            
            # 4. Render Chart
            fig = px.pie(
                category_sum, 
                values='Abs_Amount', 
                names='Category', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            # Add hover info to show currency
            fig.update_traces(textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 5. Show Total Spend
            total_spend = expenses_df['Abs_Amount'].sum()
            st.metric("Total Expenses", f"NOK {total_spend:,.2f}")
            
        else:
            st.info("No expenses found in this data.")
    else:
        st.warning("Data missing necessary columns.")