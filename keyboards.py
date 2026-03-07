from aiogram import Bot, Dispatcher, types,F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder,ReplyKeyboardBuilder
from price_list import *
from datetime import datetime
from aiogram.filters import BaseFilter

# class NotBackButton(BaseFilter):
#     async def __call__(self, message: types.Message) -> bool:
#         # Возвращает True, если текста НЕТ в списке кнопок "Назад"
#         return message.text not in ["⬅️ Назад", "⬅️ Orqaga"]

def error_message(lang):
    error_text = "Пожалуйста, выберите категорию из меню 👇" if lang == "ru" else "Iltimos, menyudan tanlang 👇"

    return error_text
def get_lang_kb():
    kb = [[types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇺🇿 O'zbek tili")]]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_beton_keyboard(lang):

    marks = list(beton.keys())

    btns = []

    for i in range(0, len(marks), 2):
        row = []
        row.append(types.KeyboardButton(text=marks[i]))
        # Проверяем, есть ли еще одна марка для пары в ряду
        if i + 1 < len(marks):
            row.append(types.KeyboardButton(text=marks[i + 1]))
        btns.append(row)

    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Orqaga"
    btns.append([types.KeyboardButton(text=back_text)])

    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)


def get_fbs_keyboard(lang):
    marks = list(fbs_prices.keys())

    btns = []

    for i in range(0, len(marks), 2):
        row = []
        row.append(types.KeyboardButton(text=marks[i]))
        # Проверяем, есть ли еще одна марка для пары в ряду
        if i + 1 < len(marks):
            row.append(types.KeyboardButton(text=marks[i + 1]))
        btns.append(row)

    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Orqaga"
    btns.append([types.KeyboardButton(text=back_text)])

    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)



def get_main_menu_kb(lang):
    if lang == "ru":
        btns = [
            [types.KeyboardButton(text="🏗 Заказать")],
            [types.KeyboardButton(text="🧾Мои заявки")], # Новая кнопка
            [types.KeyboardButton(text="⬅️ Назад")]
        ]
    else:
        btns = [
            [types.KeyboardButton(text="🏗 Buyurtma berish")],
            [types.KeyboardButton(text="🧾 Mening buyurtmalarim")], # Yangi tugma
            [types.KeyboardButton(text="⬅️ Orqaga")]
        ]
    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)


def get_cat_menu(lang):
    if lang == "ru":
        btns = [
            [types.KeyboardButton(text="Товарный бетон"), types.KeyboardButton(text="Плиты перекрытия ПБ")],

            [types.KeyboardButton(text="Фундаментальные блоки"), types.KeyboardButton(text="Лотки 6м")],

            [types.KeyboardButton(text="⬅️ Назад")]
        ]
    else:
        btns = [
            [types.KeyboardButton(text="Tayyor beton"), types.KeyboardButton(text="Qavat plitalari")],
            [types.KeyboardButton(text="Bloklar"), types.KeyboardButton(text="Lotoklar 6m")],
            [types.KeyboardButton(text="⬅️ Orqaga")]
        ]
    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)


def get_calculate_inline(lang):
    builder = InlineKeyboardBuilder()

    # Кнопка расчета
    calc_text = "🧮 Рассчитать стоимость" if lang == "ru" else "🧮 Hisoblash"
    builder.button(text=calc_text, callback_data="calculate_total")

    # Кнопка Заказать
    order_text = "✅ Заказать" if lang == "ru" else "✅ Buyurtma berish"
    builder.button(text=order_text, callback_data="confirm_order_withoutcal")

    builder.adjust(1)  # Кнопки друг под другом
    return builder.as_markup()


def get_final_order_keyboard(lang):
    builder = InlineKeyboardBuilder()


    confirm_text = "✅ Заказать" if lang == "ru" else "✅ Buyurtma berish"
    cancel_text = "❌ Отменить" if lang == "ru" else "❌ Bekor qilish"

    builder.button(text=confirm_text, callback_data="confirm_order")
    builder.button(text=cancel_text, callback_data="cancel_order")


    builder.adjust()
    return builder.as_markup()

def get_final_order_keyboard_last(lang):
    builder = InlineKeyboardBuilder()

    # Кнопки действий
    confirm_text = "✅ Отправить" if lang == "ru" else "✅ Yuborish"
    cancel_text = "❌ Отменить" if lang == "ru" else "❌ Bekor qilish"

    builder.button(text=confirm_text, callback_data="confirm_order_last")
    builder.button(text=cancel_text, callback_data="cancel_order")

    # Делаем кнопки в один ряд
    builder.adjust(2)
    return builder.as_markup()

