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

# --- 2. LOAD DATA EARLY (Needed for Sidebar Logic) ---
df = database.load_all_transactions()

# Calculate uncategorized count for the menu label
uncat_count = 0
if not df.empty:
    uncat_count = len(df[df['Category'] == 'Uncategorized'])

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("💰 Finance App")
    st.markdown("---")
    
    st.caption("MAIN MENU")
    
    # Dynamic Label: Show count if there is work to do
    cat_label = f"🔍 Categorization ({uncat_count})" if uncat_count > 0 else "🔍 Categorization"
    
    # Map the display label back to the internal key
    nav_options = {
        "📊 Monthly Dashboard": "dashboard",
        "📈 Long-term Trends": "trends",
        "⚖️ Fixed vs Variable": "fixed_var",
        cat_label: "categorization"
    }
    
    selection = st.radio(
        "Navigate", 
        list(nav_options.keys()),
        label_visibility="collapsed",
        key="main_nav"
    )
    
    # Get the internal page key (so logic doesn't break when label changes)
    page = nav_options[selection]
    
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

# Stop if no data
if df.empty:
    st.info("👋 Welcome! Upload your first bank/credit card CSVs in the sidebar to get started.")
    st.stop()

# --- GLOBAL PROCESSING ---
df['Month_Year'] = df['Date'].dt.to_period('M')
df['Type_Tag'] = df['Category'].map(EXPENSE_TYPES).fillna('Variable') 


# ==========================================
#      VIEW: CATEGORIZATION (The New Pane)
# ==========================================
if page == "categorization":
    st.header("🔍 Categorization")
    
    uncategorized_df = df[df['Category'] == 'Uncategorized'].copy()
    
    if uncategorized_df.empty:
        st.balloons()
        st.success("🎉 All caught up! Every transaction is categorized.")
        st.info("Upload more CSVs to see new items here.")
    else:
        st.info(f"You have **{len(uncategorized_df)}** transactions to review.")
        
        # Get list of valid categories from your settings + standard system ones
        valid_categories = sorted(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer'])
        
        # Configure the editor
        edited_df = st.data_editor(
            uncategorized_df[['Date', 'Description', 'Amount', 'Category', 'id']], 
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Assign Category",
                    help="Select the correct category",
                    width="medium",
                    options=valid_categories,
                    required=True,
                ),
                "id": None, # Hide ID
                "Date": st.column_config.DatetimeColumn(disabled=True, format="D MMM YYYY"),
                "Description": st.column_config.TextColumn(disabled=True),
                "Amount": st.column_config.NumberColumn(disabled=True, format="NOK %.2f")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_uncat",
            num_rows="fixed" # Prevent adding new rows
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                changes_count = 0
                
                for index, row in edited_df.iterrows():
                    # We check against the original DF to find what changed
                    # (Streamlit data editor output has same index as input)
                    original_cat = uncategorized_df.loc[index, 'Category']
                    
                    if row['Category'] != original_cat:
                        success = database.update_transaction_category(row['id'], row['Category'])
                        if success:
                            changes_count += 1
                
                if changes_count > 0:
                    st.toast(f"✅ Updated {changes_count} transactions!", icon="💾")
                    st.rerun()
                else:
                    st.info("No changes detected.")


# ==========================================
#      VIEW: MONTHLY DASHBOARD
# ==========================================
elif page == "dashboard":
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


# ==========================================
#      VIEW: LONG-TERM TRENDS
# ==========================================
elif page == "trends":
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


# ==========================================
#      VIEW: FIXED VS VARIABLE
# ==========================================
elif page == "fixed_var":
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