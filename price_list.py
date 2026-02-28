beton = {
    "M100-A": 419265,
    "M150-A": 431970,
    "M200-A": 470085,
    "M250-A": 520905,
    "M300-A": 584430,
    "M350-A": 609840,
    "M400-A": 635250,
    "M450-A": 686070
}

fbs_prices = {
    "ФБС 9.4.6-Т": 97650,
    "ФБС 12.4.6-Т": 126000,
    "ФБС 24.4.6-Т": 241500
}
price_distance=1800
price_distance_limit=70
distance_from=15
price_beton=30000

CATEGORIES_CONFIG = {
    "fbs": {
        "tovar_ru": "ФБС Блоки",
        "tovar_uz": "FBS Bloklar",
        "unit_ru": "шт",
        "unit_uz": "dona",
        "emoji": "🧱",
        "label_ru": "Тип блока",
        "label_uz": "Blok turi",
        "has_distance": False,  # Дистанция НЕ нужна
        "price_dict": fbs_prices
    },
    "beton": {
        "tovar_ru": "Бетон",
        "tovar_uz": "Beton",
        "unit_ru": "м³",
        "unit_uz": "m³",
        "emoji": "💧",
        "label_ru": "Марка",
        "label_uz": "Markasi",
        "has_distance": True,   # Дистанция НУЖНА
        "price_dict": beton
    }
}