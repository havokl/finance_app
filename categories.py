# categories.py

# Format: "KEYWORD": "CATEGORY"
# Keywords are case-insensitive.
CATEGORY_RULES = {

    # --- Car ---
    'AUTOPASSFERGE': 'Car',
    'CIRCLE K': 'Car',
    'FLYT AS': 'Car',
    'PARKLINK': 'Car',
    'SHELL': 'Car',
    'STATOIL': 'Car',
    'TORGHATTEN': 'Car',
    'UNO-X': 'Car',

    # --- Dining/Drinks ---
    '7-ELEVEN': 'Dining/Drinks',
    '7ELEVEN': 'Dining/Drinks',
    'BAKER': 'Dining/Drinks',
    'BEVERLY HILLS FUN PUB STA': 'Dining/Drinks',
    'BGO POINT DOM': 'Dining/Drinks',
    'BRIAN BORU': 'Dining/Drinks',
    'BURGER': 'Dining/Drinks',
    'COCA COLA EUROPACIFIC NOR': 'Dining/Drinks',
    'DOMINOS': 'Dining/Drinks',
    'FELIX BERGEN': 'Dining/Drinks',
    'FINNEGAARDEN HOTELL': 'Dining/Drinks',
    'FJORD1 FERDAMAT': 'Dining/Drinks',
    'FOODORA NORWAY': 'Dining/Drinks',
    'GARNES PIZZA OG GRILL': 'Dining/Drinks',
    'HEKKAN': 'Dining/Drinks',
    'ISS AVD 460095 DNB SM 55': 'Dining/Drinks',
    'KVAERNER STORD ADMIN': 'Dining/Drinks',
    'LOS TACOS': 'Dining/Drinks',
    'MAGDA': 'Dining/Drinks',
    'MCDARKEN': 'Dining/Drinks',
    'MCDBRYGGESPOREN': 'Dining/Drinks',
    'MCDONALDS': 'Dining/Drinks',
    'MCDRADALEN': 'Dining/Drinks',
    'MCDSTORD': 'Dining/Drinks',
    'NARVESEN': 'Dining/Drinks',
    'NO STRESS': 'Dining/Drinks',
    'OLD IRISH PUB STAVANGER': 'Dining/Drinks',
    'RESTAURANT': 'Dining/Drinks',
    'ST1 LONE': 'Dining/Drinks',
    'STARBUCKS': 'Dining/Drinks',
    'STORHAUG PIZZA AS': 'Dining/Drinks',
    'TEMPO TEMPO': 'Dining/Drinks',
    'WAVE': 'Dining/Drinks',
    'ZETTLE_*KUNG KUNG THAI TA': 'Dining/Drinks',

    # --- Electronics ---
    'APPLE': 'Electronics',
    'ELEKTROIMPORTOEREN': 'Electronics',
    'ELKJOEP': 'Electronics',
    'POWER': 'Electronics',

    # --- Furniture & Appliances ---
    'CLAS OHL 835': 'Furniture & Appliances',
    'EUROPRIS': 'Furniture & Appliances',
    'IKEA': 'Furniture & Appliances',
    'JERNIA': 'Furniture & Appliances',
    'JULA NORGE': 'Furniture & Appliances',
    'MEGAFLIS': 'Furniture & Appliances',
    'VEST MARKISE': 'Furniture & Appliances',

    # --- Gifts ---
    'BLINDEFORBUNDET': 'Gifts',
    'SAREPTA BLOMSTE': 'Gifts',

    # --- Groceries ---
    'BUNNPRIS': 'Groceries',
    'COOP OBS': 'Groceries',
    'EXTRA': 'Groceries',
    'JOKER': 'Groceries',
    'KIWI': 'Groceries',
    'MATKROKEN': 'Groceries',
    'MENY': 'Groceries',
    'REMA': 'Groceries',
    'SPAR LONE': 'Groceries',

    # --- Income ---
    'AKER BP': 'Income',
    'FRA AKER SOLUTIONS AS': 'Income',
    'LØNN': 'Income',
    'REISEUTGIFTER': 'Income',
    'RENTER': 'Income',

    # --- Insurance ---
    'FRENDE': 'Insurance',
    'GJENSIDIGE FORSIKRING': 'Insurance',
    'IF FORSIKRING': 'Insurance',
    'NITO FORSIKRING': 'Insurance',
    'TRYG FORSIKRING': 'Insurance',

    # --- Mortgage ---
    'LÅN': 'Mortgage',

    # --- Recreation & Well Beeing ---
    'CUT N GO': 'Recreation & Well Beeing',
    'CUTTERS': 'Recreation & Well Beeing',
    'KINO': 'Recreation & Well Beeing',

    # --- Rent ---
    'HUSLEIE': 'Rent',
    'LEIE': 'Rent',
    'TIL OLIVER TRYGVE BINDINGSBØ': 'Rent',

    # --- Saving ---
    'BARE BITCOIN': 'Saving',

    # --- Shopping ---
    'AVARDA*OUTNORTH': 'Shopping',
    'BERGANS OF NORWAY': 'Shopping',
    'BILTEMA': 'Shopping',
    'BODYLAB.NO': 'Shopping',
    'CLAS OHL 2847': 'Shopping',
    'EAST WEST': 'Shopping',
    'GJENBRUKEN BERGEN': 'Shopping',
    'H&M': 'Shopping',
    'HOEYER': 'Shopping',
    'JANUSFABRIKKEN': 'Shopping',
    'LINK BRANDS': 'Shopping',
    'NORMAL': 'Shopping',
    'SPORT 1': 'Shopping',
    'SPORT OUTLET': 'Shopping',
    'THANSEN BERGEN AASANE': 'Shopping',
    'THANSEN.NO': 'Shopping',
    'VOLT': 'Shopping',
    'XXL NOR': 'Shopping',
    'ZALANDO': 'Shopping',

    # --- Subscriptions ---
    'BONNIER PUBLICATIO': 'Subscriptions',
    'DISNEY PLUS': 'Subscriptions',
    'EVOFITNESS': 'Subscriptions',
    'HBO': 'Subscriptions',
    'MEDLEMSAVGIFT': 'Subscriptions',
    'MICROSOFT 365': 'Subscriptions',
    'NETFLIX': 'Subscriptions',
    'SKY FITNESS': 'Subscriptions',
    'SPOTIFY': 'Subscriptions',

    # --- Transfer ---
    'AKSJESPAREKONTO': 'Transfer',
    'AMERICAN EXPRESS': 'Transfer',
    'BETALING MOTTATT': 'Transfer',
    'EGEN KONTO': 'Transfer',
    'FRA HÅVARD RÅHEIM ØKLAND': 'Transfer',
    'FRA HÅVARD ØKLAND': 'Transfer',
    'FRA MIE KREYBU': 'Transfer',
    'OVERFØRING': 'Transfer',
    'SPAREKONTO': 'Transfer',
    'TIL HÅVARD RÅHEIM ØKLAND': 'Transfer',
    'TIL HÅVARD ØKLAND': 'Transfer',
    'TIL MIE KREYBU': 'Transfer',
    'TIL TRUMF': 'Transfer',
    'TIL:': 'Transfer',

    # --- Transport ---
    'ESSO': 'Transport',
    'PARKERING': 'Transport',

    # --- Travel ---
    'BOM': 'Travel',
    'FLYTOGET': 'Travel',
    'KOLUMBUS': 'Travel',
    'NORWEGIAN': 'Travel',
    'RUTER': 'Travel',
    'RYDE': 'Travel',
    'SAS': 'Travel',
    'SKYSS': 'Travel',
    'VOI': 'Travel',
    'VY': 'Travel',
    'WIDEROE': 'Travel',

    # --- Utilities ---
    'FJORDKRAFT': 'Utilities',
    'LYSE TELE': 'Utilities',
    'STRØM': 'Utilities',
    'TELENOR': 'Utilities',

    # --- Vipps (Unsorted) ---
    'VIPPS': 'Vipps (Unsorted)',
}
# --- EXPENSE TYPES MAPPING ---
# This maps your Categories to "Fixed" (Must haves) or "Variable" (Nice to haves)
EXPENSE_TYPES = {
    # Fixed Expenses (Recurring / Necessary)
    'Rent': 'Fixed',
    'Mortgage': 'Fixed',
    'Utilities': 'Fixed',
    'Insurance': 'Fixed',      # Added
    'Subscriptions': 'Fixed',  # Renamed from Entertainment
    'Saving': 'Fixed',         # Treating saving as a fixed obligation
    
    # Variable Expenses (Lifestyle / One-off)
    'Groceries': 'Variable',
    'Travel': 'Variable',      # Added
    'Dining/Drinks': 'Variable', # Renamed from Dining Out
    'Shopping': 'Variable',
    'Electronics': 'Variable',
    'Furniture & Appliances': 'Variable', # Added
    'Vipps (Unsorted)': 'Variable',
    'Gifts': 'Variable',
    'Car': 'Variable',
    'Recreation & Well Beeing': 'Variable',

    # NEW: Add Misc here
    'Misc': 'Variable',
    


    # Ignored in Expense Analysis
    'Transfer': 'Ignore',
    'Income': 'Ignore'
}