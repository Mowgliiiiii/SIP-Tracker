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
    date = input('Enter date in dd-mm-yy format: ')
    amount = int(input('Enter the amount you have invested: '))
    units = float(input('Enter the units allocated to you: '))
    nav_at_purchase = float(input('Enter the nav at purchasing time: '))

    add_instalments(scheme_code,date,amount,units,nav_at_purchase)
