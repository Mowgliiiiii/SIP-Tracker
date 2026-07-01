from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup

from database import get_all_funds, get_instalments
from add_data import add_new_instalments
from datetime import datetime
import requests
import json
import os

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
        for i in reversed(fund):
            if(current_nav<i['nav_at_purchase']):
                break
            
            local_withdrawable_amount += i['units']*current_nav
            local_withdrawable_profit += i['units']*current_nav - i['amount']

        return{ 
            'instalments': fund,
            'fund investment': total_investment_fund,
            'fund return': fund_profit,
            'fund return percent': fund_profit_percent,
            'fund withdrawable amount': local_withdrawable_amount,
            'fund withdrawable profit': local_withdrawable_profit
        }

    def open_fund_detail(self, scheme_code):
        self.root.current = 'fund_detail'
        self.root.ids.instalment_list.clear_widgets()

        fund_data = self.load_fund_detail(scheme_code)
        instalments_detail = fund_data['instalments']

        dashboard_text = (
            f"Total investment: {fund_data['fund investment']:.2f}\n"
            f"Total return: {fund_data['fund return']:.2f} ({fund_data['fund return percent']:.2f}%)\n"
            f"Withdrawable amount: {fund_data['fund withdrawable amount']:.2f}\n"
            f"Withdrawable profit: {fund_data['fund withdrawable profit']:.2f}"
        )

        dashboard = Label(text=dashboard_text, size_hint_y=None, height=120)
        self.root.ids.instalment_list.add_widget(dashboard)

        for row in instalments_detail:
            text_instalment = (
                f"Date: {datetime.strftime(row['date'],'%d-%m-%y')}\n"
                f"Amount invested: {row['amount']:.2f}\n"
                f"Current value: {row['current value']}\n"
                f"Return: {row['instalment return']}({row['instalment return percent']}%)"
            )

            instalment = Label(text=text_instalment, size_hint_y=None, height=80)
            self.root.ids.instalment_list.add_widget(instalment)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())  # left spacer
        add_instalment_btn = Button(text='Add instalment', size_hint=(0.3, 1))
        add_instalment_btn.bind(on_release=lambda instance: self.add_instalment_popup(scheme_code))
        wrapper.add_widget(add_instalment_btn)
        wrapper.add_widget(Widget())  # right spacer
        self.root.ids.instalment_list.add_widget(wrapper)

    def on_start(self):
        if os.path.exists('funds_cache.json'):
            with open('funds_cache.json','r') as f:
                self.all_funds = json.load(f)

        else:
            response = requests.get("https://api.mfapi.in/mf")
            self.all_funds = response.json()
            with open('funds_cache.json','w') as f:
                json.dump(self.all_funds,f)

        self.load_main_screen()
        
    def search_funds(self, query):
        query = query.lower()
        results = [f for f in self.all_funds if query in f['schemeName'].lower()]
        return results[:10]
    
    def add_instalment_popup(self,scheme_code):
        popup = Popup(title='Add Instalment', content=self.add_instalment_element(scheme_code),size_hint=(0.8,0.5))
        popup.open()

    def add_instalment_element(self,scheme_code):
        add_instalment_screen = BoxLayout(orientation='vertical')
        self.top_label = Label(text='Enter the details',size_hint=(1,0.3))
        add_instalment_screen.add_widget(self.top_label)
        
        row1 = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
        row1.add_widget(Label(text='Date: ',size_hint=(0.3,1)))
        self.popup_date = TextInput(hint_text='in dd/mm/yy format',size_hint=(0.7,1))
        row1.add_widget(self.popup_date)
        add_instalment_screen.add_widget(row1)

        row2 = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
        row2.add_widget(Label(text='Amount invested: ',size_hint=(0.3,1)))
        self.popup_amount = TextInput(size_hint=(0.7,1))
        row2.add_widget(self.popup_amount)
        add_instalment_screen.add_widget(row2)

        add_instalment_screen.add_widget(Button(text='Submit',size_hint=(0.25,0.2),pos_hint={'center_x': 0.5},on_release=lambda instance: self.instalment_submit(scheme_code)))

        return add_instalment_screen
        
    def instalment_submit(self,scheme_code):
        check_str = ""
        
        try:
            date_input = datetime.strptime(self.popup_date.text, "%d-%m-%y")
        except:
            check_str += "Please enter the date in the format: dd-mm-yy\n"

        try:
            amount = float(self.popup_amount.text)
        except:
            check_str += "Please enter the valid amount"
        
        if check_str == "":
            message = add_new_instalments(scheme_code,self.popup_date.text,self.popup_amount.text)
            
            self.top_label.text = message
            self.popup_date.text = ""
            self.popup_amount.text = ""

            self.open_fund_detail(scheme_code)
        else:
            self.top_label.text = check_str
        
    def build(self):
        pass
    
MyApp().run()