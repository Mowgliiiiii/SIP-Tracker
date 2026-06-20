from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from datetime import datetime

class MyApp(App):
    def on_button_click(self,instance):
        check_str = ""

        try:
            scheme_code = int(self.scheme_input.text)
        except:
            check_str += "Please enter the valid scheme code\n"
        
        try:
            date_input = datetime.strptime(self.date_input.text,"%d-%m-%y")
        except:
            check_str  += "Please enter the date in the format: dd-mm-yy\n"

        try:
            amount = float(self.amount_input.text)
        except:
            check_str += "Please enter the valid amount"
        
        if check_str == "":
            self.label.text = "Investment added successfully"
            self.scheme_input.text = ""
            self.date_input.text = ""
            self.amount_input.text = ""
        else:
            self.label.text = check_str

    
    def build(self):
        outer_layout = BoxLayout(orientation = 'vertical')
        
        inner_layout1 = BoxLayout(orientation = 'horizontal',size_hint=(1,0.2))
        inner_layout2 = BoxLayout(orientation = 'horizontal',size_hint=(1,0.2))
        inner_layout3 = BoxLayout(orientation = 'horizontal',size_hint=(1,0.2))

        self.label = Label(text="Get Started",size_hint=(1,0.2))
        outer_layout.add_widget(self.label)

        outer_layout.add_widget(inner_layout1)
        self.scheme_input = TextInput(size_hint=(0.7,1))
        inner_layout1.add_widget(Label(text="Enter Scheme Code:",size_hint=(0.3,1)))
        inner_layout1.add_widget(self.scheme_input)

        outer_layout.add_widget(inner_layout2)
        self.date_input = TextInput(size_hint=(0.7,1),hint_text=("Format: dd-mm-yy"))
        inner_layout2.add_widget(Label(text="Enter Date: ",size_hint=(0.3,1)))
        inner_layout2.add_widget(self.date_input)

        outer_layout.add_widget(inner_layout3)
        self.amount_input = TextInput(size_hint=(0.7,1))
        inner_layout3.add_widget(Label(text="Enter the amount you have invested:",size_hint=(0.3,1)))
        inner_layout3.add_widget(self.amount_input)

        outer_layout.add_widget(Button(text="Click to submit",size_hint=(1,0.2),on_press=self.on_button_click,background_color=(0.2,0.6,0.9,1)))
        #return outer_layout
    
MyApp().run()