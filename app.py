from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

from database import get_all_funds, get_instalments, delete_fund, delete_instalment
from add_data import add_new_instalments, add_new_fund
from datetime import datetime
import requests
import json
import os

class MyApp(App):
    def styled_button(self, text, **kwargs):
        btn = Button(text=text, **kwargs)
        btn.halign = 'center'
        btn.valign = 'middle'
        btn.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        btn.bind(texture_size=lambda instance, value: setattr(instance, 'height', max(value[1] + 20, 30)))
        return btn

    def add_border(self, widget, color=(0, 0, 0, 1), width=2):
        with widget.canvas.after:
            Color(*color)
            widget.border_line = Line(
                rectangle=(widget.x, widget.y, widget.width, widget.height),
                width=width
            )

        def update(instance, value):
            instance.border_line.rectangle = (
                instance.x,
                instance.y,
                instance.width,
                instance.height
            )

        widget.bind(pos=update, size=update)

    def add_card_background(self, widget, color=(0.17, 0.16, 0.19, 1)):
        with widget.canvas.before:
            Color(*color)
            widget.card_rect = Rectangle(pos=widget.pos, size=widget.size)

        widget.bind(pos=self.update_card_rect, size=self.update_card_rect)
        return widget

    def update_card_rect(self, instance, value):
        instance.card_rect.pos = instance.pos
        instance.card_rect.size = instance.size

    def on_start(self):
        Window.clearcolor = (0.03,0.03,0.03,1)

        if os.path.exists('funds_cache.json'):
            with open('funds_cache.json','r') as f:
                self.all_funds = json.load(f)

        else:
            response = requests.get("https://api.mfapi.in/mf")
            self.all_funds = response.json()
            with open('funds_cache.json','w') as f:
                json.dump(self.all_funds,f)

        self.load_main_screen()
    
    def load_main_screen(self):
        self.root.ids.fund_list.clear_widgets()
        self.main_dashboard = Label(text='Dashboard', size_hint_y=None, height=150)
        
        self.add_card_background(self.main_dashboard,(0.17, 0.16, 0.19, 1))
        self.root.ids.fund_list.add_widget(self.main_dashboard)
        
        self.load_main_dashboard()

        for row in get_all_funds():
            btn = self.styled_button(row[1], size_hint_y=None)
            btn.bind(on_release=lambda instance, sc=row[0]: self.open_fund_detail(sc))
            self.add_border(btn,(0.992, 0.702, 0.761, 1),2) #light pink
            btn.background_normal = ""
            btn.background_color = (0.686, 0.863, 0.922, 1) #light blue
            btn.color = (0,0,0,1)
            self.root.ids.fund_list.add_widget(btn)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())  # left spacer
        
        add_fund_btn = self.styled_button('Add Fund', size_hint_x=0.4)
        add_fund_btn.bind(on_release=lambda instance: self.add_fund_popup())
        wrapper.add_widget(add_fund_btn)

        wrapper.add_widget(Widget(size_hint=(0.1,1))) 
        
        delete_fund_btn = self.styled_button('Remove fund',size_hint_x=0.4)
        delete_fund_btn.bind(on_release=lambda instance: self.delete_fund_popup())
        wrapper.add_widget(delete_fund_btn)
        
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
        fund_current_value = 0.0

        for i in fund:
            current_value = i['units']*current_nav
            fund_current_value += current_value
            profit = current_value - i['amount']
            fund_profit+=profit
            return_percent = (profit/i['amount'])*100
            total_investment_fund += i['amount']

            i['current value'] = f"{current_value:.2f}"
            i['instalment return'] = f"{profit:.2f}"
            i['instalment return percent'] = f"{return_percent:.2f}"

        if(total_investment_fund!=0):
            fund_profit_percent = (fund_profit/total_investment_fund)*100
        else:
            fund_profit_percent = 0
        
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
            'fund current value': fund_current_value,
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
            f"Current value: {fund_data['fund current value']:.2f}\n"
            f"Total return: {fund_data['fund return']:.2f} ({fund_data['fund return percent']:.2f}%)\n"
            f"Withdrawable amount: {fund_data['fund withdrawable amount']:.2f}\n"
            f"Withdrawable profit: {fund_data['fund withdrawable profit']:.2f}"
        )

        dashboard = Label(text=dashboard_text, size_hint_y=None, height=120)
        self.add_card_background(dashboard,(0.17,0.16,0.19,1))
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
        
        add_instalment_btn = self.styled_button(text='Add instalment', size_hint_x=0.4)
        add_instalment_btn.bind(on_release=lambda instance: self.add_instalment_popup(scheme_code))
        wrapper.add_widget(add_instalment_btn)
        
        wrapper.add_widget(Widget(size_hint=(0.1,1)))

        delete_instalment_btn = self.styled_button(text='Delete',size_hint_x=0.4)
        delete_instalment_btn.bind(on_release=lambda instance: self.delete_instalment_popup(scheme_code))
        wrapper.add_widget(delete_instalment_btn)

        wrapper.add_widget(Widget())  # right spacer
        self.root.ids.instalment_list.add_widget(wrapper)

    def add_instalment_popup(self,scheme_code):
        popup = Popup(title='Add Instalment', content=self.add_instalment_element(scheme_code),size_hint=(0.8,0.5))
        popup.open()

    def add_instalment_element(self,scheme_code):
        add_instalment_screen = BoxLayout(orientation='vertical')
        self.top_label = Label(text='Enter the details',size_hint=(1,0.3))
        add_instalment_screen.add_widget(self.top_label)
        
        row1 = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
        row1.add_widget(Label(text='Date: ',size_hint=(0.35,1)))
        self.popup_date = TextInput(hint_text='in dd/mm/yy format',size_hint=(0.65,1))
        row1.add_widget(self.popup_date)
        add_instalment_screen.add_widget(row1)

        row2 = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
        row2.add_widget(Label(text='Amount: ',size_hint=(0.35,1)))
        self.popup_amount = TextInput(size_hint=(0.65,1))
        row2.add_widget(self.popup_amount)
        add_instalment_screen.add_widget(row2)

        add_instalment_screen.add_widget(Button(text='Submit',size_hint=(0.25,0.2),pos_hint={'center_x': 0.5},on_release=lambda instance: self.instalment_submit(scheme_code)))

        return add_instalment_screen
        
    def instalment_submit(self,scheme_code):
        check_str = ""
        
        try:
            date_input = datetime.strptime(self.popup_date.text, "%d-%m-%y")
        except:
            check_str += "Enter date in format: dd-mm-yy\n"

        try:
            amount = float(self.popup_amount.text)
        except:
            check_str += "Enter valid amount"
        
        if check_str == "":
            message = add_new_instalments(scheme_code,self.popup_date.text,self.popup_amount.text)
            
            self.top_label.text = message
            self.popup_date.text = ""
            self.popup_amount.text = ""

            self.open_fund_detail(scheme_code)
            self.load_main_screen()
        else:
            self.top_label.text = check_str

    def delete_instalment_element(self,scheme_code):
        self.selected_delete_instalment = None
        self.selected_instalment_button = None

        delete_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        delete_layout.bind(minimum_height=delete_layout.setter("height"))

        for row in get_instalments(scheme_code):
            btn = self.styled_button(
                text=f"Date: {row[2]}\nAmount: {row[3]}",
                size_hint_y=None,
                color=(0,0,0,1)
            )

            btn.bind(
                on_release=lambda instance, id=row[0]: self.select_delete_instalment(instance,id)
            )

            delete_layout.add_widget(btn)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())
        self.delete_instalment_btn = self.styled_button(text="Delete", size_hint_x=0.4, disabled=True)
        self.delete_instalment_btn.bind(on_release=lambda instance: self.post_delete_instalment(self.selected_delete_instalment,scheme_code))
        wrapper.add_widget(self.delete_instalment_btn)
        wrapper.add_widget(Widget())

        delete_layout.add_widget(wrapper)

        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(delete_layout)
        return scroll

    def select_delete_instalment(self, button, id):
        self.delete_instalment_btn.disabled = False
        self.selected_delete_instalment = id

        if self.selected_instalment_button:
            self.selected_instalment_button.background_color = (1, 1, 1, 1)

        button.background_color = (0.2, 0.6, 1, 1)
        self.selected_instalment_button = button

    def delete_instalment_popup(self,scheme_code):
        self.popup_delete_instalment = Popup(title='Delete Instalment', content=self.delete_instalment_element(scheme_code),size_hint=(0.84,0.6))
        self.popup_delete_instalment.open()

    def post_delete_instalment(self,id,scheme_code):
        delete_instalment(id)
        self.popup_delete_instalment.dismiss()
        self.open_fund_detail(scheme_code)
        self.load_main_screen()
        
    def load_main_dashboard(self):
        overall_return = 0.0
        overall_instalment = 0.0
        overall_current_value = 0.0
        overall_withdrawable_amount = 0.0
        overall_withdrawable_profit = 0.0
        
        for row in get_all_funds():
            scheme_code = row[0]
            fund_detail = self.load_fund_detail(scheme_code)

            overall_instalment+=fund_detail['fund investment']
            overall_current_value+=fund_detail['fund current value']
            overall_return+=fund_detail['fund return']
            overall_withdrawable_amount+=fund_detail['fund withdrawable amount']
            overall_withdrawable_profit+=fund_detail['fund withdrawable profit']

        overall_return_percent=(overall_return/overall_instalment)*100 if overall_instalment!=0 else 0

        main_dashboard_content = (
            f"Total investment: {overall_instalment:.2f}\n"
            f"Current value: {overall_current_value:.2f}\n"
            f"Return: {overall_return:.2f} ({overall_return_percent:.2f}%)\n"
            f"Withdrawable amount: {overall_withdrawable_amount:.2f}\n"
            f"Withdrawable profit: {overall_withdrawable_profit:.2f}"
        )

        self.main_dashboard.text = main_dashboard_content

    def add_fund_popup(self):
        self.popup_add_fund = Popup(title='Add Fund', content=self.add_fund_element(),size_hint=(0.84,0.6))
        self.popup_add_fund.open()

    def add_fund_element(self):
        add_fund_screen = BoxLayout(orientation='vertical')
        
        self.search_input = TextInput(hint_text='Search Fund Name', size_hint=(1, None), height = 40)
        self.search_layout = GridLayout(spacing=10, cols=1, size_hint_x=1, size_hint_y=None, height=290)
        self.search_layout.bind(minimum_height=self.search_layout.setter('height'))
        
        self.search_input.bind(text=lambda instance, query: self.filter_funds(query))
        
        add_fund_screen.add_widget(self.search_input)
        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(self.search_layout)
        add_fund_screen.add_widget(scroll)

        self.popup_add_fund_btn = Button(text="Add", size_hint=(0.25,None), pos_hint={'center_x':0.5},disabled=True)
        self.popup_add_fund_btn.bind(on_release=lambda instance: self.new_fund_submit(self.search_input.text))
        add_fund_screen.add_widget(self.popup_add_fund_btn)

        return add_fund_screen
    
    def new_fund_submit(self,fund_name):
        add_new_fund(fund_name)
        self.popup_add_fund.dismiss()
        self.load_main_screen()

    def filter_funds(self,query):
        self.popup_add_fund_btn.disabled = True
        self.search_layout.clear_widgets()
        top_search = self.search_funds(query)
        for i in top_search:
            self.search_layout.add_widget(
                self.styled_button(
                    text=i['schemeName'],
                    size_hint_y=None,
                    on_release=lambda instance, name=i['schemeName']: [setattr(self.search_input, "text", name), setattr(self.popup_add_fund_btn, 'disabled', False)]
                )
            )

    def search_funds(self, query):
        query = query.lower()
        results = [f for f in self.all_funds if query in f['schemeName'].lower()]
        results.sort(key=lambda f: (not f['schemeName'].lower().startswith(query), f['schemeName'].lower()))
        return results[:10]
    
    def delete_fund_element(self):
        self.selected_delete_fund = None
        self.selected_button = None

        delete_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        delete_layout.bind(minimum_height=delete_layout.setter("height"))

        for row in get_all_funds():
            btn = self.styled_button(
                text=row[1],
                size_hint_y=None,
                color=(0,0,0,1)
            )

            btn.bind(
                on_release=lambda instance, sc=row[0]: self.select_delete_fund(instance,sc)
            )

            delete_layout.add_widget(btn)

        wrapper = BoxLayout(size_hint_y=None, height=60)
        wrapper.add_widget(Widget())
        self.delete_btn = self.styled_button(text="Delete Fund", size_hint_x=0.4,disabled=True)
        self.delete_btn.bind(on_release=lambda instance: self.post_delete_fund(self.selected_delete_fund))
        wrapper.add_widget(self.delete_btn)
        wrapper.add_widget(Widget())

        delete_layout.add_widget(wrapper)

        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(delete_layout)

        return scroll

    def select_delete_fund(self, button, scheme_code):
        self.delete_btn.disabled = False
        self.selected_delete_fund = scheme_code

        if self.selected_button:
            self.selected_button.background_color = (1, 1, 1, 1)

        button.background_color = (0.2, 0.6, 1, 1)
        self.selected_button = button

    def delete_fund_popup(self):
        self.popup_delete_fund = Popup(title='Delete Fund', content=self.delete_fund_element(),size_hint=(0.84,0.6))
        self.popup_delete_fund.open()

    def post_delete_fund(self,scheme_code):
        delete_fund(scheme_code)
        self.popup_delete_fund.dismiss()
        self.load_main_screen()
        
    def build(self):
        pass
    
MyApp().run()