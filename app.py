import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_files
import database
from categories import EXPENSE_TYPES, CATEGORY_RULES 

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")
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
    
    # REMOVED "Fixed vs Variable" from the menu
    nav_options = {
        "📊 Monthly Dashboard": "dashboard",
        "📈 Long-term Trends": "trends",
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
    tab1, tab2 = st.tabs(["📝 Review Transactions", "🧠 Manage Rules"])
    
    # ... inside app.py (inside the 'categorization' page block)

    with tab1:
        # 1. Allow toggling between "Uncategorized Only" and "All Transactions"
        col_filter, _ = st.columns([1, 3])
        with col_filter:
            show_all = st.toggle("Show all transactions", value=False)
        
        # 2. Filter the dataframe based on toggle
        if show_all:
            display_df = df.copy() # Edit anything
            st.info(f"Showing all {len(display_df)} transactions.")
        else:
            display_df = df[df['Category'] == 'Uncategorized'].copy() # Standard workflow
            if display_df.empty:
                st.success("🎉 No uncategorized transactions!")
            else:
                st.info(f"Reviewing {len(display_df)} items.")

        if not display_df.empty:
            valid_categories = sorted(list(set(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer'])))
            
            # 3. Configure Editor: Enable Amount editing
            edited_df = st.data_editor(
                display_df[['Date', 'Description', 'Amount', 'Category', 'id']], 
                column_config={
                    "Category": st.column_config.SelectboxColumn("Assign", options=valid_categories, required=True),
                    "id": None, # Hidden
                    "Date": st.column_config.DatetimeColumn(disabled=True, format="D MMM"),
                    "Description": st.column_config.TextColumn(disabled=True),
                    # CHANGE: Set disabled=False so you can edit amounts
                    "Amount": st.column_config.NumberColumn(label="Amount", disabled=False, format="%.0f", required=True)
                },
                hide_index=True, 
                use_container_width=True, 
                num_rows="fixed",
                key="editor_cat"
            )
            
            # 4. Save Logic: Detect Category OR Amount changes
            if st.button("💾 Save Changes", type="primary"):
                changes_count = 0
                
                # We iterate through the EDITED dataframe
                for index, row in edited_df.iterrows():
                    trans_id = row['id']
                    
                    # Find the ORIGINAL row in the main dataframe to compare values
                    # (We use safe indexing in case the ID is somehow missing, though unlikely)
                    original_rows = df[df['id'] == trans_id]
                    
                    if not original_rows.empty:
                        original_row = original_rows.iloc[0]
                        
                        # Check 1: Did Category Change?
                        if row['Category'] != original_row['Category']:
                            # Only update if it's not 'Uncategorized' (force user to choose a real category)
                            if row['Category'] != 'Uncategorized':
                                if database.update_transaction_category(trans_id, row['Category']):
                                    changes_count += 1

                        # Check 2: Did Amount Change? (Float comparison with small tolerance)
                        if abs(row['Amount'] - original_row['Amount']) > 0.01:
                            if database.update_transaction_amount(trans_id, row['Amount']):
                                changes_count += 1
                
                if changes_count > 0:
                    st.toast(f"✅ Updated {changes_count} items!", icon="💾")
                    st.rerun()
                else:
                    st.info("No changes detected.")

    with tab2:
        st.subheader("Teach the App")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: new_keyword = st.text_input("If description contains:", placeholder="e.g. NETFLIX")
        with c2: new_category = st.selectbox("Then categorize as:", sorted(list(set(list(EXPENSE_TYPES.keys()) + ['Income', 'Transfer']))))
        with c3:
            st.write("") 
            st.write("") 
            if st.button("➕ Add Rule") and new_keyword:
                database.add_rule(new_keyword, new_category)
                st.success(f"Added: {new_keyword}")
                st.rerun()
        
        st.divider()
        rules_df = pd.DataFrame(list(database.load_rules_from_db().items()), columns=['Keyword', 'Category']).sort_values('Keyword')
        rules_df['Delete'] = False
        edited_rules = st.data_editor(rules_df, column_config={"Keyword": st.column_config.TextColumn(disabled=True), "Category": st.column_config.TextColumn(disabled=True)}, hide_index=True, use_container_width=True)
        to_delete = edited_rules[edited_rules['Delete'] == True]
        if not to_delete.empty:
            if st.button(f"🗑️ Delete {len(to_delete)} Rules"):
                for k in to_delete['Keyword']: database.delete_rule(k)
                st.rerun()
        if not to_delete.empty:
            if st.button(f"🗑️ Delete {len(to_delete)} Rules"):
                for k in to_delete['Keyword']: database.delete_rule(k)
                st.rerun()

        # --- NEW CODE STARTS HERE ---
        st.markdown("---")
        st.subheader("📤 Export for categories.py")
        st.caption("Copy this code and replace the CATEGORY_RULES dictionary in your categories.py file.")
        
        # 1. Load current live rules
        current_rules = database.load_rules_from_db()
        
        # 2. Sort by Category first (item[1]), then by Keyword (item[0])
        # This groups all "Groceries" together, then all "Income" together, etc.
        sorted_items = sorted(current_rules.items(), key=lambda item: (item[1], item[0]))
        
        # 3. Build the string
        dict_str = "CATEGORY_RULES = {\n"
        
        # We can also add comments to separate the groups visually
        current_category = ""
        for keyword, category in sorted_items:
            # Optional: Add a comment header when the category changes
            if category != current_category:
                dict_str += f"\n    # --- {category} ---\n"
                current_category = category
            
            dict_str += f"    '{keyword}': '{category}',\n"
            
        dict_str += "}"
        
        # 4. Display
        st.code(dict_str, language='python')



# ==========================================
#      VIEW: MONTHLY DASHBOARD
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
    expenses_df = view_df[exp_mask].copy()
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    exp = expenses_df['Abs_Amount'].sum()
    sav = inc - exp
    rate = (sav / inc * 100) if inc > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Income", f"{inc:,.0f}")
    m2.metric("Expenses", f"{exp:,.0f}")
    m3.metric("Savings", f"{sav:,.0f}")
    m4.metric("Rate", f"{rate:.1f}%")
    st.divider()
    
    # 1. Main Spending Pie & Top Expenses
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Spending Breakdown")
        if not expenses_df.empty:
            fig = px.pie(expenses_df, values='Abs_Amount', names='Category', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses data.")
            
    with c2:
        st.subheader("Top Expenses")
        if not expenses_df.empty:
            st.dataframe(expenses_df[['Description', 'Amount', 'Category']].sort_values('Amount', ascending=True).head(10).style.format({'Amount': "{:.0f}"}), use_container_width=True, hide_index=True)

    with st.expander("📄 View All Transactions"):
        st.dataframe(view_df[['Date', 'Description', 'Category', 'Amount']].sort_values(by='Date', ascending=False), use_container_width=True)

    # --- INTEGRATED FIXED VS VARIABLE SECTION ---
    st.divider()
    st.subheader("⚖️ Fixed vs Variable (Monthly Analysis)")
    
    if not expenses_df.empty:
        # Calculate stats for the VIEWED period
        type_sum = expenses_df.groupby("Type_Tag")["Abs_Amount"].sum().reset_index()
        total_period = type_sum['Abs_Amount'].sum()
        
        # Safe getters for Fixed/Variable sums
        fixed_row = type_sum[type_sum['Type_Tag']=='Fixed']
        fixed_amt = fixed_row['Abs_Amount'].sum() if not fixed_row.empty else 0
        
        var_row = type_sum[type_sum['Type_Tag']=='Variable']
        var_amt = var_row['Abs_Amount'].sum() if not var_row.empty else 0
        
        fv_c1, fv_c2 = st.columns([1, 1])
        with fv_c1:
            fig_fv = px.pie(type_sum, values='Abs_Amount', names='Type_Tag', 
                            color='Type_Tag', 
                            color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'},
                            title="Structure")
            st.plotly_chart(fig_fv, use_container_width=True)
            
        with fv_c2:
            st.markdown("### Breakdown")
            st.metric("Fixed Costs (Needs)", f"{fixed_amt:,.0f} NOK", f"{(fixed_amt/total_period*100):.1f}%")
            st.metric("Variable Costs (Wants)", f"{var_amt:,.0f} NOK", f"{(var_amt/total_period*100):.1f}%")
            st.info("💡 **Target:** Fixed costs should ideally be < 50% of your income.")

# ==========================================
#      VIEW: LONG TERM TRENDS
# ==========================================
elif page == "trends":
    st.header("📈 Financial History")
    hist_df = df.copy()
    hist_df['Month'] = hist_df['Date'].dt.strftime('%Y-%m')
    
    # 1. Income vs Expenses
    summ = []
    for m in sorted(hist_df['Month'].unique()):
        x = hist_df[hist_df['Month']==m]
        i = x[(x['Amount']>0)&(x['Category']=='Income')]['Amount'].sum()
        e = x[(x['Amount']<0)&(x['Category']!='Transfer')&(x['Category']!='Income')]['Amount'].abs().sum()
        summ.append({'Month':m, 'Type':'Income', 'Amount':i})
        summ.append({'Month':m, 'Type':'Expenses', 'Amount':e})
    
    st.subheader("Income vs Expenses")
    st.plotly_chart(px.bar(pd.DataFrame(summ), x='Month', y='Amount', color='Type', barmode='group', color_discrete_map={'Income': '#00CC96', 'Expenses': '#EF553B'}), use_container_width=True)
    
    # 2. Category Line Chart
    st.divider()
    st.subheader("Category Trends")
    et = hist_df[(hist_df['Amount']<0)&(hist_df['Category']!='Transfer')&(hist_df['Category']!='Income')].copy()
    et['Abs_Amount'] = et['Amount'].abs()
    line_data = et.groupby(['Month','Category'])['Abs_Amount'].sum().reset_index()
    st.plotly_chart(px.line(line_data, x='Month', y='Abs_Amount', color='Category', markers=True, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)

    # --- INTEGRATED FIXED VS VARIABLE HISTORY ---
    st.divider()
    st.subheader("⚖️ Lifestyle Inflation (Fixed vs Variable over time)")
    
    # Reuse 'et' dataframe (Expenses Only)
    monthly_type = et.groupby(['Month', 'Type_Tag'])['Abs_Amount'].sum().reset_index()
    
    fig_bar = px.bar(monthly_type, x='Month', y='Abs_Amount', color='Type_Tag', 
                     barmode='stack', 
                     title="Are your fixed costs growing?",
                     color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'})
    st.plotly_chart(fig_bar, use_container_width=True)