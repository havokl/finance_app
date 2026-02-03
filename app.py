import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files
import database
from categories import EXPENSE_TYPES 

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")
database.init_db()

# --- CSS STYLING ---
st.markdown("""
<style>
    [data-testid="stRadio"] > div { gap: 10px; }
    [data-testid="stRadio"] label > div:first-child { display: none; }
    [data-testid="stRadio"] label {
        padding: 10px 15px;
        background-color: #f0f2f6;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    [data-testid="stRadio"] label:hover {
        background-color: #e0e2e6;
        border-color: #d0d2d6;
    }
    [data-testid="stRadio"] label[data-checked="true"] {
        background-color: #e8f0fe;
        border-color: #4285f4;
        color: #1967d2;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("💰 Finance App")
    st.markdown("---")
    
    st.caption("MAIN MENU")
    page = st.radio(
        "Navigate", 
        ["📊 Monthly Dashboard", "📈 Long-term Trends", "⚖️ Fixed vs Variable"],
        label_visibility="collapsed",
        key="main_nav"
    )
    
    st.markdown("---")
    
    st.caption("DATA MANAGEMENT")
    uploaded_files = st.file_uploader("Upload CSVs", type='csv', accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process & Save", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                new_df = process_files(uploaded_files)
                if not new_df.empty:
                    count = database.save_transactions(new_df)
                    if count > 0:
                        st.success(f"✅ Saved {count} items!")
                        st.rerun()
                    else:
                        st.warning("⚠️ No new data.")
                else:
                    st.error("Could not process.")
    
    st.markdown("---")
    with st.expander("⚙️ Settings"):
        if st.button("🗑️ Clear Database", use_container_width=True):
            database.clear_database()
            st.warning("Cleared!")
            st.rerun()

# --- 3. LOAD DATA ---
df = database.load_all_transactions()

if df.empty:
    st.info("👋 Welcome! Upload your first bank/credit card CSVs in the sidebar to get started.")
    st.stop()

# ==========================================
#      NEW FEATURE: UNCATEGORIZED REVIEW
# ==========================================
uncategorized_df = df[df['Category'] == 'Uncategorized'].copy()

if not uncategorized_df.empty:
    st.warning(f"⚠️ You have {len(uncategorized_df)} uncategorized transactions!")
    
    with st.expander("🔍 Review & Fix Uncategorized Items", expanded=True):
        st.markdown("Assign categories below and click **Save Changes**.")
        
        # Get list of valid categories from your settings
        # We filter out 'Ignore' types if you want, or keep all keys
        valid_categories = sorted(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer'])
        
        # Configure the editor
        edited_df = st.data_editor(
            uncategorized_df[['Date', 'Description', 'Amount', 'Category', 'id']], # Include ID hidden? No, need it for logic
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Assign Category",
                    help="Select the correct category",
                    width="medium",
                    options=valid_categories,
                    required=True,
                ),
                "id": None, # Hide the ID column from the UI
                "Date": st.column_config.DatetimeColumn(disabled=True),
                "Description": st.column_config.TextColumn(disabled=True),
                "Amount": st.column_config.NumberColumn(disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            key="editor_uncat"
        )
        
        if st.button("💾 Save Changes"):
            changes_count = 0
            
            # Iterate through the edited dataframe
            for index, row in edited_df.iterrows():
                original_row = uncategorized_df.loc[index]
                
                # If the category changed from 'Uncategorized' to something else
                if row['Category'] != 'Uncategorized':
                    # Update in Database
                    success = database.update_transaction_category(row['id'], row['Category'])
                    if success:
                        changes_count += 1
            
            if changes_count > 0:
                st.success(f"✅ Updated {changes_count} transactions!")
                st.rerun()
            else:
                st.info("No changes detected.")
    st.divider()

# ==========================================
#          END NEW FEATURE
# ==========================================

# --- GLOBAL PROCESSING ---
df['Month_Year'] = df['Date'].dt.to_period('M')
df['Type_Tag'] = df['Category'].map(EXPENSE_TYPES).fillna('Variable') 

# --- VIEW 1: MONTHLY DASHBOARD ---
if page == "📊 Monthly Dashboard":
    st.header("📊 Monthly Snapshot")
    
    available_months = sorted(df['Month_Year'].unique().astype(str), reverse=True)
    col_sel, _ = st.columns([1, 4])
    with col_sel:
        selected_month = st.selectbox("Select Month", ["All Time"] + available_months)
    
    if selected_month != "All Time":
        view_df = df[df['Month_Year'].astype(str) == selected_month].copy()
    else:
        view_df = df.copy()

    # Metrics
    income_mask = (view_df['Amount'] > 0) & (view_df['Category'] == 'Income')
    income_df = view_df[income_mask]
    
    expense_mask = (view_df['Amount'] < 0) & (view_df['Category'] != 'Transfer') & (view_df['Category'] != 'Income')
    expenses_df = view_df[expense_mask].copy()
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    total_income = income_df['Amount'].sum()
    total_expense = expenses_df['Abs_Amount'].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Income", f"NOK {total_income:,.0f}")
    m2.metric("💸 Expenses", f"NOK {total_expense:,.0f}")
    m3.metric("🐷 Net Savings", f"NOK {net_savings:,.0f}", delta_color="normal")
    m4.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    st.divider()

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Where did the money go?")
        if not expenses_df.empty:
            cat_sum = expenses_df.groupby("Category")["Abs_Amount"].sum().reset_index()
            fig = px.pie(cat_sum, values='Abs_Amount', names='Category', hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses this month.")
            
    with c2:
        st.subheader("Top Expenses")
        if not expenses_df.empty:
            top_tx = expenses_df.nlargest(10, 'Abs_Amount')[['Description', 'Category', 'Abs_Amount', 'Date']]
            st.dataframe(top_tx.style.format({'Abs_Amount': "{:,.2f}"}), use_container_width=True, hide_index=True)

    with st.expander("📄 View All Transactions"):
        st.dataframe(view_df[['Date', 'Description', 'Category', 'Amount', 'Source']].sort_values(by='Date', ascending=False), use_container_width=True)

# --- VIEW 2: LONG-TERM TRENDS ---
elif page == "📈 Long-term Trends":
    st.header("📈 Financial History")
    
    history_df = df.copy()
    history_df['Month'] = history_df['Date'].dt.strftime('%Y-%m')
    
    monthly_summary = []
    for month in sorted(history_df['Month'].unique()):
        m_df = history_df[history_df['Month'] == month]
        inc = m_df[(m_df['Amount'] > 0) & (m_df['Category'] == 'Income')]['Amount'].sum()
        exp_mask = (m_df['Amount'] < 0) & (m_df['Category'] != 'Transfer') & (m_df['Category'] != 'Income')
        exp = m_df[exp_mask]['Amount'].abs().sum()
        monthly_summary.append({'Month': month, 'Type': 'Income', 'Amount': inc})
        monthly_summary.append({'Month': month, 'Type': 'Expenses', 'Amount': exp})
        
    trend_df = pd.DataFrame(monthly_summary)
    
    st.subheader("Income vs Expenses")
    fig_main = px.bar(trend_df, x='Month', y='Amount', color='Type', barmode='group',
                      color_discrete_map={'Income': '#00CC96', 'Expenses': '#EF553B'})
    st.plotly_chart(fig_main, use_container_width=True)
    
    st.divider()
    st.subheader("Spending Categories over Time")
    
    exp_trend = history_df[(history_df['Amount'] < 0) & (history_df['Category'] != 'Transfer') & (history_df['Category'] != 'Income')].copy()
    exp_trend['Abs_Amount'] = exp_trend['Amount'].abs()
    cat_monthly = exp_trend.groupby(['Month', 'Category'])['Abs_Amount'].sum().reset_index()
    
    fig_line = px.line(
        cat_monthly, x='Month', y='Abs_Amount', color='Category', 
        markers=True, title="Category Trends",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_line.update_traces(mode="lines+markers")
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

# --- VIEW 3: FIXED VS VARIABLE ---
elif page == "⚖️ Fixed vs Variable":
    st.header("⚖️ Fixed vs Variable Analysis")
    
    exp_df = df[(df['Amount'] < 0) & (df['Category'] != 'Transfer') & (df['Category'] != 'Income')].copy()
    exp_df['Abs_Amount'] = exp_df['Amount'].abs()
    
    if exp_df.empty:
        st.warning("No data available.")
        st.stop()
        
    type_sum = exp_df.groupby("Type_Tag")["Abs_Amount"].sum().reset_index()
    
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(type_sum, values='Abs_Amount', names='Type_Tag', 
                         color='Type_Tag', color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'})
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("Ratio")
        total = type_sum['Abs_Amount'].sum()
        fixed_amt = type_sum[type_sum['Type_Tag']=='Fixed']['Abs_Amount'].sum()
        var_amt = type_sum[type_sum['Type_Tag']=='Variable']['Abs_Amount'].sum()
        
        st.metric("Fixed Costs", f"{fixed_amt:,.0f} NOK", f"{(fixed_amt/total*100):.1f}% of total")
        st.metric("Variable Costs", f"{var_amt:,.0f} NOK", f"{(var_amt/total*100):.1f}% of total")

    st.divider()
    st.subheader("History")
    exp_df['Month'] = exp_df['Date'].dt.strftime('%Y-%m')
    monthly_type = exp_df.groupby(['Month', 'Type_Tag'])['Abs_Amount'].sum().reset_index()
    
    fig_bar = px.bar(monthly_type, x='Month', y='Abs_Amount', color='Type_Tag', 
                     barmode='stack', color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'})
    st.plotly_chart(fig_bar, use_container_width=True)