import fooddata
import json
import os

def get_langs():
    """Return a list of available languages from the food data."""
    return list(fooddata.food_data[0]['names'].keys())

def get_measurements():
    """Return a list of available measurements from the food data, including grams and kilograms."""
    measurement_keys = list(fooddata.food_data[0]['measurements'].keys())
    measurement_keys.append('grams')
    measurement_keys.append('kilograms')
    return measurement_keys

def get_foodnames(main_lang, additional_langs):
    """Return a list of food names with their IDs in specified languages."""
    foodnames = []
    for food in fooddata.food_data:
        food_id = food['id']
        food_names = {lang: food['names'].get(lang, "") for lang in [main_lang] + additional_langs}
        foodnames.append((food_id, food_names))
    return foodnames

def get_button_texts(selected_language):
    """Retrieve button texts for the specified language."""
    return fooddata.buttonstext[selected_language]

def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return round((fahrenheit - 32) * 5.0 / 9.0)

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return round((celsius * 9.0 / 5.0) + 32)

def round_to_nearest_quarter(value):
    """Round value to the nearest 0.25."""
    return round(value * 4) / 4

def get_conversion_factors(food_id):
    """Retrieve conversion factors for a given food ID and return them as floats."""
    food_item = next((food for food in fooddata.food_data if food['id'] == food_id), None)
    conversion_factors = {}
    if food_item is not None:
        for factor, value in food_item.get('measurements', {}).items():
            conversion_factors[factor] = float(value)
    return conversion_factors

def get_unit_translation(language, unit):
    """Get the appropriate unit translation based on the given language."""
    if language in fooddata.unit_translations:
        return fooddata.unit_translations[language].get(unit, unit)
    return unit

def convert_measurement(food_id, measurement_name, value, language):
    """Convert a given measurement value based on whether it's metric or non-metric."""
    conversion_factors = get_conversion_factors(food_id)
    
    if measurement_name == 'grams':
        result = convert_grams_to_non_metric(value, conversion_factors)
        return result
    
    elif measurement_name == 'kilograms':
        value_in_grams = value * 1000  # Convert kilograms to grams
        result = convert_grams_to_non_metric(value_in_grams, conversion_factors)
        return result
    
    else:
        if measurement_name not in conversion_factors:
            return "Invalid measurement type."
        
        conversion_factor = conversion_factors[measurement_name]
        grams = value * conversion_factor
        rounded_value = round_grams(grams)
        unit = 'gram' if rounded_value < 1000 else 'kilogram'
        if rounded_value >= 1000:
            rounded_value = round(rounded_value / 1000, 1)  # Round to 1 decimal place for kilograms
        localized_unit = get_unit_translation(language, unit)
        result_string = f"{rounded_value} {localized_unit}"
        return result_string

def convert_grams_to_non_metric(value_in_grams, conversion_factors):
    """Convert grams to non-metric measurements based on specified rules."""
    if value_in_grams < 10:
        teaspoons = value_in_grams / conversion_factors.get('teaspoon', 1)
        result = round_to_nearest_quarter(teaspoons)
        return f"{result} teaspoon(s)"
    elif value_in_grams < 50:
        tablespoons = value_in_grams / conversion_factors.get('tablespoon', 1)
        result = round_to_nearest_quarter(tablespoons)
        return f"{result} tablespoon(s)"
    elif value_in_grams < 100:
        ounces = value_in_grams / conversion_factors.get('ounce', 1)
        result = round(ounces, 1)
        return f"{result} ounce(s)"
    elif value_in_grams < 1000:
        cups = value_in_grams / conversion_factors.get('cup', 1)
        result = round(cups, 1)
        return f"{result} cup(s)"
    else:
        pounds = value_in_grams / conversion_factors.get('pound', 1)
        result = round(pounds, 1)
        return f"{result} pound(s)"

def round_grams(grams):
    """Round the grams based on specific rules."""
    if grams < 50:
        return max(round(grams), 0.25)
    elif 50 <= grams <= 1000:
        return round(grams / 5) * 5
    else:
        return round(grams / 10) * 10

from kivy.core.text import LabelBase

def register_fonts():
    LabelBase.register(name="NotoSans", fn_regular="fonts/NotoSans-Regular.ttf")
    LabelBase.register(name="NotoSansJP", fn_regular="fonts/NotoSansJP-Regular.ttf")
    LabelBase.register(name="NotoSansSC", fn_regular="fonts/NotoSansSC-Regular.ttf")
    LabelBase.register(name="NotoSansArabic", fn_regular="fonts/NotoSansArabic-Regular.ttf")

