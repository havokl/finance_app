import pandas as pd
import streamlit as st

def clean_bank_data(df):
    """
    Cleaning logic for the Norwegian Bank Format (Semicolon separated).
    """
    # 1. Filter out "Reservert" (pending)
    if 'Bokføringsdato' in df.columns:
        df = df[df['Bokføringsdato'] != 'Reservert']

    # 2. Rename Columns
    column_mapping = {
        'Bokføringsdato': 'Date',
        'Beløp': 'Amount',
        'Tittel': 'Description',
        'Navn': 'Description_Backup',
        'Betalingstype': 'Type' 
    }
    available_cols = [c for c in column_mapping.keys() if c in df.columns]
    df = df[available_cols].rename(columns=column_mapping)

    # 3. Clean Amount (Format: "1.000,00" -> 1000.00)
    if 'Amount' in df.columns and df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].astype(str)
        df['Amount'] = df['Amount'].str.replace('.', '', regex=False)
        df['Amount'] = df['Amount'].str.replace(',', '.', regex=False)
        df['Amount'] = pd.to_numeric(df['Amount'])

    # 4. Standardize Date (Bank uses YYYY/MM/DD often, or DD.MM.YYYY)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    df['Source'] = 'Bank Account'
    return df

def clean_amex_csv(df):
    """
    Cleaning logic for the Amex CSV format.
    Format: Dato, Beskrivelse, Beløp
    """
    # 1. Rename Columns
    column_mapping = {
        'Dato': 'Date',
        'Beløp': 'Amount',
        'Beskrivelse': 'Description'
    }
    existing_cols = [c for c in column_mapping.keys() if c in df.columns]
    df = df[existing_cols].rename(columns=column_mapping)

    # 2. Clean Amount
    # Amex CSV uses quoted numbers with comma decimals: "29,41"
    # AND it uses a special Unicode Minus Sign (\u2212) instead of hyphen.
    if 'Amount' in df.columns:
        # Ensure string
        df['Amount'] = df['Amount'].astype(str)
        # Replace Unicode Minus with standard hyphen
        df['Amount'] = df['Amount'].str.replace('\u2212', '-', regex=False)
        # Handle European decimal formatting
        df['Amount'] = df['Amount'].str.replace('.', '', regex=False) # Remove thousands sep if any
        df['Amount'] = df['Amount'].str.replace(',', '.', regex=False) # Comma to dot
        
        # Convert to float
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # 3. Flip Signs
        # Amex lists Expenses as Positive (e.g. 29.41). Bank lists them as Negative.
        # We want Expenses to be Negative.
        df['Amount'] = df['Amount'] * -1

    # 3. Standardize Date (Amex uses US format MM/DD/YYYY e.g. 01/30/2026)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

    df['Source'] = 'Credit Card'
    df['Type'] = 'Credit Card Transaction'
    return df

def process_files(uploaded_files):
    """
    Main entry point: Accepts a LIST of uploaded files, processes them, 
    and returns a single merged DataFrame.
    """
    all_dataframes = []

    for uploaded_file in uploaded_files:
        try:
            # 1. Peek at the first line to determine format
            # We read line, decode, and then reset file pointer
            first_line = uploaded_file.readline().decode('utf-8', errors='ignore')
            uploaded_file.seek(0) 

            # 2. Dispatch Logic
            if "Dato,Beskrivelse,Beløp" in first_line:
                # It's the AMEX CSV
                df_raw = pd.read_csv(uploaded_file)
                df_clean = clean_amex_csv(df_raw)
                all_dataframes.append(df_clean)
                
            elif ";" in first_line:
                # It's the BANK CSV (semicolon separated)
                try:
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='latin-1')
                
                df_clean = clean_bank_data(df_raw)
                all_dataframes.append(df_clean)
            
            else:
                # Fallback
                st.warning(f"Skipping {uploaded_file.name}: Unknown format.")
        
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    # 3. Merge all results
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Ensure Category exists
        if 'Category' not in final_df.columns:
            final_df['Category'] = 'Uncategorized'
            
        # Sort by Date
        final_df = final_df.sort_values(by='Date', ascending=False)
        return final_df
    
    return pd.DataFrame() # Return empty if nothing worked