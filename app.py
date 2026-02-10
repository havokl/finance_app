import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data_processor import process_files
from streamlit_option_menu import option_menu
import database
from categories import EXPENSE_TYPES, CATEGORY_RULES 



# --- CONFIGURATION ---
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")
database.init_db()

# Seed the database with your existing python files on startup
database.seed_rules_if_empty(CATEGORY_RULES)
database.seed_categories_if_empty(EXPENSE_TYPES)

# Fetch dynamic configuration
ALL_CATEGORIES = database.get_categories() # Returns dict {'Rent': 'Fixed', ...}
CATEGORY_LIST = list(ALL_CATEGORIES.keys())

# --- DYNAMIC COLOR GENERATOR ---
# Since categories are now dynamic, we can't hardcode all colors.
# This function maps your known colors and generates grey/random for new ones.
def get_category_color_map():
    base_colors = {
        "Groceries": "#AED581", "Dining/Drinks": "#FF8A65", "Rent": "#64B5F6",
        "Mortgage": "#42A5F5", "Utilities": "#FFD54F", "Travel": "#4DB6AC",
        "Shopping": "#BA68C8", "Car": "#90A4AE", "Insurance": "#E57373",
        "Subscriptions": "#9575CD", "Saving": "#81C784", "Income": "#66BB6A",
        "Transfer": "#E0E0E0", "Uncategorized": "#E0E0E0"
    }
    # Ensure every category in DB has a color (default to grey if unknown)
    full_map = {}
    for cat in CATEGORY_LIST:
        full_map[cat] = base_colors.get(cat, "#CFD8DC") # Default Grey
    return full_map

CATEGORY_COLORS = get_category_color_map()

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
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LOAD DATA ---
df = database.load_all_transactions()
uncat_count = len(df[df['Category'] == 'Uncategorized']) if not df.empty else 0


# --- SIDEBAR: NAVIGATION ---
# Change "selected_tab" to "selected"
with st.sidebar:
    st.header("Navigation")
    selected = option_menu(  # <--- Rename this from selected_tab to selected
        menu_title=None,
        options=["Dashboard", "Trends", "Categorize", "Settings"], 
        icons=["speedometer2", "graph-up", "tags", "gear"],
        default_index=0,
    )

  
    page_map = {
    "Dashboard": "dashboard", 
    "Trends": "trends", 
    "Categorize": "categorization", 
    "Settings": "settings"
    }

    page = page_map[selected]

    st.divider()
    
    uploaded_files = st.file_uploader("Upload Bank CSVs", accept_multiple_files=True)
    
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
    # ... (After your existing file_uploader code) ...

    st.divider()
    
    # --- DATA MANAGEMENT (Backup/Restore) ---
    with st.expander("💾 Data Management"):
        st.caption("Backup your categorized data or restore a previous version.")
        
        # 1. DOWNLOAD (Backup)
        with open("finance.db", "rb") as fp:
            btn = st.download_button(
                label="Download Backup",
                data=fp,
                file_name=f"finance_backup_{datetime.now().strftime('%Y%m%d')}.db",
                mime="application/x-sqlite3",
                help="Click to save a copy of your database to your computer."
            )
        
        st.markdown("---")
        
        # 2. UPLOAD (Restore)
        restore_file = st.file_uploader("Restore Backup", type=["db"], key="restore_uploader")
        
        if restore_file:
            # Add a confirmation button to prevent accidental overwrites
            if st.button("⚠️ Confirm Restore"):
                if database.restore_db(restore_file):
                    st.success("Database restored successfully!")
                    st.rerun() # Force a reload to show the restored data
                else:
                    st.error("Failed to restore database.")
    
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
df['Type_Tag'] = df['Category'].map(ALL_CATEGORIES).fillna('Variable') 

