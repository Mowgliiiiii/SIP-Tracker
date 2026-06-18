from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class MyApp(App):
    def on_button_click(self,instance):
        print('Button Clicked')
    
    def build(self):
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label(text="Hello World",size_hint=(1,0.3)))
        layout.add_widget(Button(text="Get Started",size_hint=(1,0.7),on_press=self.on_button_click))
        return layout
    
MyApp().run()