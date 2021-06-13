import requests as rq
import json

from utils import present_cocktail

BASE_URL = "http://www.thecocktaildb.com/api/json/v1/1/"


def search_by_ingredient(name):
    try:
        results = json.loads(rq.get(f"{BASE_URL}filter.php?i={name}").text)["drinks"]
    except Exception:
        return None
    if results:
        return {drink.get("strDrink"): drink.get("idDrink") for drink in results[:5]}
    else:
        return None


def search_by_name(name):
    try:
        results = json.loads(rq.get(f"{BASE_URL}search.php?s={name}").text)["drinks"]
    except Exception:
        return None
    if results:
        return {drink.get("strDrink"): drink.get("idDrink") for drink in results[:5]}
    else:
        return None


def get_by_name(name, lang):
    drink = json.loads(rq.get(f"{BASE_URL}search.php?s={name}").text)["drinks"][0]
    return present_cocktail(drink, lang)


def get_random_cocktail(lang):
    drink = json.loads(rq.get(f"{BASE_URL}random.php").text)["drinks"][0]
    return present_cocktail(drink, lang)


if __name__ == "__main__":
    print(search_by_ingredient("gin"))
