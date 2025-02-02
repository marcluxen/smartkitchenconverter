from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from conversionslogic import (
    register_fonts, language_fonts, available_languages, get_button_texts,
    get_recipe_names, get_recipe_details, update_recipe_name, delete_recipe, get_recipes_info
)


register_fonts()

class LanguageButton(Button):
    code = StringProperty('')
    default_color = ListProperty([1, 1, 1, 1])
    selected_color = ListProperty([0, 1, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_color = self.background_color
        self.selected = False

class TouchableLabel(Label):
    def __init__(self, recipe_popup, **kwargs):
        super(TouchableLabel, self).__init__(**kwargs)
        self.recipe_popup = recipe_popup
        self.selected = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return self.recipe_popup.select_recipe(self)

class EditableTextInput(TextInput):
    def __init__(self, recipe_popup, **kwargs):
        super(EditableTextInput, self).__init__(**kwargs)
        self.recipe_popup = recipe_popup
        self.multiline = False
        self.original_text = self.text

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.select_all()
            else:
                self.recipe_popup.select_recipe(self)
        return super(EditableTextInput, self).on_touch_down(touch)

    def on_focus(self, instance, value):
        if not value:  # Lost focus
            if self.text != self.original_text:
                self.recipe_popup.perform_rename(self.original_text, self.text)
                self.original_text = self.text

    def on_text_validate(self):
        self.focus = False

class RecipePopup(Popup):
    def __init__(self, main_language, on_recipe_load, **kwargs):
        super(RecipePopup, self).__init__(**kwargs)
        self.title = "Recipe Selection"
        self.size_hint = (0.8, 0.8)
        self.selected_recipe = None
        self.main_language = main_language
        self.on_recipe_load = on_recipe_load

        # Initialize button_texts
        self.button_texts = get_button_texts(self.main_language)

        layout = BoxLayout(orientation='vertical')

        scroll_view = ScrollView(size_hint=(1, 0.8))
        # Add a white background to the ScrollView
        with scroll_view.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.scroll_bg = Rectangle(size=scroll_view.size, pos=scroll_view.pos)
        scroll_view.bind(size=self.update_scroll_bg, pos=self.update_scroll_bg)
        
        self.recipe_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=1)
        self.recipe_list.bind(minimum_height=self.recipe_list.setter('height'))
        
        self.update_recipe_list()

        scroll_view.add_widget(self.recipe_list)
        layout.add_widget(scroll_view)

        button_layout = BoxLayout(size_hint=(1, 0.2))
        
        load_button = Button(text=self.button_texts['load'], on_press=self.load_recipe)
        rename_button = Button(text=self.button_texts['rename'], on_press=self.rename_recipe)
        delete_button = Button(text=self.button_texts['delete'], on_press=self.delete_recipe)

        button_layout.add_widget(load_button)
        button_layout.add_widget(rename_button)
        button_layout.add_widget(delete_button)

        layout.add_widget(button_layout)
        
        self.content = layout

    def update_scroll_bg(self, instance, value):
        """Update the background rectangle of the ScrollView."""
        self.scroll_bg.size = instance.size
        self.scroll_bg.pos = instance.pos

    def update_recipe_list(self):
        self.recipe_list.clear_widgets()
        for name in get_recipe_names():  # Call the function that returns alphabetized names
            recipes = get_recipes_info()
            details = recipes[name]
            recipe_language = details['language_preferences']['main_language']
            text_input = EditableTextInput(
                self,
                text=name,
                size_hint_y=None,
                height=40,
                font_name=language_fonts[recipe_language],
                background_color=(1, 1, 1, 1),
                background_normal='',
                background_active='',
                border=(0, 0, 0, 0)
            )
            self.recipe_list.add_widget(text_input)    

    def select_recipe(self, instance):
        if self.selected_recipe:
            self.selected_recipe.background_color = (1, 1, 1, 1)
        self.selected_recipe = instance
        self.selected_recipe.background_color = (0, 1, 0, 0.1)


    def select_recipe(self, instance):
        if self.selected_recipe:
            self.selected_recipe.background_color = (1, 1, 1, 1)
        self.selected_recipe = instance
        self.selected_recipe.background_color = (0, 1, 0, 0.1)

    def load_recipe(self, instance):
        if self.selected_recipe:
            recipe_details = get_recipe_details(self.selected_recipe.text)
            self.on_recipe_load(recipe_details)
            self.dismiss()

    def rename_recipe(self, instance):
        if self.selected_recipe:
            self.selected_recipe.focus = True

    def perform_rename(self, old_name, new_name):
        if old_name != new_name:
            if new_name in get_recipes_info():
                self.show_rename_popup(old_name, new_name)
            else:
                self.do_rename(old_name, new_name)

    def show_rename_popup(self, old_name, new_name):
        texts = get_button_texts(self.main_language)
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=texts['overwrite_recipe']))
        buttons = BoxLayout(size_hint_y=None, height=40)
        yes_button = Button(text=texts['yes'])
        no_button = Button(text=texts['no'])
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)

        popup = Popup(title='', content=content, size_hint=(0.8, 0.3))

        def on_yes(instance):
            popup.dismiss()
            self.do_rename(old_name, new_name)

        def on_no(instance):
            popup.dismiss()
            self.selected_recipe.text = old_name  # Revert the change

        yes_button.bind(on_release=on_yes)
        no_button.bind(on_release=on_no)

        popup.open()

    def do_rename(self, old_name, new_name):
        success = update_recipe_name(old_name, new_name)
        if success:
            self.selected_recipe.text = new_name
            self.selected_recipe.original_text = new_name
        else:
            self.selected_recipe.text = old_name  # Revert the change
        self.update_recipe_list()  # Refresh the recipe list after renaming
        self.selected_recipe = None  # Reset selection after renaming is complete
   
    def delete_recipe(self, instance):
        if self.selected_recipe:
            recipe_name = self.selected_recipe.text
            texts = get_button_texts(self.main_language)
            
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=texts['are_you_sure']))
            buttons = BoxLayout(size_hint_y=None, height=40)
            yes_button = Button(text=texts['yes'])
            no_button = Button(text=texts['no'])
            buttons.add_widget(yes_button)
            buttons.add_widget(no_button)
            content.add_widget(buttons)

            popup = Popup(title='', content=content, size_hint=(0.8, 0.3))

            def on_yes(instance):
                success = delete_recipe(recipe_name)
                if success:
                    self.update_recipe_list()
                popup.dismiss()

            def on_no(instance):
                popup.dismiss()

            yes_button.bind(on_release=on_yes)
            no_button.bind(on_release=on_no)

            popup.open()

