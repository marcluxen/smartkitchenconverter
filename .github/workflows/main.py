from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from langselect import langselect
from conversionsgui import conversionsgui
import json
import os

def check_and_initialize_json():
    file_path = 'recipes.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        data = []
        with open(file_path, 'w') as file:
            json.dump(data, file)
        return data

class MainApp(App):
    def build(self):
        self.recipes_data = check_and_initialize_json()
        sm = ScreenManager()
        sm.add_widget(LanguageScreen(name='language'))
        sm.add_widget(ConversionScreen(name='conversion'))
        return sm

class LanguageScreen(Screen):
    def on_enter(self):
        self.add_widget(langselect(on_language_select=self.on_language_select, on_recipe_load=self.on_recipe_load))

    def on_language_select(self, main_lang, additional_langs):
        conversion_screen = self.manager.get_screen('conversion')
        conversion_screen.set_languages(main_lang, additional_langs)
        self.manager.current = 'conversion'

    def on_recipe_load(self, recipe_details):
        conversion_screen = self.manager.get_screen('conversion')
        conversion_screen.load_recipe(recipe_details)
        self.manager.current = 'conversion'

class ConversionScreen(Screen):
    def set_languages(self, main_lang, additional_langs):
        self.clear_widgets()
        self.conversion_gui = conversionsgui(main_lang=main_lang, additional_langs=additional_langs)
        self.add_widget(self.conversion_gui)

    def load_recipe(self, recipe_details):
        self.clear_widgets()
        language_prefs = recipe_details['language_preferences']
        self.conversion_gui = conversionsgui(
            main_lang=language_prefs['main_language'],
            additional_langs=language_prefs['additional_languages']
        )
        print("Conversion GUI methods:", dir(self.conversion_gui))  # Add this line
        self.conversion_gui.load_recipe(recipe_details)
        self.add_widget(self.conversion_gui)

if __name__ == '__main__':
    MainApp().run()
