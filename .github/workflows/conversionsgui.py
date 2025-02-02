from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.app import App
import conversionslogic

class NumericInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if not substring:
            return
        if substring.isnumeric():
            super().insert_text(substring, from_undo=from_undo)
        elif substring == '.' and self.text and self.text[-1].isnumeric():
            super().insert_text(substring, from_undo=from_undo)
        elif '.' in self.text and substring.isnumeric():
            super().insert_text(substring, from_undo=from_undo)
           


class conversionsgui(BoxLayout):
    def __init__(self, main_lang, additional_langs, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=10, size_hint=(0.9, 0.9), **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.main_lang, self.additional_langs = main_lang, additional_langs
        self.measurements = conversionslogic.get_measurements()
        self.foodnames = conversionslogic.get_foodnames(self.main_lang, self.additional_langs)
        self.main_font = conversionslogic.language_fonts[self.main_lang]
        self.button_texts = conversionslogic.get_button_texts(self.main_lang)
        self.multiresults = conversionslogic.get_multiresults_translation(self.main_lang)
        conversionslogic.register_fonts()
        self.setup_ui()

    def setup_ui(self):
        temp_unit_color = (0.75, 0.55, 0.60, 1)
        metric_spinner_color = (0.65, 0.45, 0.50, 1)
        food_spinner_color = (0.60, 0.40, 0.45, 1)
        convert_button_color = (0.20, 0.45, 0.25, 1)
        copy_button_color = (0.40, 0.65, 0.45, 1)
        reset_button_color = (0.8, 0.2, 0.2, 1)
        multiply_button_color = (0.8, 0.4, 0.4, 1)
        save_button_color = (0.5, 0.5, 0.7, 1)
        back_button_color = (0.7, 0.7, 0.7, 1)  # Added this line for the back button color

        temp_layout = BoxLayout(size_hint_y=None, height='30dp', spacing=5, size_hint_x=1)
        self.temp_value = NumericInput(multiline=False, size_hint_x=0.3, font_name=self.main_font, 
                                       foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1),
                                       font_size='11sp')
        self.temp_unit = Spinner(text='Fahrenheit', values=('Celsius', 'Fahrenheit'), 
                                 size_hint_x=0.7, font_name=self.main_font,
                                 background_normal='', background_color=temp_unit_color)
        temp_layout.add_widget(self.temp_value)
        temp_layout.add_widget(self.temp_unit)
        self.add_widget(temp_layout)

        input_layout = GridLayout(cols=3, spacing=5, size_hint_y=None, height='200dp', size_hint_x=1)
        self.inputs = []
        for i in range(8):
            value_entry = NumericInput(multiline=False, size_hint_x=0.2, font_name=self.main_font, 
                                       foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1),
                                       font_size='11sp')
            metric_spinner = Spinner(text=self.measurements[0], values=self.measurements, font_name=self.main_font,
                                     size_hint_x=0.3, background_normal='', background_color=metric_spinner_color)
            food_spinner = Spinner(text=list(self.foodnames)[i][1][self.main_lang], 
                                   values=[name[self.main_lang] for _, name in self.foodnames],
                                   font_name=self.main_font, size_hint_x=0.5,
                                   background_normal='', background_color=food_spinner_color)
            input_layout.add_widget(value_entry)
            input_layout.add_widget(metric_spinner)
            input_layout.add_widget(food_spinner)
            self.inputs.append((value_entry, metric_spinner, food_spinner))
        self.add_widget(input_layout)

        scroll_view = ScrollView(size_hint_y=None, height='250dp', size_hint_x=1)
        self.results_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll_view.add_widget(self.results_layout)
        self.add_widget(scroll_view)
        
        button_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=5, size_hint_x=1)
        button_colors = [convert_button_color, copy_button_color, reset_button_color, save_button_color, back_button_color]
        button_texts = ['button_convert', 'button_copy', 'button_reset', 'button_save_recipe', 'button_back']
        button_funcs = [self.convert, self.copy_results, self.reset_inputs, self.save_recipe, self.go_back]

        for text, func, color in zip(button_texts, button_funcs, button_colors):
            btn = Button(text=self.button_texts[text], on_press=func, font_name=self.main_font,
                         background_normal='', background_color=color, size_hint_x=0.2)
            button_layout.add_widget(btn)

        self.add_widget(button_layout)

        multiply_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=5, size_hint_x=1)
        multiply_btn = Button(text=self.button_texts["button_multiply_divide"], 
                              on_press=self.multiply_divide_results, 
                              font_name=self.main_font,
                              size_hint_x=0.7,
                              background_normal='',
                              background_color=multiply_button_color)
        self.factor_input = NumericInput(multiline=False, size_hint_x=0.3, font_name=self.main_font,
                                         foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1),
                                         font_size='11sp')
        multiply_layout.add_widget(multiply_btn)
        multiply_layout.add_widget(self.factor_input)
        self.add_widget(multiply_layout)

    def convert(self, instance, factor=1):
        self.results_layout.clear_widgets()
        
        if factor != 1:
            factor_label = Label(text=f"{self.multiresults} {factor}", 
                                 color=(0, 0, 0, 1), font_name=self.main_font,
                                 size_hint_y=None, height='20dp', font_size='14sp', bold=True)
            self.results_layout.add_widget(factor_label)
        
        language_fonts = {self.main_lang: self.main_font}
        for lang in self.additional_langs:
            language_fonts[lang] = conversionslogic.language_fonts.get(lang, self.main_font)
        
        temp_value = self.temp_value.text
        if temp_value:
            try:
                temp_value = float(temp_value)
                result = conversionslogic.fahrenheit_to_celsius(temp_value) if self.temp_unit.text == "Fahrenheit" else conversionslogic.celsius_to_fahrenheit(temp_value)
                label = Label(text=f"{result:g} {'°C' if self.temp_unit.text == 'Fahrenheit' else '°F'}", 
                              color=(0, 0, 0, 1), font_name=self.main_font,
                              size_hint_y=None, height='20dp', font_size='11sp')
                self.results_layout.add_widget(label)
            except ValueError:
                pass
        
        main_language_results = []
        results_by_language = {lang: [] for lang in self.additional_langs}
        
        for value_entry, metric_spinner, food_spinner in self.inputs:
            if value_entry.text:
                try:
                    value = float(value_entry.text) * factor
                    food_name = food_spinner.text
                    measurement = metric_spinner.text
                    food_id = next((food_id for food_id, names in self.foodnames if names[self.main_lang] == food_name), None)
                    if food_id:
                        converted_value = conversionslogic.convert_measurement(food_id, measurement.lower(), value, self.main_lang)
                        if isinstance(converted_value, str):
                            main_language_results.append(f"{converted_value} {food_name}\n")
                        for lang in self.additional_langs:
                            translated_food_name = next((names[lang] for _, names in self.foodnames if names[self.main_lang] == food_name), None)
                            if translated_food_name:
                                converted_translated_value = conversionslogic.convert_measurement(food_id, measurement.lower(), value, lang)
                                if isinstance(converted_translated_value, str):
                                    results_by_language[lang].append(f"{converted_translated_value} {translated_food_name}\n")
                except ValueError:
                    pass

        for result in main_language_results:
            label = Label(text=result.strip(), color=(0, 0, 0, 1), 
                          font_name=self.main_font,
                          size_hint_y=None, height='20dp', font_size='14sp')
            self.results_layout.add_widget(label)


        def add_language_section(lang, results):
            separator = Widget(size_hint_y=None, height='1dp')
            separator.canvas.add(Color(0.5, 0.5, 0.5))
            separator.canvas.add(Rectangle(pos=separator.pos, size=separator.size))
            self.results_layout.add_widget(separator)

            header = Label(text=f"{conversionslogic.available_languages[lang]}:", 
                           color=(0, 0, 0, 1), font_name=language_fonts[lang],
                           size_hint_y=None, height='25dp', bold=True, font_size='14sp')
            self.results_layout.add_widget(header)

            for result in results:
                label = Label(text=result.strip(), color=(0, 0, 0, 1), 
                              font_name=language_fonts[lang],
                              size_hint_y=None, height='20dp', font_size='14sp')
                self.results_layout.add_widget(label)

        for lang, results in results_by_language.items():
            if results:
                add_language_section(lang, results)

        final_separator = Widget(size_hint_y=None, height='1dp')
        final_separator.canvas.add(Color(0.5, 0.5, 0.5))
        final_separator.canvas.add(Rectangle(pos=final_separator.pos, size=final_separator.size))
        self.results_layout.add_widget(final_separator)

    def copy_results(self, instance):
        results_text = '\n'.join([label.text for label in self.results_layout.children if isinstance(label, Label)])
        Clipboard.copy(results_text)

    def reset_inputs(self, instance):
        self.temp_value.text = ''
        self.factor_input.text = ''
        for value_entry, _, _ in self.inputs:
            value_entry.text = ''
        self.results_layout.clear_widgets()

    def multiply_divide_results(self, instance):
        if self.factor_input.text:
            try:
                factor = float(self.factor_input.text)
                self.convert(instance, factor)
            except ValueError:
                pass

    def go_back(self, instance):
            app = App.get_running_app()
            app.root.current = 'language'

    def save_recipe(self, instance):
        def save_with_name(name):
            # Prepare recipe data
            self.recipe_data = {
                "temperature": {
                    "value": self.temp_value.text,
                    "unit": self.temp_unit.text
                },
                "ingredients": [],
                "factor": self.factor_input.text,
                "main_language": self.main_lang,
                "additional_languages": self.additional_langs
            }
            
            for value_entry, metric_spinner, food_spinner in self.inputs:
                if value_entry.text:
                    food_name = food_spinner.text
                    food_id = next((food_id for food_id, names in self.foodnames if names[self.main_lang] == food_name), None)
                    self.recipe_data["ingredients"].append({
                        "value": value_entry.text,
                        "unit": metric_spinner.text,
                        "food_id": food_id
                    })
            
            # Check if the recipe name already exists
            result, status = conversionslogic.save_user_choices(
                name,
                self.temp_unit.text,
                [],  # Empty list since we're just checking the name
                "",
                self.main_lang,
                [],
            )
            
            if status == "Confirm_Overwrite":
                show_overwrite_confirmation(name)  # Pass only the name for confirmation
            else:
                name_popup.dismiss()  # Close popup after successful save

        
        def show_overwrite_confirmation(name):
            texts = conversionslogic.get_button_texts(self.main_lang)
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=texts["overwrite_recipe"]))
            buttons = BoxLayout(size_hint_y=None, height='40dp')
            yes_button = Button(text=texts["yes"])
            no_button = Button(text=texts["no"])
            buttons.add_widget(yes_button)
            buttons.add_widget(no_button)
            content.add_widget(buttons)

            overwrite_popup = Popup(title='', content=content, size_hint=(0.8, 0.3))

            def on_yes(instance):
                overwrite_popup.dismiss()
                
                # Second confirmation popup: "Are you sure?"
                are_you_sure_content = BoxLayout(orientation='vertical')
                are_you_sure_content.add_widget(Label(text=texts["are_you_sure"]))
                are_you_sure_buttons = BoxLayout(size_hint_y=None, height='40dp')
                sure_yes_button = Button(text=texts["yes"])
                sure_no_button = Button(text=texts["no"])
                are_you_sure_buttons.add_widget(sure_yes_button)
                are_you_sure_buttons.add_widget(sure_no_button)
                are_you_sure_content.add_widget(are_you_sure_buttons)

                are_you_sure_popup = Popup(title='', content=are_you_sure_content, size_hint=(0.8, 0.3))

                def on_sure_yes(instance):
                    # Save the recipe after double confirmation
                    conversionslogic.save_user_choices(
                        name,
                        self.temp_unit.text,
                        self.recipe_data["ingredients"],  # Use prepared recipe data here
                        self.factor_input.text,
                        self.main_lang,
                        self.additional_langs,
                        confirm_overwrite=True
                    )
                    are_you_sure_popup.dismiss()
                    name_popup.dismiss()  # Close all popups

                def on_sure_no(instance):
                    are_you_sure_popup.dismiss()

                sure_yes_button.bind(on_release=on_sure_yes)
                sure_no_button.bind(on_release=on_sure_no)
                are_you_sure_popup.open()

            def on_no(instance):
                overwrite_popup.dismiss()

            yes_button.bind(on_release=on_yes)
            no_button.bind(on_release=on_no)
            overwrite_popup.open()

        # Popup to get recipe name from user
        texts = conversionslogic.get_button_texts(self.main_lang)
        content = BoxLayout(orientation='horizontal', spacing=5)
        name_input = TextInput(multiline=False, font_name=self.main_font, size_hint_x=0.8)
        confirm_button = Button(text=">", size_hint_x=0.2)
        content.add_widget(name_input)
        content.add_widget(confirm_button)

        name_popup = Popup(
            title=texts["choose_name"], 
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            title_font=self.main_font
        )

        def on_confirm(instance):
            save_with_name(name_input.text)

        confirm_button.bind(on_press=on_confirm)
        name_input.bind(on_text_validate=on_confirm)

        name_popup.open()

    def load_recipe(self, recipe_details):
  
        # Set temperature
        temperature_value = recipe_details.get('temperature_value', '')
        temperature_unit = recipe_details.get('temperature_unit', '')
        self.temp_value.text = str(temperature_value)
        self.temp_unit.text = temperature_unit

        # Update language preferences
        language_preferences = recipe_details.get('language_preferences', {})
        main_lang = language_preferences.get('main_language')
        additional_langs = language_preferences.get('additional_languages')
        if main_lang and additional_langs:
            self.main_lang = main_lang
            self.additional_langs = additional_langs
            self.foodnames = conversionslogic.get_foodnames(self.main_lang, self.additional_langs)
            self.measurements = conversionslogic.get_measurements()
          
        # Set ingredients
        ingredients = recipe_details.get('foods', [])
        print(f"Ingredients: {ingredients}")
        for i, ingredient in enumerate(ingredients):
            if i < len(self.inputs):
                value_entry, metric_spinner, food_spinner = self.inputs[i]
                value_entry.text = str(ingredient.get('value', ''))
                metric_spinner.text = ingredient.get('unit', '')
                
                food_name = ingredient.get('food', '')
                food_spinner.text = food_name
                
        # Set multiplication factor
        self.factor_input.text = str(recipe_details.get('multiplication_factor', ''))
       
        # Update spinner values
        self.update_spinner_values()
        

        # Perform conversion to update results
        self.convert(None)
        

    def update_spinner_values(self):
        
        for i, (_, metric_spinner, food_spinner) in enumerate(self.inputs):
            # Update food spinner values based on the current language
            food_spinner.values = [food[self.main_lang] for _, food in self.foodnames]
            
            # Update measurement spinner values
            metric_spinner.values = self.measurements
            
            
    def update_language_preferences(self):
         
        # Fetch updated food names and measurements based on the selected languages
        self.foodnames = conversionslogic.get_foodnames(self.main_lang, self.additional_langs)
        self.measurements = conversionslogic.get_measurements()
        
        


      
