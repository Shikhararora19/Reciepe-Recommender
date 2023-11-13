from flask import Flask, render_template, request
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
# Connect to the SQLite database
conn = sqlite3.connect("recipes.db")

# Define the function to generate recipe recommendations

# Create a Flask application object
app = Flask(__name__)
@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    # get user input from request form
    user_input = request.form
    print(user_input)  # print user input to check form data
    dietary_restrictions = user_input.getlist("diet")
    favorite_ingredients = user_input.get("ingredients")
    print(favorite_ingredients)  # print favorite ingredients to check value
    if favorite_ingredients:
        favorite_ingredients = favorite_ingredients.split(",")
    else:
        favorite_ingredients = []
    favorite_cuisine = user_input.get("cuisine")
    
    # load recipes from database
    conn = sqlite3.connect("recipes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM recipes")
    data = c.fetchall()
    conn.close()
    
    # convert recipe data to dataframe
    recipes_df = pd.DataFrame(data, columns=["id", "title", "sourceUrl", "vegetarian", "vegan", "gluten_free", "dairy_free", "ingredients"])
    
    print(recipes_df)  # print recipes dataframe to check data
    
    # filter recipes by dietary restrictions
    for restriction in dietary_restrictions:
        if "vegetarian" in dietary_restrictions:
            recipes_df = recipes_df[recipes_df["vegetarian"] == 1]
        if "vegan" in dietary_restrictions:
            recipes_df = recipes_df[recipes_df["vegan"] == 1]
        if "gluten_free" in dietary_restrictions:
            recipes_df = recipes_df[recipes_df["gluten_free"] == 1]
        if "dairy_free" in dietary_restrictions:
            recipes_df = recipes_df[recipes_df["dairy_free"] == 1]
    print(recipes_df)  # print filtered recipes dataframe to check data
    
    # calculate TF-IDF vectors for recipe ingredients
    vectorizer = TfidfVectorizer(stop_words="english")
    ingredient_vectors = vectorizer.fit_transform(recipes_df["ingredients"])
    print(ingredient_vectors)  # print ingredient vectors to check data
    
    # calculate cosine similarity between user input and recipe vectors
    favorite_ingredients_vector = vectorizer.transform([",".join(favorite_ingredients)])
    cosine_similarities = cosine_similarity(favorite_ingredients_vector, ingredient_vectors).flatten()
    print(cosine_similarities)  # print cosine similarities to check data
    
    # rank recipes by similarity score and return top 10 recommendations
    recipes_df["similarity_score"] = cosine_similarities
    recommendations_df = recipes_df.sort_values(by="similarity_score", ascending=False).head(10)
    recommendations = [
    {
        "id": row["id"],
        "title": row["title"],
        "sourceUrl": row["sourceUrl"],
        "vegetarian": row["vegetarian"],
        "vegan": row["vegan"],
        "gluten_free": row["gluten_free"],
        "dairy_free": row["dairy_free"],
        "ingredients": row["ingredients"],
    }
    for _, row in recommendations_df.iterrows()
]

    # render recommendations template with recommended recipes
    return render_template("recommendations.html", recommendations=recommendations)
    
# Define the route and the view function for the home page
@app.route("/", methods=["GET", "POST"])
def home():
    # If the user submits the form, process the input and generate recipe recommendations
    if request.method == "POST":
        ingredients = request.form["ingredients"]
        cuisine = request.form["cuisine"]
        recommendations = get_recommendations(ingredients, cuisine)
        return render_template("home.html", recommendations=recommendations)
        
            
    # If the user requests the home page, render the HTML template
    return render_template("home.html", recommendations="")

# Start the Flask application on the development server
if __name__ == "__main__":
    app.run(debug=True)
