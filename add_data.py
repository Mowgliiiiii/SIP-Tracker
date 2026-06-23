import requests
from datetime import datetime
from database import add_fund,add_instalments, get_all_funds

def add_new_fund(scheme_code,fund_name):
    add_fund(scheme_code,fund_name)

def add_new_instalments(scheme_code,input_date,amount):
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        data = response.json()
    except:
        message = "Wrong scheme code"
        return message

    fund_present = False
    for rows in get_all_funds():
        if scheme_code == rows[0]:
            fund_present = True
        
    if not fund_present:
        add_new_fund(scheme_code,data['meta']['scheme_name'])

    date = input_date[:-2] + "20" + input_date[-2:]

    check_date = datetime.strptime(date,"%d-%m-%Y")
    date_loop = 0
    nav_availble = True
    
    while date!=data['data'][date_loop]['date']:
        if check_date > datetime.strptime(data['data'][date_loop]['date'],"%d-%m-%Y"):
            if date_loop == 0:
                nav_availble = False
            else:
                date_loop-=1
            break
        date_loop+=1

    if nav_availble:
        nav_at_purchase = float(data['data'][date_loop]['nav'])

        units = amount/nav_at_purchase

        add_instalments(scheme_code,input_date,amount,units,nav_at_purchase)
        message = "Successfully added"
        return message
    else:
        message = "Date not found"
        return message