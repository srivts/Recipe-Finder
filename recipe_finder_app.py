from flask import Flask, request, render_template
import pandas as pd
app=Flask(__name__)
def load_data():
    data_path = "C:\\Users\\sandh\\OneDrive\\Desktop\\merged_recipes.csv"
    try:
        recipes_df = pd.read_csv(data_path)
        print("Data loaded successfully.")
        return recipes_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def parse_ingredients(ingredients_str):
    return set(ingredient.strip().lower() for ingredient in ingredients_str.split(','))

# Check if the recipe contains all the input ingredients
def check_ingredients(recipe_ingredients, input_ingredients_set):
    if isinstance(recipe_ingredients, list):
        recipe_ingredients_set = set(ingredient.lower() for ingredient in recipe_ingredients)
        return input_ingredients_set.issubset(recipe_ingredients_set)
    return False

# Find recipes that match the given ingredients
def find_recipes(ingredients_list, recipes_df):
    # Convert the comma-separated input into a set of ingredients
    input_ingredients_set = parse_ingredients(ingredients_list)

    # Apply the check_ingredients function to each row
    matched_recipes = recipes_df[recipes_df['ingredients'].apply(
        lambda x: check_ingredients(eval(x), input_ingredients_set) if isinstance(x, str) else False
    )]

    return matched_recipes

def display_recipes(recipe_id, recipes_df):
    # Find the recipe by its recipe_id
    recipe = recipes_df[recipes_df['id'] == recipe_id]

    if not recipe.empty:
        recipe = recipe.iloc[0]
        print(f"Recipe ID: {recipe['id']}")
        print(f"Name: {recipe['name']}")
        print(f"Description: {recipe['description']}")

        # Ingredients
        ingredients = eval(recipe['ingredients']) if isinstance(recipe['ingredients'], str) else recipe['ingredients']
        print(f"Ingredients: {(ingredients)}")

        # Steps
        steps = eval(recipe['steps']) if isinstance(recipe['steps'], str) else recipe['steps']
        print("Steps:")
        for index, step in enumerate(steps, 1):
            print(f"{index}. {step}")

        # Tags
        tags = eval(recipe['tags']) if isinstance(recipe['tags'], str) else recipe['tags']
        print(f"Tags: {', '.join(tags)}")



    else:
        print("Recipe not found.")
@app.route('/')
def index():
    return render_template('input.html')
@app.route('/find_recipes',methods=['POST'])

def find_recipes_route():
    ingredients_list=request.form['ingredients']
    recipes_df = load_data()
    if recipes_df is None:
        return "Unable to proceed as data could not be loaded.",500

    matched_recipes = find_recipes(ingredients_list, recipes_df)
    recipe_list=[{'id': recipe['id'],'name':recipe['name']}for __, recipe in matched_recipes.iterrows()]
    return render_template('recipes.html', recipes=recipe_list)

@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    recipes_df = load_data()
    if recipes_df is None:
        return "Unable to proceed as data could not be loaded.", 500
    recipe=recipes_df[recipes_df['id']==recipe_id]


    if not recipe.empty:
        recipe=recipe.iloc[0].to_dict()
        recipe['steps']=recipe['steps'].split(',')
        recipe['ingredients'] = recipe['ingredients'].split(',')
        recipe['tags']=recipe['tags'].split(',')


        # Nutrition
        nutrition_labels = ['calories(kcal)', 'total fat(g)', 'sodium(mg)', 'carbs(g)', 'sugars(g)', 'protein(g)',
                            'fiber(g)']
        nutrition_values = recipe['nutrition'].split(', ')  # nutrition is a comma-separated string in the dataset
        nutrition_list = list(zip(nutrition_labels, nutrition_values))


        return render_template('recipe_details.html', recipe=recipe, nutrition_list=nutrition_list)
    else:
        return 'recipe not found',404

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)