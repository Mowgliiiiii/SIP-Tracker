import sqlite3

def create_tables():
    conn = sqlite3.connect('sip_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS funds(
        scheme_code TEXT PRIMARY KEY,
        fund_name TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instalments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code TEXT,
        date TEXT,
        amount REAL,
        units REAL,
        nav_at_purchase REAL
    )
    ''')
    
    conn.commit()
    conn.close()


def get_all_funds():
    conn = sqlite3.connect('sip_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT scheme_code, fund_name FROM funds")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_instalments(scheme_code):
    conn = sqlite3.connect('sip_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instalments WHERE scheme_code = ?", (scheme_code,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_fund(scheme_code,fund_name):
    conn = sqlite3.connect('sip_tracker.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO funds(scheme_code,fund_name) values (?,?)",(scheme_code,fund_name))
    conn.commit()
    conn.close()

def add_instalments(scheme_code,date,amount,units,nav_at_purchase):
    conn = sqlite3.connect('sip_tracker.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO instalments(scheme_code,date,amount,units,nav_at_purchase) values (?,?,?,?,?)",(scheme_code,date,amount,units,nav_at_purchase))
    conn.commit()
    conn.close()