# ==========================================
#      VIEW: CATEGORIZATION
# ==========================================
if page == "categorization":
    st.header("📝 Review Transactions")
    
    # Calculate progress
    total_tx = len(df)
    uncat_tx = len(df[df['Category'] == 'Uncategorized'])
    progress = int(((total_tx - uncat_tx) / total_tx) * 100) if total_tx > 0 else 100

    if uncat_tx > 0:
        st.warning(f"🚨 {uncat_tx} transactions need your attention!")
        st.progress(progress, text=f"Categorization Progress: {progress}%")
    else:
        st.balloons()
        st.success("🎉 All caught up! Great job.")

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
        valid_categories = sorted(list(set(list(ALL_CATEGORIES.keys()) + ['Income', 'Transfer'])))
        
        # 3. Configure Editor: Enable Amount editing
        edited_df = st.data_editor(
            display_df[['Date', 'Description', 'Amount', 'Category', 'id']], 
            column_config={
                "Category": st.column_config.SelectboxColumn("Assign", options=valid_categories, required=True),
                "id": None, # Hidden
                "Date": st.column_config.DatetimeColumn(disabled=True, format="D MMM"),
                "Description": st.column_config.TextColumn(disabled=True),
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
            
            for index, row in edited_df.iterrows():
                trans_id = row['id']
                original_rows = df[df['id'] == trans_id]
                
                if not original_rows.empty:
                    original_row = original_rows.iloc[0]
                    
                    # Check 1: Category Change
                    if row['Category'] != original_row['Category']:
                        if row['Category'] != 'Uncategorized':
                            if database.update_transaction_category(trans_id, row['Category']):
                                changes_count += 1

                    # Check 2: Amount Change
                    if abs(row['Amount'] - original_row['Amount']) > 0.01:
                        if database.update_transaction_amount(trans_id, row['Amount']):
                            changes_count += 1
            
            if changes_count > 0:
                st.toast(f"✅ Updated {changes_count} items!", icon="💾")
                st.rerun()
            else:
                st.info("No changes detected.")




# ==========================================
#       VIEW: MONTHLY DASHBOARD
# ==========================================
elif page == "dashboard":
    st.header("📊 Monthly Snapshot")
    
    # 1. Get available months
    # Ensure Month_Year exists
    if 'Month_Year' not in df.columns and not df.empty:
        df['Month_Year'] = df['Date'].dt.to_period('M').astype(str)

    available_months = sorted(df['Month_Year'].unique().astype(str), reverse=True)
    
    # 2. Set up Options and Default Selection
    options = ["All Time"] + available_months
    current_month_str = datetime.now().strftime('%Y-%m')
    
    # Determine which index to select by default
    if current_month_str in options:
        default_index = options.index(current_month_str)
    elif len(available_months) > 0:
        default_index = 1 # Default to latest available if current is missing
    else:
        default_index = 0

    col_sel, _ = st.columns([1, 4])
    with col_sel: 
        selected_month = st.selectbox(
            "Select Month", 
            options, 
            index=default_index,
            format_func=lambda x: "All Time" if x == "All Time" else datetime.strptime(x, '%Y-%m').strftime('%B %Y')
        )

    # 3. FILTER DATA (Current vs Previous)
    
    # A. Current Selection Data
    if selected_month == "All Time":
        view_df = df.copy()
        prev_df = pd.DataFrame() # No comparison for All Time
    else:
        view_df = df[df['Month_Year'].astype(str) == selected_month].copy()
        
        # B. Calculate Previous Month String
        sel_date = datetime.strptime(selected_month, "%Y-%m")
        # Go back one month
        if sel_date.month == 1:
            prev_month = 12
            prev_year = sel_date.year - 1
        else:
            prev_month = sel_date.month - 1
            prev_year = sel_date.year
            
        prev_month_str = f"{prev_year}-{prev_month:02d}"
        
        # C. Previous Month Data
        prev_df = df[df['Month_Year'].astype(str) == prev_month_str].copy()

    # 4. CALCULATE METRICS (Current)
    inc = view_df[(view_df['Amount'] > 0) & (view_df['Category'] == 'Income')]['Amount'].sum()
    
    exp_mask = (view_df['Amount'] < 0) & (view_df['Category'] != 'Transfer') & (view_df['Category'] != 'Income')
    expenses_df = view_df[exp_mask].copy()
    expenses_df['Abs_Amount'] = expenses_df['Amount'].abs()
    
    exp = expenses_df['Abs_Amount'].sum()
    sav = inc - exp
    rate = (sav / inc * 100) if inc > 0 else 0

    # 5. CALCULATE METRICS (Previous)
    if not prev_df.empty:
        prev_inc = prev_df[(prev_df['Amount'] > 0) & (prev_df['Category'] == 'Income')]['Amount'].sum()
        
        prev_exp_mask = (prev_df['Amount'] < 0) & (prev_df['Category'] != 'Transfer') & (prev_df['Category'] != 'Income')
        prev_exp = prev_df[prev_exp_mask]['Amount'].abs().sum()
        
        prev_sav = prev_inc - prev_exp
        
        # Deltas
        inc_delta = inc - prev_inc
        exp_delta = exp - prev_exp 
        sav_delta = sav - prev_sav
    else:
        # If "All Time" or no previous data, deltas are 0
        inc_delta, exp_delta, sav_delta = 0, 0, 0

    # 6. DISPLAY METRICS ROW (Bento Box Style)
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Income", f"{inc:,.0f} kr", delta=f"{inc_delta:,.0f} kr", delta_color="normal")
    with col2: 
        # Note: If exp_delta is Positive (e.g. 5000), it means we spent 5000 MORE. 
        # Standard delta_color="inverse" turns Positive Red (Bad) and Negative Green (Good).
        st.metric("Expenses", f"{exp:,.0f} kr", delta=f"{exp_delta:,.0f} kr", delta_color="inverse")
    with col3: 
        st.metric("Savings", f"{sav:,.0f} kr", delta=f"{sav_delta:,.0f} kr", delta_color="normal")
    with col4: 
        Savings_rate = ((inc-exp)/inc)*100 if (inc-exp)/inc > 0 else 0
        st.metric("Saving Rate", f"{Savings_rate:.0f}%")

    st.markdown("---")

    # 7. CHARTS ROW (2:1 Ratio)
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Spending Structure")
        if not expenses_df.empty:
            # Create two internal columns for Fixed vs Variable
            col_fixed, col_var = st.columns(2)
            
            # --- Chart 1: Fixed ---
            with col_fixed:
                # 1. Filter Data First
                fixed_df = expenses_df[expenses_df['Type_Tag'] == 'Fixed']
                # 2. Calculate Total
                fixed_total = fixed_df['Abs_Amount'].sum() if not fixed_df.empty else 0
                
                # 3. Display Header with Total
                st.markdown(f"**🔒 Fixed: {fixed_total:,.0f} kr**")
                
                if not fixed_df.empty:
                    fig_fixed = px.pie(fixed_df, values='Abs_Amount', names='Category', 
                                     hole=0.5, 
                                     color='Category',
                                     color_discrete_map=CATEGORY_COLORS)
                    # Hide legend to keep the split view clean
                    fig_fixed.update_traces(hovertemplate='%{label}: %{value:,.0f} kr')
                    fig_fixed.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
                    st.plotly_chart(fig_fixed, use_container_width=True)
                else:
                    st.info("No fixed expenses.")

            # --- Chart 2: Variable ---
            with col_var:
                # 1. Filter Data First
                var_df = expenses_df[expenses_df['Type_Tag'] == 'Variable']
                # 2. Calculate Total
                var_total = var_df['Abs_Amount'].sum() if not var_df.empty else 0
                
                # 3. Display Header with Total
                st.markdown(f"**🛒 Variable: {var_total:,.0f} kr**")
                
                if not var_df.empty:
                    fig_var = px.pie(var_df, values='Abs_Amount', names='Category', 
                                   hole=0.5, 
                                   color='Category',
                                   color_discrete_map=CATEGORY_COLORS)
                    fig_var.update_traces(hovertemplate='%{label}: %{value:,.0f} kr')
                    fig_var.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
                    st.plotly_chart(fig_var, use_container_width=True)
                else:
                    st.info("No variable expenses.")
        else:
            st.info("No expenses found.")

    with c2:
        st.subheader("Top Expenses")
        if not expenses_df.empty:
            # Clean Table View
            top_exp = expenses_df[['Description', 'Amount', 'Category']].sort_values('Amount', ascending=True).head(8)
            st.dataframe(
                top_exp, 
                column_config={
                    "Amount": st.column_config.NumberColumn(format="kr %.0f"),
                    "Description": st.column_config.TextColumn(width="medium"),
                },
                hide_index=True, 
                use_container_width=True
            )
        else:
            st.info("No data.")

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
            # Label cleanup
            fig_fv.update_traces(hovertemplate='%{label}: %{value:,.0f} kr')
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
    
   # 2. Category Trends (IMPROVED & POLISHED)
    st.divider()
    st.subheader("Category Trends")

    # PREPARE DATA
    et = hist_df[
        (hist_df['Amount'] < 0) & 
        (hist_df['Category'] != 'Transfer') & 
        (hist_df['Category'] != 'Income')
    ].copy()
    et['Abs_Amount'] = et['Amount'].abs()
    
    # AGGREGATE MONTHLY
    trend_data = et.groupby(['Month', 'Category'])['Abs_Amount'].sum().reset_index()

    # UI CONTROLS
    c_ctrl1, c_ctrl2 = st.columns([2, 1])
    
    with c_ctrl1:
        # Filter for 'Variable' expenses first
        variable_only = et[et['Type_Tag'] == 'Variable']
        
        # Get the top 7 largest VARIABLE categories
        top_variable_cats = variable_only.groupby('Category')['Abs_Amount'].sum().nlargest(7).index.tolist()
        
        selected_cats = st.multiselect(
            "Select Categories to Compare:",
            options=sorted(trend_data['Category'].unique()), # All categories still available as options
            default=top_variable_cats # Default selection is now specific to Variable
        )
        
    with c_ctrl2:
        chart_type = st.selectbox("Chart Type", ["Area Chart","Line Chart", "Stacked Bar" ])

    # FILTER & PLOT
    if selected_cats:
        filtered_data = trend_data[trend_data['Category'].isin(selected_cats)]
        
        # --- COMMON CHART SETTINGS ---
        # We define labels here once to use in all charts
        chart_labels = {
            "Abs_Amount": "Amount",  # <--- Renames 'Abs_Amount' to 'Amount'
            "Month": "Date",
            "Category": "Category"
        }

        if chart_type == "Stacked Bar":
            fig = px.bar(
                filtered_data, x='Month', y='Abs_Amount', color='Category', 
                color_discrete_map=CATEGORY_COLORS,
                labels=chart_labels # Apply labels
            )
        elif chart_type == "Area Chart":
            fig = px.area(
                filtered_data, x='Month', y='Abs_Amount', color='Category', 
                color_discrete_map=CATEGORY_COLORS,
                labels=chart_labels # Apply labels
            )
        else:
            fig = px.line(
                filtered_data, x='Month', y='Abs_Amount', color='Category', 
                markers=True, 
                color_discrete_map=CATEGORY_COLORS,
                labels=chart_labels # Apply labels
            )

        # --- APPLY DATE FORMATTING TO HOVER ---
        # %B = Full Month Name (July), %Y = Year (2025)
        fig.update_traces(xhoverformat="%B %Y") 
        
        fig.update_layout(height=450, xaxis_title=None, yaxis_title="Amount (NOK)")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Select at least one category above to see the trends.")
    # --- INTEGRATED FIXED VS VARIABLE HISTORY ---
    st.divider()
    st.subheader("⚖️ Fixed vs Variable Expenses Over TSime")
    
    # Reuse 'et' dataframe (Expenses Only)
    monthly_type = et.groupby(['Month', 'Type_Tag'])['Abs_Amount'].sum().reset_index()
    
    fig_bar = px.bar(monthly_type, x='Month', y='Abs_Amount', color='Type_Tag', 
                     barmode='stack', 
                     title="Are your fixed expenses growing?",
                     color_discrete_map={'Fixed': '#636EFA', 'Variable': '#EF553B'})
    st.plotly_chart(fig_bar, use_container_width=True)


# ... (after all the logic for Dashboard, Trends, and Categorize) ...

if selected == "Settings":
    st.title("⚙️ Settings & Management")
    
    col1, col2 = st.columns(2)
    
    # --- LEFT COLUMN: CATEGORIES ---
    with col1:
        st.subheader("📂 Manage Categories")
        st.write("Add new spending categories here.")
        
        # Add New Category
        with st.form("add_cat_form"):
            new_cat_name = st.text_input("New Category Name")
            new_cat_type = st.selectbox("Type", ["Variable", "Fixed"])
            submitted = st.form_submit_button("Add Category")
            
            if submitted and new_cat_name:
                if new_cat_name in ALL_CATEGORIES:
                    st.warning("Category already exists.")
                else:
                    database.add_category(new_cat_name, new_cat_type)
                    st.success(f"Added {new_cat_name}!")
                    st.rerun()

        # List / Delete Categories
        st.divider()
        st.write("Existing Categories:")
        for cat, type_tag in ALL_CATEGORIES.items():
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.text(cat)
            c2.caption(type_tag)
            if c3.button("🗑️", key=f"del_{cat}"):
                database.delete_category(cat)
                st.rerun()

    # --- RIGHT COLUMN: RULES ---
    with col2:
        st.subheader("🧠 Manage Rules")
        st.write("Automate categorization based on keywords.")
        
        c_r1, c_r2 = st.columns([2, 2])
        with c_r1: 
            new_keyword = st.text_input("If description contains:", placeholder="e.g. NETFLIX")
        with c_r2: 
            # Income/Transfer + Dynamic Categories
            rule_cats = sorted(list(set(list(ALL_CATEGORIES.keys()) + ['Income', 'Transfer'])))
            new_category = st.selectbox("Assign Category:", rule_cats)
            
        if st.button("➕ Add Rule") and new_keyword:
            database.add_rule(new_keyword, new_category)
            st.success(f"Added rule: {new_keyword} -> {new_category}")
            st.rerun()
        
        st.divider()
        
        # Rule Editor
        rules = database.load_rules_from_db()
        rules_df = pd.DataFrame(list(rules.items()), columns=['Keyword', 'Category']).sort_values('Keyword')
        rules_df['Delete'] = False # Add checkbox column
        
        edited_rules = st.data_editor(
            rules_df, 
            column_config={
                "Keyword": st.column_config.TextColumn(disabled=True), 
                "Category": st.column_config.TextColumn(disabled=True)
            }, 
            hide_index=True, 
            use_container_width=True
        )
        
        # Delete Logic
        to_delete = edited_rules[edited_rules['Delete'] == True]
        if not to_delete.empty:
            if st.button(f"🗑️ Delete {len(to_delete)} Rules"):
                for k in to_delete['Keyword']: 
                    database.delete_rule(k)
                st.rerun()

        # Export Logic
        st.markdown("---")
        with st.expander("📤 View Python Dictionary (Advanced)"):
            st.caption("Use this if you want to update categories.py manually.")
            sorted_items = sorted(rules.items(), key=lambda item: (item[1], item[0]))
            dict_str = "CATEGORY_RULES = {\n"
            current_category = ""
            for keyword, category in sorted_items:
                if category != current_category:
                    dict_str += f"\n    # --- {category} ---\n"
                    current_category = category
                dict_str += f"    '{keyword}': '{category}',\n"
            dict_str += "}"
            st.code(dict_str, language='python')