language_fonts = {
    "en": "NotoSans", "de": "NotoSans", "es": "NotoSans", "fr": "NotoSans",
    "nl": "NotoSans", "it": "NotoSans", "pt": "NotoSans",
    "ja": "NotoSansJP", "zh": "NotoSansSC", "ar": "NotoSansArabic"
}

available_languages = {
    "en": "English", "de": "Deutsch", "es": "Español", "fr": "Français",
    "nl": "Nederlands", "it": "Italiano", "pt": "Português",
    "ja": "日本語", "zh": "中文", "ar": "العربية"
}

def get_multiresults_translation(main_lang):
    return fooddata.multiresults[main_lang]

def save_user_choices(name, temp_unit, foods, factor, main_lang, additional_langs, confirm_overwrite=False):
    file_path = 'recipes.json'
    
    user_choice = {
        "temperature_unit": temp_unit,
        "foods": foods,  # This now contains only value, unit, and food_id
        "multiplication_factor": factor,
        "language_preferences": {
            "main_language": main_lang,
            "additional_languages": additional_langs
        }
    }
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    
    name_existed = name in data
    
    if name_existed and not confirm_overwrite:
        return None, "Confirm_Overwrite"
    
    data[name] = user_choice
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

    return user_choice, "Updated" if name_existed else "Created"



def get_recipe_names():
    recipes = get_recipes_info()
    return sorted(list(recipes.keys()))  # Alphabetize the list of recipe names

def get_recipe_details(recipe_name):
    recipes = get_recipes_info()
    return recipes.get(recipe_name)

def get_recipes_info():
    with open('recipes.json', 'r') as file:
        recipes = json.load(file)
    return recipes

def save_recipes_info(recipes):
    with open('recipes.json', 'w') as file:
        json.dump(recipes, file, indent=4)

def update_recipe_name(old_name, new_name):
    with open('recipes.json', 'r', encoding='utf-8') as file:
        recipes = json.load(file)
    
    if old_name in recipes:
        recipes[new_name] = recipes.pop(old_name)
    
    with open('recipes.json', 'w', encoding='utf-8') as file:
        json.dump(recipes, file, indent=4, ensure_ascii=False)
    
    return True


def delete_recipe(recipe_name):
    try:
        with open('recipes.json', 'r', encoding='utf-8') as file:
            recipes = json.load(file)
        
        if recipe_name in recipes:
            del recipes[recipe_name]
            
            with open('recipes.json', 'w', encoding='utf-8') as file:
                json.dump(recipes, file, indent=4, ensure_ascii=False)
            
            return True
        else:
            return False
    except Exception as e:
        print(f"Error deleting recipe: {e}")
        return False
    

def on_recipe_load(self, recipe_details):
    # Update temperature
    self.temp_value.text = str(recipe_details['temperature']['value'])
    self.temp_unit.text = recipe_details['temperature']['unit']

    # Update ingredients
    for i, ingredient in enumerate(recipe_details['ingredients']):
        if i < len(self.inputs):
            value_entry, metric_spinner, food_spinner = self.inputs[i]
            value_entry.text = str(ingredient['value'])
            metric_spinner.text = ingredient['unit']
            food_name = next((names[self.main_lang] for food_id, names in self.foodnames if food_id == ingredient['food_id']), '')
            food_spinner.text = food_name

    # Clear any remaining inputs
    for i in range(len(recipe_details['ingredients']), len(self.inputs)):
        value_entry, metric_spinner, food_spinner = self.inputs[i]
        value_entry.text = ''
        metric_spinner.text = self.measurements[0]
        food_spinner.text = list(self.foodnames)[0][1][self.main_lang]

    # Update multiplication factor
    self.factor_input.text = str(recipe_details['factor'])

    # Update language preferences
    self.main_lang = recipe_details['main_language']
    self.additional_langs = recipe_details['additional_languages']
    self.update_language_preferences()

    # Perform conversion to update results
    self.convert(None)

def update_language_preferences(self):
    self.main_font = conversionslogic.language_fonts[self.main_lang]
    self.button_texts = conversionslogic.get_button_texts(self.main_lang)
    self.multiresults = conversionslogic.get_multiresults_translation(self.main_lang)
    self.foodnames = conversionslogic.get_foodnames(self.main_lang, self.additional_langs)
    
    # Update food spinners
    for _, _, food_spinner in self.inputs:
        food_spinner.values = [name[self.main_lang] for _, name in self.foodnames]
    
    # Update button texts
    for child in self.children:
        if isinstance(child, BoxLayout):
            for button in child.children:
                if isinstance(button, Button):
                    for key, value in self.button_texts.items():
                        if button.text == self.button_texts[key]:
                            button.text = value
                            break
    
    # Refresh the UI
    self.convert(None)