class langselect(FloatLayout):
    selected_language_1 = StringProperty('en')
    selected_other_languages = ListProperty([])

    def __init__(self, on_language_select, on_recipe_load, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        self.left_buttons = []
        self.right_buttons = []
        self.on_language_select = on_language_select
        self.on_recipe_load = on_recipe_load
        self.setup_ui()

    def setup_ui(self):
        main_layout = GridLayout(cols=2, size_hint=(1, 0.9), pos_hint={'top': 1})
        
        column_configs = [
            ('left', '1', (0.8, 0.5, 0.7, 1)),
            ('right', '(2, 3, 4)', (1, 0.7, 0.8, 1))
        ]

        for side, title, color in column_configs:
            layout = GridLayout(cols=1, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            
            layout.add_widget(self._create_title_label(title))
            
            for code, name in available_languages.items():
                btn = self._create_language_button(name, code, color, side)
                layout.add_widget(btn)
            
            main_layout.add_widget(layout)
        
        self.add_widget(main_layout)

        self.load_recipe_button = self.create_load_recipe_button()
        self.add_widget(self.load_recipe_button)
        
        self.submit_button = self._create_submit_button()
        self.add_widget(self.submit_button)

    def _create_title_label(self, title):
        return Label(
            text=title, 
            size_hint=(1, None),
            height='20dp',
            color=(0.8, 0.2, 0.2, 1), 
            bold=True, 
            font_name="NotoSans",
            font_size='18sp',
            text_size=(None, 20),  # Changed from '20dp' to 20
            valign='middle',
            halign='center'
        )

    def _create_language_button(self, name, code, color, side):
        btn = LanguageButton(
            text=name, 
            code=code, 
            background_color=color, 
            font_name=language_fonts[code],
            size_hint=(1, None),
            height='40dp'
        )
        btn.bind(on_press=self.on_left_button_press if side == 'left' else self.on_right_button_press)
        
        if side == 'left':
            self.left_buttons.append(btn)
            if code == 'en':  # Pre-select English
                btn.selected = True
                btn.background_color = btn.selected_color
        else:
            self.right_buttons.append(btn)
        
        return btn

    def create_load_recipe_button(self):
        btn = Button(
            text="",  # Initially empty
            size_hint=(0.4, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.05},  # Lower position (below submit button)
            disabled=True,  # Initially disabled
            background_color=(1, 0.71, 0.76, 1),  # Medium pastel pink
            font_name=language_fonts['en']  # Default to English font initially
        )
        btn.bind(on_press=self.open_recipe_popup)
        return btn

    def _create_submit_button(self):
        return Button(
            text=">",
            font_size='30sp',
            size_hint=(0.4, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.15},  # Higher position (above load recipe button)
            background_color=(0, 1, 0, 1),  # Green color (RGBA)
            on_press=self.submit_selection
        )
    
    def on_left_button_press(self, button):
        for btn in self.left_buttons:
            btn.selected = btn == button
            btn.background_color = btn.selected_color if btn.selected else btn.default_color
        self.selected_language_1 = button.code
        self.update_load_recipe_button()

    def on_right_button_press(self, button):
        if button.selected:
            button.selected = False
            button.background_color = button.default_color
            self.selected_other_languages.remove(button.code)
        else:
            if len(self.selected_other_languages) < 3:
                button.selected = True
                button.background_color = button.selected_color
                self.selected_other_languages.append(button.code)
            else:
                oldest_code = self.selected_other_languages.pop(0)
                oldest_button = next(btn for btn in self.right_buttons if btn.code == oldest_code)
                oldest_button.selected = False
                oldest_button.background_color = oldest_button.default_color
                
                button.selected = True
                button.background_color = button.selected_color
                self.selected_other_languages.append(button.code)

    def update_load_recipe_button(self):
        button_texts = get_button_texts(self.selected_language_1)
        self.load_recipe_button.text = button_texts["button_recipes"]
        self.load_recipe_button.font_name = language_fonts[self.selected_language_1]  # Update font
        self.load_recipe_button.disabled = False

    def open_recipe_popup(self, instance):
        popup = RecipePopup(main_language=self.selected_language_1, on_recipe_load=self.on_recipe_load)
        popup.open()

    def submit_selection(self, instance):
        main_lang = self.selected_language_1
        additional_langs = self.selected_other_languages
        self.on_language_select(main_lang, additional_langs)