def get_admin_order_keyboard(user_id):
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Выполнено", callback_data=f"order_done_{user_id}")
    builder.button(text="❌ Отменить", callback_data=f"order_cancel_{user_id}")
    builder.adjust(2)
    return builder.as_markup()




def quantity_or_unit(lang,category,quantity):
    if category == "beton":
        unit = "м³"
    else:
        unit = "шт" if lang == "ru" else "dona"


    return f"{quantity} {unit}"



async def choosing_language(message):
    if "Русский" in message.text:
        lang = "ru"
        await message.answer("Установлен русский язык. Добро пожаловать! 👋",reply_markup=get_main_menu_kb("ru"))
    else:
        lang = "uz"

        await message.answer("O'zbek tili tanlandi. Xush kelibsiz! 👋",reply_markup=get_main_menu_kb("uz"))


def get_summary_text(category, lang, quantity=None, product=None, distance=None, cart=None):
    config = CATEGORIES_CONFIG.get(category, CATEGORIES_CONFIG["beton"])
    tovar_name = config[f"tovar_{lang}"]
    unit = config[f"unit_{lang}"]
    label = config[f"label_{lang}"]
    emoji = config["emoji"]

    # --- ЛОГИКА ДЛЯ ПЛИТ И ФБС (КОРЗИНА) ---
    if (category == "plita" or category == "fbs") and cart:
        lines = []
        if lang == "ru":
            title = "Блоки" if category == "fbs" else "Плиты"
            lines.append(f"📝 <b>Ваш заказ ({title}):</b>")
            lines.append(f"━━━━━━━━━━━━━━")

            for i, item in enumerate(cart, 1):
                # Для плит добавляем (X м), для ФБС — нет
                dist_info = f" ({item['distance']} м)" if category == "plita" else ""
                lines.append(f"{i}. {item['product']} — {item['quantity']} {unit}{dist_info}")

            choose_text = "Выберите действие:"
        else:
            title = "Bloklar" if category == "fbs" else "Plitalar"
            lines.append(f"📝 <b>Sizning buyurtmangiz ({title}):</b>")
            lines.append(f"━━━━━━━━━━━━━━")

            for i, item in enumerate(cart, 1):
                dist_info = f" ({item['distance']} m)" if category == "plita" else ""
                lines.append(f"{i}. {item['product']} — {item['quantity']} {unit}{dist_info}")

            choose_text = "Harakatni tanlang:"

        lines.append(f"━━━━━━━━━━━━━━")
        summary = "\n".join(lines)
        return summary, choose_text

    # --- ЛОГИКА ДЛЯ ОСТАЛЬНЫХ (БЕТОН, ЛОТКИ) ---
    if lang == "ru":
        lines = [
            f"📝 <b>Ваш выбор:</b>",
            f"━━━━━━━━━━━━━━",
            f"{emoji} <b>Товар:</b> {tovar_name}",
            f"🏗 <b>{label}:</b> <code>{product}</code>",
            f"🔢 <b>Количество:</b> <code>{quantity} {unit}</code>"
        ]
        if config.get("has_distance") and distance:
            lines.append(f"🚚 <b>Дистанция:</b> <code>{distance} км</code>")

        if category == "lotok":
            # Удаляем строку с продуктом, если это лотки (как в твоем оригинале)
            lines = [l for l in lines if label not in l]

        lines.append(f"━━━━━━━━━━━━━━")
        summary = "\n".join(lines)
        choose_text = "Выберите действие:"
    else:
        lines = [
            f"📝 <b>Sizning tanlovingiz:</b>",
            f"━━━━━━━━━━━━━━",
            f"{emoji} <b>Mahsulot:</b> {tovar_name}",
            f"🏗 <b>{label}:</b> <code>{product}</code>",
            f"🔢 <b>Miqdori:</b> <code>{quantity} {unit}</code>"
        ]
        if config.get("has_distance") and distance:
            lines.append(f"🚚 <b>Masofa:</b> <code>{distance} km</code>")

        if category == "lotok":
            lines = [l for l in lines if label not in l]

        lines.append(f"━━━━━━━━━━━━━━")
        summary = "\n".join(lines)
        choose_text = "Harakatni tanlang:"

    return summary, choose_text


