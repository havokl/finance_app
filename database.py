import sqlite3
import pandas as pd
import hashlib

DB_NAME = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Note: SQL is case-insensitive, but usually returns lowercase columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            source TEXT,
            type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_transaction_id(row):
    # Safely convert to string to generate hash
    date_str = str(row['Date'])
    desc_str = str(row['Description'])
    amt_str = str(row['Amount'])
    raw_str = f"{date_str}{desc_str}{amt_str}"
    return hashlib.md5(raw_str.encode()).hexdigest()

def save_transactions(df):
    if df.empty:
        return 0

    save_df = df.copy()

    # Ensure Date is string format YYYY-MM-DD for SQLite
    if 'Date' in save_df.columns:
        if not pd.api.types.is_datetime64_any_dtype(save_df['Date']):
             save_df['Date'] = pd.to_datetime(save_df['Date'], errors='coerce')
        save_df['Date'] = save_df['Date'].dt.strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    added_count = 0
    
    for _, row in save_df.iterrows():
        trans_id = generate_transaction_id(row)
        
        try:
            # We map the DataFrame capitalized columns to SQL lowercase columns
            c.execute('''
                INSERT INTO transactions (id, date, description, amount, category, source, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trans_id, 
                row['Date'], 
                row['Description'], 
                row['Amount'], 
                row['Category'], 
                row.get('Source', 'Unknown'), 
                row.get('Type', 'Unknown')
            ))
            added_count += 1
        except sqlite3.IntegrityError:
            pass 
            
    conn.commit()
    conn.close()
    return added_count

def load_all_transactions():
    conn = sqlite3.connect(DB_NAME)
    
    try:
        df = pd.read_sql("SELECT * FROM transactions", conn)
    except Exception:
        df = pd.DataFrame()
    
    conn.close()
    
    if not df.empty:
        # --- FIX: RENAME COLUMNS BACK TO TITLE CASE ---
        # SQL returns 'date', 'amount'. App needs 'Date', 'Amount'.
        df = df.rename(columns={
            'date': 'Date',
            'description': 'Description',
            'amount': 'Amount',
            'category': 'Category',
            'source': 'Source',
            'type': 'Type'
        })

        # Now we can safely access 'Date'
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
        if 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            
    return df

def clear_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()