import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files
import database
# We still need categories.py for the INITIAL seed and the Expense Types mapping
from categories import EXPENSE_TYPES, CATEGORY_RULES 

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")

# Initialize DB and Seed Rules if new
database.init_db()
database.seed_rules_if_empty(CATEGORY_RULES)

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

# --- 2. LOAD DATA ---
df = database.load_all_transactions()
uncat_count = len(df[df['Category'] == 'Uncategorized']) if not df.empty else 0

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("💰 Finance App")
    st.markdown("---")
    st.caption("MAIN MENU")
    
    cat_label = f"🔍 Categorization ({uncat_count})" if uncat_count > 0 else "🔍 Categorization"
    nav_options = {
        "📊 Monthly Dashboard": "dashboard",
        "📈 Long-term Trends": "trends",
        "⚖️ Fixed vs Variable": "fixed_var",
        cat_label: "categorization"
    }
    selection = st.radio("Navigate", list(nav_options.keys()), label_visibility="collapsed", key="main_nav")
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
        if st.button("🗑️ Clear Transactions"):
            database.clear_database()
            st.warning("Transactions cleared! Rules kept.")
            st.rerun()

if df.empty:
    st.info("👋 Welcome! Upload your first bank/credit card CSVs.")
    st.stop()

# --- GLOBAL PROCESSING ---
df['Month_Year'] = df['Date'].dt.to_period('M')
df['Type_Tag'] = df['Category'].map(EXPENSE_TYPES).fillna('Variable') 

