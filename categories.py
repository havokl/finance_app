# categories.py

# Format: "KEYWORD": "CATEGORY"
# Keywords are case-insensitive.
CATEGORY_RULES = {
    # --- INCOME (Money In) ---
    'AKER BP': 'Income',          # Salary & Travel Reimbursements
    'LØNN': 'Income',             # Generic Salary
    'RENTER': 'Income',           # Interest
    'REISEUTGIFTER': 'Income',    # Travel refunds
    
    # --- TRANSFERS (Internal movements - Ignored in Spend Charts) ---
    'AMERICAN EXPRESS': 'Transfer',      # Payment from Bank -> Amex
    'BETALING MOTTATT': 'Transfer',      # Payment received by Amex
    'OVERFØRING': 'Transfer',            # Generic bank transfers
    'SPAREKONTO': 'Transfer',            # Savings
    'AKSJESPAREKONTO': 'Transfer',       # Investments
    'EGEN KONTO': 'Transfer',
    'TIL:': 'Transfer',                  # Often used for transfers (check this!)
    'TIL HÅVARD RÅHEIM ØKLAND': 'Transfer',
    'FRA HÅVARD RÅHEIM ØKLAND': 'Transfer',
    'TIL HÅVARD ØKLAND': 'Transfer',
    'FRA HÅVARD ØKLAND': 'Transfer',
    'TIL MIE KREYBU': 'Transfer',
    'FRA MIE KREYBU': 'Transfer',
    'TIL TRUMF': 'Transfer',


    # --- EXPENSES (Money Out) ---
    # Groceries
    'REMA': 'Groceries',
    'KIWI': 'Groceries',
    'EXTRA': 'Groceries',
    'MENY': 'Groceries',
    'BUNNPRIS': 'Groceries',
    'MATKROKEN': 'Groceries',
    'COOP OBS': 'Groceries',
    'JOKER': 'Groceries',

    
    # Transport & Travel
    'CIRCLE K': 'Transport',
    'SHELL': 'Transport',
    'UNO-X': 'Transport',
    'ESSO': 'Transport',
    'PARKERING': 'Transport',
    'RYDE': 'Transport',
    'VOI': 'Transport',
    'KOLUMBUS': 'Transport',
    'BOM': 'Transport',
    'VY': 'Transport',
    'RUTER': 'Transport',
    'SKYSS': 'Transport',
    'FLYT AS': 'Transport',
    'AUTOPASSFERGE': 'Transport',
    'TORGHATTEN': 'Transport',

    'NORWEGIAN': 'Travel',
    'SAS': 'Travel',
    'WIDEROE': 'Travel',
    'FLYTOGET': 'Travel',
    
    # Shopping
    'ZALANDO': 'Shopping',
    'H&M': 'Shopping',
    'VOLT': 'Shopping',
    'LINK BRANDS': 'Shopping',
    'SPORT OUTLET': 'Shopping',
    'EAST WEST': 'Shopping',
    'NORMAL': 'Shopping',
    'BODYLAB.NO': 'Shopping',
    'XXL NOR': 'Shopping',
    'AVARDA*OUTNORTH': 'Shopping',
    'ELKJOEP': 'Electronics',
    'POWER': 'Electronics',
    'APPLE': 'Electronics',
    'ELEKTROIMPORTOEREN': 'Electronics',
    'VEST MARKISE': 'Furniture & Appliances',
    'JERNIA': 'Furniture & Appliances',
    'IKEA': 'Furniture & Appliances',
    'EUROPRIS': 'Furniture & Appliances',
    'JULA NORGE': 'Furniture & Appliances',

    
    # Food & Drinks
    'BURGER': 'Dining/Drinks',
    'MCDONALDS': 'Dining/Drinks',
    'DOMINOS': 'Dining/Drinks',
    'RESTAURANT': 'Dining/Drinks',
    'STARBUCKS': 'Dining/Drinks',
    '7-ELEVEN': 'Dining/Drinks',
    '7ELEVEN': 'Dining/Drinks',
    'NARVESEN': 'Dining/Drinks',
    'GARNES PIZZA OG GRILL': 'Dining/Drinks',
    'FELIX BERGEN': 'Dining/Drinks',
    'BAKER': 'Dining/Drinks',
    'FINNEGAARDEN HOTELL': 'Dining/Drinks',
    'MAGDA': 'Dining/Drinks',
    'BRIAN BORU': 'Dining/Drinks',
    
    
    # Housing & Utilities
    'STRØM': 'Utilities',
    'FJORDKRAFT': 'Utilities',
    'TELENOR': 'Utilities',
    'LYSE TELE': 'Utilities',
    
    'LEIE': 'Rent',
    'HUSLEIE': 'Rent',
    'TIL OLIVER TRYGVE BINDINGSBØ': 'Rent', 
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
    'SKY FITNESS': 'Subscriptions',
    'MICROSOFT 365': 'Subscriptions',
    #'KINO': 'Entertainment',
    'VIPPS': 'Vipps (Unsorted)',
    #Saving
    'BARE BITCOIN': 'Saving'

}