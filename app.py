from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from add_data import add_new_instalments

from datetime import datetime

class MyApp(App):
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