# ==========================================
#      VIEW: CATEGORIZATION
# ==========================================
if page == "categorization":
    st.header("🔍 Categorization Center")
    
    # We use Tabs to separate "Fixing" from "Teaching"
    tab1, tab2 = st.tabs(["📝 Review Transactions", "🧠 Manage Rules"])
    
    # --- TAB 1: REVIEW ---
    with tab1:
        uncategorized_df = df[df['Category'] == 'Uncategorized'].copy()
        if uncategorized_df.empty:
            st.success("🎉 No uncategorized transactions!")
        else:
            st.info(f"Reviewing {len(uncategorized_df)} items.")
            valid_categories = sorted(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer'])
            
            edited_df = st.data_editor(
                uncategorized_df[['Date', 'Description', 'Amount', 'Category', 'id']], 
                column_config={
                    "Category": st.column_config.SelectboxColumn("Assign", options=valid_categories, required=True),
                    "id": None,
                    "Date": st.column_config.DatetimeColumn(disabled=True, format="D MMM"),
                    "Description": st.column_config.TextColumn(disabled=True),
                    "Amount": st.column_config.NumberColumn(disabled=True, format="%.0f")
                },
                hide_index=True, use_container_width=True, num_rows="fixed"
            )
            
            if st.button("💾 Save Changes", type="primary"):
                changes_count = 0
                for index, row in edited_df.iterrows():
                    if row['Category'] != 'Uncategorized':
                        if database.update_transaction_category(row['id'], row['Category']):
                            changes_count += 1
                if changes_count > 0:
                    st.toast(f"✅ Updated {changes_count} items!", icon="💾")
                    st.rerun()

    # --- TAB 2: RULE MANAGER (NEW!) ---
    with tab2:
        st.subheader("Teach the App")
        st.markdown("Add keywords here so the app learns automatically for next time.")
        
        # 1. Add New Rule
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            new_keyword = st.text_input("If description contains:", placeholder="e.g. NETFLIX")
        with c2:
            new_category = st.selectbox("Then categorize as:", sorted(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer']))
        with c3:
            st.write("") # Spacer
            st.write("") 
            if st.button("➕ Add Rule"):
                if new_keyword:
                    database.add_rule(new_keyword, new_category)
                    st.success(f"Added rule: {new_keyword} -> {new_category}")
                    st.rerun()
        
        st.divider()
        
        # 2. View/Delete Existing Rules
        st.subheader("Existing Rules")
        current_rules = database.load_rules_from_db()
        
        # Convert to DF for display
        rules_df = pd.DataFrame(list(current_rules.items()), columns=['Keyword', 'Category'])
        rules_df = rules_df.sort_values(by='Keyword')
        
        # We allow deleting rules via a dataframe with a checkbox
        rules_df['Delete'] = False
        
        edited_rules = st.data_editor(
            rules_df,
            column_config={
                "Keyword": st.column_config.TextColumn(disabled=True),
                "Category": st.column_config.TextColumn(disabled=True),
                "Delete": st.column_config.CheckboxColumn("Delete?", default=False)
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Check if deletions happened
        to_delete = edited_rules[edited_rules['Delete'] == True]
        if not to_delete.empty:
            if st.button(f"🗑️ Delete {len(to_delete)} Rules"):
                for keyword in to_delete['Keyword']:
                    database.delete_rule(keyword)
                st.rerun()


# ==========================================
#      VIEW: DASHBOARD (Standard)
# ==========================================
elif page == "dashboard":
    st.header("📊 Monthly Snapshot")
    available_months = sorted(df['Month_Year'].unique().astype(str), reverse=True)
    col_sel, _ = st.columns([1, 4])
    with col_sel: selected_month = st.selectbox("Select Month", ["All Time"] + available_months)
    view_df = df[df['Month_Year'].astype(str) == selected_month].copy() if selected_month != "All Time" else df.copy()

    # Metrics
    inc = view_df[(view_df['Amount'] > 0) & (view_df['Category'] == 'Income')]['Amount'].sum()
    exp_mask = (view_df['Amount'] < 0) & (view_df['Category'] != 'Transfer') & (view_df['Category'] != 'Income')
    exp = view_df[exp_mask]['Amount'].abs().sum()
    sav = inc - exp
    rate = (sav / inc * 100) if inc > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Income", f"{inc:,.0f}")
    m2.metric("Expenses", f"{exp:,.0f}")
    m3.metric("Savings", f"{sav:,.0f}")
    m4.metric("Rate", f"{rate:.1f}%")
    st.divider()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Spending")
        exp_df = view_df[exp_mask].copy()
        exp_df['Abs_Amount'] = exp_df['Amount'].abs()
        if not exp_df.empty:
            fig = px.pie(exp_df, values='Abs_Amount', names='Category', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Details")
        if not exp_df.empty:
            st.dataframe(exp_df[['Description', 'Amount', 'Category']].sort_values('Amount', ascending=True).head(10), use_container_width=True, hide_index=True)

# ==========================================
#      VIEW: TRENDS
# ==========================================
elif page == "trends":
    st.header("📈 Financial History")
    hist_df = df.copy()
    hist_df['Month'] = hist_df['Date'].dt.strftime('%Y-%m')
    
    # Bar Chart
    summ = []
    for m in sorted(hist_df['Month'].unique()):
        x = hist_df[hist_df['Month']==m]
        i = x[(x['Amount']>0)&(x['Category']=='Income')]['Amount'].sum()
        e = x[(x['Amount']<0)&(x['Category']!='Transfer')&(x['Category']!='Income')]['Amount'].abs().sum()
        summ.append({'Month':m, 'Type':'Income', 'Amount':i})
        summ.append({'Month':m, 'Type':'Expenses', 'Amount':e})
    
    st.subheader("Income vs Expenses")
    st.plotly_chart(px.bar(pd.DataFrame(summ), x='Month', y='Amount', color='Type', barmode='group', color_discrete_map={'Income': '#00CC96', 'Expenses': '#EF553B'}), use_container_width=True)
    
    # Line Chart
    st.subheader("Category Trends")
    et = hist_df[(hist_df['Amount']<0)&(hist_df['Category']!='Transfer')&(hist_df['Category']!='Income')].copy()
    et['Abs_Amount'] = et['Amount'].abs()
    line_data = et.groupby(['Month','Category'])['Abs_Amount'].sum().reset_index()
    st.plotly_chart(px.line(line_data, x='Month', y='Abs_Amount', color='Category', markers=True, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)

# ==========================================
#      VIEW: FIXED VS VARIABLE
# ==========================================
elif page == "fixed_var":
    st.header("⚖️ Fixed vs Variable")
    e = df[(df['Amount']<0)&(df['Category']!='Transfer')&(df['Category']!='Income')].copy()
    e['Abs_Amount'] = e['Amount'].abs()
    
    if not e.empty:
        c1, c2 = st.columns(2)
        grp = e.groupby('Type_Tag')['Abs_Amount'].sum().reset_index()
        with c1: st.plotly_chart(px.pie(grp, values='Abs_Amount', names='Type_Tag', color='Type_Tag', color_discrete_map={'Fixed':'#636EFA','Variable':'#EF553B'}), use_container_width=True)
        with c2:
            t = grp['Abs_Amount'].sum()
            f = grp[grp['Type_Tag']=='Fixed']['Abs_Amount'].sum()
            v = grp[grp['Type_Tag']=='Variable']['Abs_Amount'].sum()
            st.metric("Fixed", f"{f:,.0f}", f"{f/t*100:.1f}%")
            st.metric("Variable", f"{v:,.0f}", f"{v/t*100:.1f}%")