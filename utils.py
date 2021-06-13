def pretty_string_recipe(ingredients, measures):
    ingredients = [i.strip() for i in ingredients]
    measures = [i.strip() for i in measures]
    return "\n".join(list(map(lambda x: "· " + " of ".join(x), (tuple(zip(measures, ingredients))))))


def present_cocktail(drink, lang):
    drink_name = drink["strDrink"]
    ingredients = list(filter(lambda x: x,
                              [drink[key] for key in drink.keys() if "strIngredient" in key]))
    measures = list(filter(lambda x: x,
                           [drink[key] for key in drink.keys() if "strMeasure" in key]))
    instructions = drink.get(f"strInstructions")
    if drink.get(f"strInstructions{lang}"):
        instructions = drink.get(f"strInstructions{lang}")
    return drink_name, pretty_string_recipe(ingredients, measures), instructions
