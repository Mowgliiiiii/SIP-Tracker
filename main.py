import requests
import sqlite3
from datetime import datetime

scheme_code = "140196"
url = f"https://api.mfapi.in/mf/{scheme_code}/latest"

response = requests.get(url)
data = response.json()

print(data)
print(data['meta']['scheme_name'])
print(data['data'][0]['nav'])
print(data['data'][0]['date'])

liquid = [{'date': datetime.strptime('03-03-26','%d-%m-%y'),
          'amount': 3000,
          'nav_at_purchase': 3544.5704,
          'units': 0.846},

          {'date': datetime.strptime('22-04-26','%d-%m-%y'),
           'amount': 3000,
           'nav_at_purchase': 3581.521,
           'units': 0.838},

           {'date': datetime.strptime('14-05-26','%d-%m-%y'),
           'amount': 5000,
           'nav_at_purchase': 3592.7732,
           'units': 1.392},

           {'date': datetime.strptime('31-05-26','%d-%m-%y'),
           'amount': 3500,
           'nav_at_purchase': 3602.9964,
           'units': 0.971}]

liquid = sorted(liquid,key=lambda x: x['date'])

current_nav = float(data['data'][0]['nav'])

total_profit = 0

for i in liquid:
    current_value = i['units']*current_nav
    profit = current_value - i['amount']
    total_profit+=profit
    
    print(f"Date: {i['date']}" )
    print(f"Invested amount: {i['amount']}")
    print(f"Current value: {current_value}")
    print(f"Return: {profit}\n")

print(f"Net profit over all instalments: {total_profit}")

max_withdrawable_amount = 0.0

for i in liquid:
    if(current_nav<i['nav_at_purchase']):
        break
    
    max_withdrawable_amount += i['units']*current_nav

print(f"Maximum withdrawable amount is: {max_withdrawable_amount}")

conn = sqlite3.connect('sip_tracker.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS funds(
    scheme_code TEXT PRIMARY KEY,
    fund_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS installments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code TEXT,
    date TEXT,
    amount REAL,
    units REAL,
    nav_at_purchase REAL
)
''')

cursor.execute("INSERT OR IGNORE INTO funds(scheme_code,fund_name) values (?,?)",(scheme_code,data['meta']['scheme_name']))

cursor.execute("SELECT * FROM funds")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.commit()
conn.close()