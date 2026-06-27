from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from database import get_all_funds, get_instalments
from add_data import add_new_instalments
from datetime import datetime
import requests

class MyApp(App):
    def load_main_screen(self):
        for row in get_all_funds():
            btn = Button(text=row[1], size_hint_y=None, height=50)
            btn.bind(on_release=lambda instance, sc=row[0]: self.open_fund_detail(sc))
            self.root.ids.fund_list.add_widget(btn)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())  # left spacer
        add_fund_btn = Button(text='Add Fund', size_hint=(0.3, 1))
        wrapper.add_widget(add_fund_btn)
        wrapper.add_widget(Widget())  # right spacer
        self.root.ids.fund_list.add_widget(wrapper)


    def load_fund_detail(self,scheme_code):
        fund = []

        for row_instalments in get_instalments(scheme_code):
            fund.append({
                'date': datetime.strptime(row_instalments[2],'%d-%m-%y'),          
                'amount': row_instalments[3],
                'nav_at_purchase': row_instalments[5],
                'units': row_instalments[4]
            })

        fund = sorted(fund,key=lambda x: x['date'],reverse=True)

        url = f"https://api.mfapi.in/mf/{scheme_code}/latest"

        response = requests.get(url)
        data = response.json()

        current_nav = float(data['data'][0]['nav'])

        fund_profit = 0.0
        total_investment_fund = 0.0

        for i in fund:
            current_value = i['units']*current_nav
            profit = current_value - i['amount']
            fund_profit+=profit
            return_percent = (profit/i['amount'])*100
            total_investment_fund += i['amount']

            i['current value'] = f"{current_value:.2f}"
            i['instalment return'] = f"{profit:.2f}"
            i['instalment return percent'] = f"{return_percent:.2f}"

        fund_profit_percent = (fund_profit/total_investment_fund)*100
        
        local_withdrawable_amount = 0.0

        local_withdrawable_profit = 0.0
        for i in fund:
            if(current_nav<i['nav_at_purchase']):
                break
            
            local_withdrawable_amount += i['units']*current_nav
            local_withdrawable_profit += i['units']*current_nav - i['amount']

        return fund

    def open_fund_detail(self, scheme_code):
        self.root.current = 'fund_detail'
        self.root.ids.instalment_list.clear_widgets()

        instalments_detail = self.load_fund_detail(scheme_code)

        for row in instalments_detail:
            text_instalment = (
                f"Date: {row['date']}\n"
                f"Amount invested: {row['amount']:.2f}\n"
                f"Current value: {row['current value']}\n"
                f"Return: {row['instalment return']}({row['instalment return percent']}%)"
            )

            instalment = Label(text=text_instalment, size_hint_y=None, height=80)
            self.root.ids.instalment_list.add_widget(instalment)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())  # left spacer
        add_instalment_btn = Button(text='Add instalment', size_hint=(0.3, 1))
        wrapper.add_widget(add_instalment_btn)
        wrapper.add_widget(Widget())  # right spacer
        self.root.ids.instalment_list.add_widget(wrapper)

    def on_start(self):
        import requests
        response = requests.get("https://api.mfapi.in/mf")
        self.all_funds = response.json()
        self.load_main_screen()
    
    def search_funds(self, query):
        query = query.lower()
        results = [f for f in self.all_funds if query in f['schemeName'].lower()]
        return results[:10]
        
    def on_button_click(self):
        check_str = ""

        try:
            scheme_code = int(self.root.ids.scheme_input.text)
        except:
            check_str += "Please enter the valid scheme code\n"
        
        try:
            date_input = datetime.strptime(self.root.ids.date_input.text, "%d-%m-%y")
        except:
            check_str += "Please enter the date in the format: dd-mm-yy\n"

        try:
            amount = float(self.root.ids.amount_input.text)
        except:
            check_str += "Please enter the valid amount"
        
        if check_str == "":
            message = add_new_instalments(scheme_code,self.root.ids.date_input.text,amount)
            
            self.root.ids.top_label.text = message
            self.root.ids.scheme_input.text = ""
            self.root.ids.date_input.text = ""
            self.root.ids.amount_input.text = ""
        else:
            self.root.ids.top_label.text = check_str
        
    def build(self):
        pass
    
MyApp().run()