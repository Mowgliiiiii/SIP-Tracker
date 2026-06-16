import requests
from datetime import datetime

from database import create_tables, get_all_funds, get_instalments

create_tables()

total_profit = 0.0
max_withdrawable_amount = 0.0

for row_funds in get_all_funds():
    fund = []

    for row_instalments in get_instalments(row_funds[0]):
        fund.append({
            'date': datetime.strptime(row_instalments[2],'%d-%m-%y'),
            'scheme_code': row_instalments[1],            
            'amount': row_instalments[3],
            'nav_at_purchase': row_instalments[5],
            'units': row_instalments[4],
            'id':row_instalments[0]
        })

    fund = sorted(fund,key=lambda x: x['date'])

    scheme_code = row_funds[0]
    url = f"https://api.mfapi.in/mf/{scheme_code}/latest"

    response = requests.get(url)
    data = response.json()

    current_nav = float(data['data'][0]['nav'])

    print(data)
    print(data['meta']['scheme_name'])
    print(data['data'][0]['nav'])
    print(data['data'][0]['date'])

    fund_profit = 0

    for i in fund:
        current_value = i['units']*current_nav
        profit = current_value - i['amount']
        fund_profit+=profit
        
        print(f"Date: {i['date']}" )
        print(f"Invested amount: {i['amount']}")
        print(f"Current value: {current_value}")
        print(f"Return: {profit}\n")

    print(f"Net profit over all instalments for the {row_funds[1]}: {fund_profit}")

    total_profit += fund_profit

    local_withdrawable_amount = 0.0

    for i in fund:
        if(current_nav<i['nav_at_purchase']):
            break
        
        local_withdrawable_amount += i['units']*current_nav

    max_withdrawable_amount += local_withdrawable_amount

    print(f"Maximum withdrawable amount for the {row_funds[1]} is: {local_withdrawable_amount}")

print(f"Total returns over all my funds: {total_profit}")
print(f"Maximum amount can be redeemed in profit: {max_withdrawable_amount}")