def making_order_text(lang, category, message):
    if category == "plita":
        if lang == "ru":
            text = (f"✅ Вы выбрали: **{message}**\n\n"
                    f"📏 Введите точную длину плиты (в метрах, например: 4.1 или 3.9):")
        else:
            text = (f"✅ Siz **{message}** ni tanladingiz.\n\n"
                    f"📏 Plita uzunligini kiriting (metrda, masalan: 4.1 yoki 3.9):")
    else:
        # Стандартная логика для Бетона / ФБС
        if lang == "ru":
            text = (f"✅ Вы выбрали: **{message}**\n\n"
                    f"🚚 Введите расстояние доставки вручную (от 1 до 70 км):")
        else:
            text = (f"✅ Siz **{message}** ni tanladingiz.\n\n"
                    f"🚚 Yetkazib berish masofasini qo'lda kiriting (1 dan 70 km gacha):")

    return text


def making_order_beton(lang, message):
    if lang == "ru":
        text = (f"✅ Вы выбрали: **{message}**\n\n"
                f"🚚 Введите расстояние доставки вручную (от 1 до 70 км):")
    else:
        text = (f"✅ Siz **{message}** ni tanladingiz.\n\n"
                f"🚚 Yetkazib berish masofasini qo'lda kiriting (1 dan 70 km gacha):")

    return text


def get_quantity_text(lang):
    text="🔢 Введите необходимое количество:" if lang == "ru" else "🔢 Kerakli miqdorni kiriting:"
    return text


def back_menu(category,lang):

    if category == "beton":
        keyboard=get_beton_keyboard(lang)
    elif category == "fbs":
        keyboard= get_fbs_keyboard(lang)

    elif category == "lotok":
        keyboard=get_cat_menu(lang)

    elif category == "plita":
        keyboard = get_plita_width_kb(lang)


    return keyboard


def calculate_total(
    category, lang, quantity,
    product=None, dist=None, cart=None,
    phone=None, name=None, date=None,
    is_manager=False, withoutcal=False, nasos=False
):
    config = CATEGORIES_CONFIG.get(category, CATEGORIES_CONFIG["beton"])
    tovar_name = config[f"tovar_{lang}"]
    emoji = config["emoji"]
    label = config[f"label_{lang}"]
    price_dict = config.get("price_dict", {})

    def fmt(val):
        return f"{int(val):,}".replace(",", " ")

    # 1. ЗАГОЛОВОК
    if is_manager:
        res_header = "🚀 <b>НОВЫЙ ЗАКАЗ!</b>"
    else:
        if withoutcal:
            res_header = f"📝 <b>{'Оформление заказа' if lang == 'ru' else 'Buyurtmani rasmiylashtirish'}:</b>"
        else:
            res_header = f"📊 <b>{'Итоговый расчет' if lang == 'ru' else 'Yakuniy hisob'}:</b>"

    # 2. ДАННЫЕ КЛИЕНТА (ВЕРХНИЙ БЛОК)
    client_top = ""
    if name or phone:
        name_line = f"👤 <b>{'Заказчик' if lang == 'ru' else 'Buyurtmachi'}:</b> {name}\n" if name else ""
        phone_line = f"📞 <b>{'Тел' if lang == 'ru' else 'Telefon'}:</b> {phone}\n" if phone else ""
        client_top = f"\n{name_line}{phone_line}"

    # 3. ИНФОРМАЦИЯ О ТОВАРЕ
    product_info = f"\n{emoji} <b>{'Категория' if lang == 'ru' else 'Kategoriya'}:</b> {tovar_name}\n"

    if category in ["plita", "fbs"] and cart:
        items_list = []
        for item in cart:
            p_name = item.get('product')
            p_qty = item.get('quantity')
            if category == "plita":
                p_dist = item.get('distance', '0')
                items_list.append(f"🔹 {p_name} ({p_dist} м) — {p_qty} шт.")
            else:
                items_list.append(f"🔹 {p_name} — {p_qty} шт.")
        product_info += "\n".join(items_list)
    elif product:
        product_info += f"🏗 <b>{label}:</b> {product}\n"
        product_info += f"🔢 <b>{'Количество' if lang == 'ru' else 'Miqdor'}:</b> {quantity} {config.get(f'unit_{lang}', '')}\n"
        if category == "beton" and dist:
            product_info += f"📍 <b>{'Дистанция' if lang == 'ru' else 'Masofa'}:</b> {dist} км\n"

    # 4. ЛОГИКА АВТОНАСОСА (ТОЛЬКО ДЛЯ БЕТОНА)
    nasos_line = ""
    if category == "beton":
        text_nasos = "✅ Да" if lang == "ru" else "✅ Ha"
        if not nasos:
            text_nasos = "❌ Нет" if lang == "ru" else "❌ Yo'q"
        label_nasos = "🚜 Автонасос:" if lang == "ru" else "🚜 Avtonasos:"
        nasos_line = f"{label_nasos} {text_nasos}\n"

    # 5. БЛОК КАЛЬКУЛЯЦИИ (ЦЕНЫ)
    calc_block = ""
    if not withoutcal:
        total_sum = 0
        if category == "plita":
            total_sum = sum(calculate_price_plita(i['product'], i['distance']) * int(i['quantity']) for i in cart)
        elif category == "fbs" and cart:
            total_sum = sum(price_dict.get(i['product'], 0) * int(i['quantity']) for i in cart)
        else:
            price_mat = price_dict if category == "lotok" else price_dict.get(product, 0)
            delivery = 0
            if category == "beton" and dist:
                delivery = price_beton if dist <= distance_from else price_beton + ((dist - distance_from) * price_distance)
            total_sum = quantity * (price_mat + delivery)

            # Для одиночных товаров (бетон/лоток) добавим расшифровку цены
            if category != "plita" and category != "fbs":
                calc_block += f"💵 <b>Цена:</b> {fmt(price_mat)} сум\n"
                if category == "beton":
                    calc_block += f"🚛 <b>Доставка:</b> {fmt(delivery)} сум\n"

        calc_block = f"━━━━━━━━━━━━━━\n{calc_block}✨ <b>ИТОГО: {fmt(total_sum)} сум</b>"

    # 6. ДАТА ОТГРУЗКИ (ВСЕГДА В КОНЦЕ)
    footer_date = ""
    if date:
        footer_date = f"\n\n🚛 <b>{'Дата Отгрузки' if lang == 'ru' else 'Yuklash sanasi'}:</b> {date}"

    # СБОРКА ФИНАЛЬНОГО ТЕКСТА
    if withoutcal:
        # Для клиента без цен
        result = (
            f"{res_header}\n"
            f"━━━━━━━━━━━━━━"
            f"{client_top}\n"
            f"{product_info}"
            f"{nasos_line}"
            f"━━━━━━━━━━━━━━"
            f"{footer_date}"
        )
    else:
        # Полный расчет (для менеджера или по кнопке Рассчитать)
        result = (
            f"{res_header}\n"
            f"━━━━━━━━━━━━━━"
            f"{client_top}\n"
            f"{product_info}"
            f"{nasos_line}\n"
            f"{calc_block}"
            f"{footer_date}"
        )

    return result

