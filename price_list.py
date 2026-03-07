MESSAGES = {
    "ask_name": {
        "ru": "👤 <b>Введите ваше имя:</b>",
        "uz": "👤 <b>Ismingizni kiriting:</b>"
    },
    "ask_phone": {
        "ru": "📱 <b>Введите ваш номер телефона:</b>\n<i>Например: +998901234567</i>",
        "uz": "📱 <b>Telefon raqamingizni kiriting:</b>\n<i>Masalan: +998901234567</i>"
    },
    "ask_date": {
        "ru": "📅 <b>Дата отгрузки (ДД.ММ.ГГГГ):</b>\n<i>Пример: 10.03.2026</i>",
        "uz": "📅 <b>Yuklash sanasi (KK.OO.YYYY):</b>\n<i>Masalan: 10.03.2026</i>"
    },
    "error_date": {
        "ru": "❌ Неверный формат даты!",
        "uz": "❌ Sana formati noto'g'ri!"
    }
}

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
price_plita_sm_12=2067
price_plita_sm_10=2756
start_price_12=214988
start_price_10=187425
def calculate_price_plita(product,distance):
    if product == "1.2 м":
        # Порог 3.9 метра
        if distance <= 3.9:
            price_per_one = start_price_12
        else:
            # Считаем разницу в см: (текущая длина - 3.9) * 100
            extra_sm = (distance - 3.9) * 100
            price_per_one = start_price_12 + (extra_sm * price_plita_sm_12)

    else:  # Для "1.0 м"
        # Порог 3.7 метра
        if distance <= 3.7:
            price_per_one = start_price_10
        else:
            # Считаем разницу в см: (текущая длина - 3.7) * 100
            extra_sm = (distance - 3.7) * 100
            price_per_one = start_price_10 + (extra_sm * price_plita_sm_10)

        # Итоговая сумма за все количество

    return int(price_per_one)

CATEGORIES_CONFIG = {
    "fbs": {
        "tovar_ru": "Фундаментальные блоки",
        "tovar_uz": "Bloklar",
        "unit_ru": "шт",
        "unit_uz": "dona",
        "emoji": "🧱",
        "label_ru": "Тип блока",
        "label_uz": "Blok turi",
        "has_distance": False,
        "price_dict": fbs_prices,
    },
    "beton": {
        "tovar_ru": "Товарный бетон",
        "tovar_uz": "Tayyor beton",
        "unit_ru": "м³",
        "unit_uz": "m³",
        "emoji": "💧",
        "label_ru": "Марка",
        "label_uz": "Markasi",
        "has_distance": True,
        "price_dict": beton
    },
    "lotok": {
        "tovar_ru": "Лотки 6м",
        "tovar_uz": "Lotoklar 6m",
        "unit_ru": "шт",
        "unit_uz": "dona",
        "emoji": "〰️",
        "label_ru": "Размер лотка",
        "label_uz": "Lotok o'lchami",
        "has_distance": False,
        "price_dict": 810000  # Заменил на переменную словаря
    },
    "plita": {
        "tovar_ru": "Плиты перекрытия ПБ",
        "tovar_uz": "Qavat plitalari",
        "unit_ru": "шт",
        "unit_uz": "dona",
        "emoji": "🏗",
        "label_ru": "Маркировка плиты",
        "label_uz": "Plita markirovkasi",
        "has_distance": True, # Обычно плиты заказывают без автоматического расчета доставки за км

    }
}

