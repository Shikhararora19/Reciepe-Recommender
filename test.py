import requests
import sqlite3
import json
# Set up database connection
conn = sqlite3.connect('recipes.db')
c = conn.cursor()

# Create table to store recipes


# Make API request to Spoonacular for recipes
response = requests.get('https://api.spoonacular.com/recipes/random?number=1000&apiKey=e8822364237a405384fb516c70bc2b8d')

# Parse response and insert recipes into database
data = response.json()
for recipe in data['recipes']:
    ingrediants = recipe['extendedIngredients']
    ingrediants_array = []
    for ingrediant in ingrediants:
        ingrediants_array.append(ingrediant['name'])
    ingrediants_1 = my_bytes = json.dumps(ingrediants_array).encode('utf-8')

    title = recipe['title']
    c.execute("INSERT INTO recipes (id, title, ingredients, source, vegetarian, vegan, gluten_free, dairy_free) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          (recipe['id'], recipe['title'], ingrediants_1, recipe['sourceUrl'] ,recipe['vegetarian'] , recipe['vegan'], recipe['glutenFree'], recipe['dairyFree']))
# Commit changes and close connection
conn.commit()
conn.close()