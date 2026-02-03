# categories.py

# Format: "KEYWORD": "CATEGORY"
# Keywords are case-insensitive.
CATEGORY_RULES = {
    # --- TRANSFERS (Ignored in charts) ---
    'AMERICAN EXPRESS': 'Transfer',      
    'BETALING MOTTATT': 'Transfer',      
    'OVERFØRING': 'Transfer',            
    'SPAREKONTO': 'Transfer',            
    'AKSJESPAREKONTO': 'Transfer',       
    'TIL BARE BITCOIN': 'Transfer', # Example from your bank CSV
    'TIL OLIVER': 'Transfer',       # Example from your bank CSV

    # --- SPENDING CATEGORIES ---
    # Groceries
    'REMA': 'Groceries',
    'KIWI': 'Groceries',
    'EXTRA': 'Groceries',
    'MENY': 'Groceries',
    'BUNNPRIS': 'Groceries',
    'MATKROKEN': 'Groceries',
    
    # Transport & Travel
    'CIRCLE K': 'Transport',
    'SHELL': 'Transport',
    'UNO-X': 'Transport',
    'PARKERING': 'Transport',
    'RYDE': 'Transport',
    'VOI': 'Transport',
    'BOM': 'Transport',
    'VY': 'Transport',
    'RUTER': 'Transport',
    'SKYSS': 'Transport',
    'NORWEGIAN': 'Travel',
    'SAS': 'Travel',
    'WIDEROE': 'Travel',
    'FLYTOGET': 'Travel',
    
    # Shopping
    'ZALANDO': 'Shopping',
    'H&M': 'Shopping',
    'VOLT': 'Shopping',
    'JERNIA': 'Shopping',
    'IKEA': 'Shopping',
    'LINK BRANDS': 'Shopping',
    'SPORT OUTLET': 'Shopping',
    'EAST WEST': 'Shopping',
    'NORMAL': 'Shopping',
    'XXL NOR': 'Shopping',
    'ELKJOEP': 'Electronics',
    'POWER': 'Electronics',
    'APPLE': 'Electronics',
    'ELEKTROIMPORTOEREN': 'Electronics',
    
    # Food & Drinks
    'BURGER': 'Dining Out',
    'MCDONALDS': 'Dining Out',
    'DOMINOS': 'Dining Out',
    'RESTAURANT': 'Dining Out',
    'STARBUCKS': 'Dining Out',
    '7-ELEVEN': 'Dining Out',
    'NARVESEN': 'Dining Out',
    'BAKER': 'Dining Out',
    
    # Housing & Utilities
    'STRØM': 'Utilities',
    'FJORDKRAFT': 'Utilities',
    'TELENOR': 'Utilities',
    
    'LEIE': 'Rent',
    'HUSLEIE': 'Rent',
    'LÅN': 'Mortgage',

    #INSURANCE
    'FRENDE': 'INSURANCE',
    'IF FORSIKRING': 'INSURANCE',
    'TRYG FORSIKRING': 'INSURANCE',
    'GJENSIDIGE FORSIKRING': 'INSURANCE',
    
    # Entertainment & Subsriptions
    'NETFLIX': 'Subscriptions',
    'SPOTIFY': 'Subscriptions',
    'HBO': 'Subscriptions',
    'MEDLEMSAVGIFT': 'Subscriptions',
    #'KINO': 'Entertainment',
    'VIPPS': 'Vipps (Unsorted)'
}