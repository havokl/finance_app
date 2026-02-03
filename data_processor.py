import pandas as pd
import streamlit as st
import database

# Note: We no longer import CATEGORY_RULES from categories.py for processing.
# We fetch them live from the DB.

def categorize_transaction(description, db_rules):
    """
    Looks for keywords in the description using the rules from DB.
    """
    if not isinstance(description, str):
        return 'Uncategorized'
    
    description_upper = description.upper()
    
    # Iterate through the rules loaded from DB
    for keyword, category in db_rules.items():
        if keyword in description_upper:
            return category
            
    return 'Uncategorized'

# --- CLEANING FUNCTIONS (Same as before) ---
def clean_bank_data(df):
    if 'Bokføringsdato' in df.columns:
        df = df[df['Bokføringsdato'] != 'Reservert']
    column_mapping = {'Bokføringsdato': 'Date', 'Beløp': 'Amount', 'Tittel': 'Description', 'Navn': 'Description_Backup', 'Betalingstype': 'Type'}
    available_cols = [c for c in column_mapping.keys() if c in df.columns]
    df = df[available_cols].rename(columns=column_mapping)
    if 'Amount' in df.columns and df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Amount'] = pd.to_numeric(df['Amount'])
    if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Source'] = 'Bank Account'
    return df

def clean_amex_csv(df):
    column_mapping = {'Dato': 'Date', 'Beløp': 'Amount', 'Beskrivelse': 'Description'}
    existing_cols = [c for c in column_mapping.keys() if c in df.columns]
    df = df[existing_cols].rename(columns=column_mapping)
    if 'Amount' in df.columns:
        df['Amount'] = df['Amount'].astype(str).str.replace('\u2212', '-', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce') * -1
    if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['Source'] = 'Credit Card'
    df['Type'] = 'Credit Card Transaction'
    return df

def process_files(uploaded_files):
    all_dataframes = []
    
    # 1. LOAD RULES FROM DB ONCE
    db_rules = database.load_rules_from_db()

    for uploaded_file in uploaded_files:
        try:
            first_line = uploaded_file.readline().decode('utf-8', errors='ignore')
            uploaded_file.seek(0) 

            if "Dato,Beskrivelse,Beløp" in first_line:
                df_raw = pd.read_csv(uploaded_file)
                df_clean = clean_amex_csv(df_raw)
                all_dataframes.append(df_clean)
            elif ";" in first_line:
                try:
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='latin-1')
                df_clean = clean_bank_data(df_raw)
                all_dataframes.append(df_clean)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # 2. PASS DB RULES TO FUNCTION
        if 'Description' in final_df.columns:
            final_df['Category'] = final_df['Description'].apply(lambda x: categorize_transaction(x, db_rules))
        else:
            final_df['Category'] = 'Uncategorized'
            
        final_df = final_df.sort_values(by='Date', ascending=False)
        return final_df
    
    return pd.DataFrame()