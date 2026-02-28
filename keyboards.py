from aiogram import Bot, Dispatcher, types,F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from price_list import *
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
            [types.KeyboardButton(text="🛍 Заказать")],
            [types.KeyboardButton(text="📋 Мои заявки")], # Новая кнопка
            [types.KeyboardButton(text="⬅️ Назад")]
        ]
    else:
        btns = [
            [types.KeyboardButton(text="🛍 Buyurtma berish")],
            [types.KeyboardButton(text="📋 Mening buyurtmalarim")], # Yangi tugma
            [types.KeyboardButton(text="⬅️ Orqaga")]
        ]
    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)


def get_cat_menu(lang):
    if lang == "ru":
        btns = [
            [types.KeyboardButton(text="🏗 Бетон"), types.KeyboardButton(text="🧱 Плиты перекрытия")],

            [types.KeyboardButton(text="🟦 ФБС (Блоки)"), types.KeyboardButton(text="〰️ Лотки")],

            [types.KeyboardButton(text="⬅️ Назад")]
        ]
    else:
        btns = [
            [types.KeyboardButton(text="🏗 Beton"), types.KeyboardButton(text="🧱 Plitalar")],
            [types.KeyboardButton(text="🟦 FBS (Bloklar)"), types.KeyboardButton(text="〰️ Lotoklar")],
            [types.KeyboardButton(text="⬅️ Orqaga")]
        ]
    return types.ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)




def get_calculate_inline(lang):
    builder = InlineKeyboardBuilder()
    text = "🧮 Рассчитать стоимость" if lang == "ru" else "🧮 Hisoblash"
    # callback_data поможет нам отловить нажатие именно этой кнопки
    builder.button(text=text, callback_data="calculate_total")
    return builder.as_markup()


def get_final_order_keyboard(lang):
    builder = InlineKeyboardBuilder()

    # Кнопки действий
    confirm_text = "✅ Заказать" if lang == "ru" else "✅ Buyurtma berish"
    cancel_text = "❌ Отменить" if lang == "ru" else "❌ Bekor qilish"

    builder.button(text=confirm_text, callback_data="confirm_order")
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
    if category == "fbs":
        unit = "шт" if lang == "ru" else "dona"
    else:
        unit = "м³"

    return f"{quantity} {unit}"



async def choosing_language(message):
    if "Русский" in message.text:
        lang = "ru"
        await message.answer("Установлен русский язык. Добро пожаловать! 👋",reply_markup=get_main_menu_kb("ru"))
    else:
        lang = "uz"

        await message.answer("O'zbek tili tanlandi. Xush kelibsiz! 👋",reply_markup=get_main_menu_kb("uz"))