import requests
import json
from datetime import datetime
from database import add_fund,add_instalments, get_all_funds

def add_new_fund(fund_name):
    with open('funds_cache.json','r') as f:
        all_funds = json.load(f)

    for i in all_funds:
        if(fund_name==i['schemeName']):
            scheme_code = i['schemeCode']
            break
        
    add_fund(scheme_code,fund_name)

def add_new_instalments(scheme_code,input_date,amount):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    data = response.json()

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

        units = float(amount)/nav_at_purchase

        add_instalments(scheme_code,input_date,amount,units,nav_at_purchase)
        message = "Successfully added"
        return message
    else:
        message = "Date not found"
        return message