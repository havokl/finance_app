import sqlite3
import pandas as pd
import hashlib
import shutil
import os

DB_NAME = "finance.db"

# --- 1. TABLE MANAGEMENT ---
# database.py
import sqlite3

# ... existing code ...

# --- 1. TABLE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # ... existing transactions table ...
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
    
    # ... existing rules table ...
    c.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            keyword TEXT PRIMARY KEY,
            category TEXT
        )
    ''')

    # NEW: Categories Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY,
            type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# --- CATEGORY MANAGEMENT ---
def get_categories():
    """Returns a dictionary {category_name: type} (e.g., {'Rent': 'Fixed'})"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT name, type FROM categories")
        data = c.fetchall()
        return {name: type_tag for name, type_tag in data}
    except Exception:
        return {}
    finally:
        conn.close()

def add_category(name, type_tag):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO categories (name, type) VALUES (?, ?)", (name, type_tag))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding category: {e}")
        return False
    finally:
        conn.close()

def delete_category(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM categories WHERE name = ?", (name,))
        # Optional: Also delete rules associated with this category?
        # c.execute("DELETE FROM rules WHERE category = ?", (name,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def seed_categories_if_empty(initial_categories):
    """Populates DB with hardcoded categories if table is empty."""
    current = get_categories()
    if not current:
        print("Seeding categories table...")
        for name, type_tag in initial_categories.items():
            add_category(name, type_tag)

# --- 2. RULE MANAGEMENT ---
def load_rules_from_db():
    """Returns a dictionary of rules {keyword: category}"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT keyword, category FROM rules")
    data = c.fetchall()
    conn.close()
    return {keyword: category for keyword, category in data}

def add_rule(keyword, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # INSERT OR REPLACE allows updating existing keywords
        c.execute("INSERT OR REPLACE INTO rules (keyword, category) VALUES (?, ?)", 
                  (keyword.upper(), category))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding rule: {e}")
        return False
    finally:
        conn.close()

def delete_rule(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM rules WHERE keyword = ?", (keyword,))
    conn.commit()
    conn.close()

def seed_rules_if_empty(initial_rules_dict):
    """
    Takes the rules from categories.py and puts them in DB 
    ONLY if the DB is empty.
    """
    current_rules = load_rules_from_db()
    if not current_rules:
        print("Seeding database with initial rules...")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for key, cat in initial_rules_dict.items():
            c.execute("INSERT OR IGNORE INTO rules (keyword, category) VALUES (?, ?)", 
                      (key.upper(), cat))
        conn.commit()
        conn.close()

# --- 3. TRANSACTION MANAGEMENT (Unchanged) ---
def generate_transaction_id(row):
    date_str = str(row['Date'])
    desc_str = str(row['Description'])
    amt_str = str(row['Amount'])
    raw_str = f"{date_str}{desc_str}{amt_str}"
    return hashlib.md5(raw_str.encode()).hexdigest()

def save_transactions(df):
    if df.empty: return 0
    save_df = df.copy()
    
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
            c.execute('''
                INSERT INTO transactions (id, date, description, amount, category, source, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (trans_id, row['Date'], row['Description'], row['Amount'], 
                  row['Category'], row.get('Source', 'Unknown'), row.get('Type', 'Unknown')))
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
        df = df.rename(columns={'date': 'Date', 'description': 'Description', 'amount': 'Amount', 'category': 'Category', 'source': 'Source', 'type': 'Type'})
        if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if 'Amount' in df.columns: df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    return df

def update_transaction_category(transaction_id, new_category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE transactions SET category = ? WHERE id = ?", (new_category, transaction_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# ... inside database.py

def update_transaction_amount(transaction_id, new_amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE transactions SET amount = ? WHERE id = ?", (new_amount, transaction_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating amount: {e}")
        return False
    finally:
        conn.close()

def clear_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    # Note: We do NOT delete the rules table here, or you lose your config!
    conn.commit()
    conn.close()

    # --- Add to the bottom of database.py ---


def get_db_path():
    """Returns the path to the current database file."""
    return DB_NAME

def restore_db(uploaded_file):
    """Overwrites the current database with the uploaded file."""
    try:
        with open(DB_NAME, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        print(f"Error restoring DB: {e}")
        return False