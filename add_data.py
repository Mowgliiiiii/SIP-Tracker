import requests
from datetime import datetime
from database import add_fund,add_instalments, create_tables

print("1. Add new fund")
print("2. Add instalment to existing fund")

choice = int(input())

if choice==1:
    fund_name = input("Fund name: ")
    scheme_code = input("Scheme_code: ")

    add_fund(scheme_code,fund_name)

else:
    scheme_code = (input('Enter Scheme_code: '))
    input_date = input('Enter date in dd-mm-yy format: ')
    amount = int(input('Enter the amount you have invested: '))
    
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    data = response.json()

    date = input_date[:-2] + "20" + input_date[-2:]

    check_date = datetime.strptime(date,"%d-%m-%Y")
    date_loop = 0
    while date!=data['data'][date_loop]['date']:
        if check_date > datetime.strptime(data['data'][date_loop]['date'],"%d-%m-%Y"):
            if date_loop == 0:
                print('NAV is not available yet')
            else:
                date_loop-=1
            break
        date_loop+=1
    
    if(date_loop!=0):
        nav_at_purchase = float(data['data'][date_loop]['nav'])
        print(nav_at_purchase)

        units = amount/nav_at_purchase
        print(units)

    #add_instalments(scheme_code,date,amount,units,nav_at_purchase)
