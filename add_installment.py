import sqlite3

scheme_code = (input('Enter Scheme_code: '))
date = input('Enter data in dd-mm-yy format: ')
amount = int(input('Enter the amount you have invested: '))
units = float(input('Enter the units allocated to you: '))
nav_at_purchase = float(input('Enter the nav at purchasing time: '))

conn = sqlite3.connect('sip_tracker.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO installments(scheme_code,date,amount,units,nav_at_purchase) values (?,?,?,?,?)",(scheme_code,date,amount,units,nav_at_purchase))
conn.commit()
conn.close()