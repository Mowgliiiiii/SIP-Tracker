from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from database import get_all_funds, get_instalments
from add_data import add_new_instalments
from datetime import datetime

class MyApp(App):
    def load_main_screen(self):
        for row in get_all_funds():
            btn = Button(text=row[1], size_hint_y=None, height=50)
            btn.bind(on_press=lambda instance, sc=row[0]: self.open_fund_detail(sc))
            self.root.ids.fund_list.add_widget(btn)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())  # left spacer
        add_fund_btn = Button(text='Add Fund', size_hint=(0.3, 1))
        wrapper.add_widget(add_fund_btn)
        wrapper.add_widget(Widget())  # right spacer
        self.root.ids.fund_list.add_widget(wrapper)

    def open_fund_detail(self, scheme_code):
        print(scheme_code)
        self.root.current = 'fund_detail'

    def on_start(self):
        import requests
        response = requests.get("https://api.mfapi.in/mf")
        self.all_funds = response.json()
        self.load_main_screen()
        print(self.search_funds("parag parikh"))
    
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