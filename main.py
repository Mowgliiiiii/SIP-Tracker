import requests
import sqlite3
from datetime import datetime

from database import create_tables, get_all_funds, get_installments

create_tables()

print(get_all_funds())
print(get_installments(140196))

scheme_code = "140196"
url = f"https://api.mfapi.in/mf/{scheme_code}/latest"

response = requests.get(url)
data = response.json()

print(data)
print(data['meta']['scheme_name'])
print(data['data'][0]['nav'])
print(data['data'][0]['date'])

conn = sqlite3.connect('sip_tracker.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM installments")
rows_installments = cursor.fetchall()

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