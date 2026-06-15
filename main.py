import requests
import sqlite3
from datetime import datetime

scheme_code = "140196"
url = f"https://api.mfapi.in/mf/{scheme_code}/latest"

response = requests.get(url)
data = response.json()

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

# for i in liquid:
#    cursor.execute("INSERT OR IGNORE INTO installments(scheme_code,date,amount,units,nav_at_purchase) values (?,?,?,?,?)",(scheme_code,datetime.strftime(i['date'],'%d-%m-%y'),i['amount'],i['units'],i['nav_at_purchase']))

cursor.execute("SELECT * FROM funds")
rows_funds = cursor.fetchall()

for row in rows_funds:
    print(row)

cursor.execute("SELECT * FROM installments")
rows_installments = cursor.fetchall()

for row in rows_installments:
    print(row)

print(data)
print(data['meta']['scheme_name'])
print(data['data'][0]['nav'])
print(data['data'][0]['date'])

liquid = []

for row in rows_installments:
    liquid.append({
        'date': datetime.strptime(row[2],'%d-%m-%y'),
        'scheme_code': row[1],            
        'amount': row[3],
        'nav_at_purchase': row[5],
        'units': row[4],
        'id':row[0]
    })

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



conn.commit()
conn.close()