def plita_loop(category,lang):
    if category == "fbs":
        text = ("✅ Блок добавлена в список!\n\n") if lang == "ru" else (
            "✅ Blok ro'yxatga qo'shildi!\n\n")

    else:
        text = ("✅ Плита добавлена в список!\n\n"
                "Желаете добавить еще плиту другого размера ?") if lang == "ru" else (
            "✅ Plita ro'yxatga qo'shildi!\n\n"
            "Boshqa o'lchamdagi plita qo'shasizmi ?")


    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Добавить еще" if lang == "ru" else "➕ Yana qo'shish")
    builder.button(text="✅ Далее" if lang == "ru" else "✅ Davom etish")
    keyboard=builder.as_markup(resize_keyboard=True)


    return text,keyboard


def length_or_distance(category, lang):
    if category == "plita":
        return "📏 **Введите длину плиты (в метрах):**" if lang == "ru" else "📏 **Plita uzunligini kiriting (metrda):**"
    else:
        return "🚚 **Введите дистанцию доставки (1-70 км):**" if lang == "ru" else "🚚 **Yetkazib berish masofasini kiriting (1-70 km):**"


def get_plita_width_kb(lang):
    builder = ReplyKeyboardBuilder()

    # Кнопки ширины
    builder.button(text="1.2 м")
    builder.button(text="1.0 м")

    # Кнопка назад
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Orqaga"
    builder.row(types.KeyboardButton(text=back_text))

    return builder.as_markup(resize_keyboard=True)


def get_yes_no_keyboard(lang="ru"):
    builder = ReplyKeyboardBuilder()

    # Тексты кнопок
    yes_text = "✅ Да" if lang == "ru" else "✅ Ha"
    no_text = "❌ Нет" if lang == "ru" else "❌ Yo'q"

    # Добавляем кнопки с уникальными callback_data
    builder.button(text=yes_text)
    builder.button(text=no_text)

    # Располагаем их в один ряд
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)