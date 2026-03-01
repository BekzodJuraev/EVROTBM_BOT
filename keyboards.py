from aiogram import Bot, Dispatcher, types,F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from price_list import *

from aiogram.filters import BaseFilter

# class NotBackButton(BaseFilter):
#     async def __call__(self, message: types.Message) -> bool:
#         # Возвращает True, если текста НЕТ в списке кнопок "Назад"
#         return message.text not in ["⬅️ Назад", "⬅️ Orqaga"]
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


def get_summary_text(category, quantity, lang, product=None, distance=None):
    config = CATEGORIES_CONFIG.get(category, CATEGORIES_CONFIG["beton"])

    tovar_name = config[f"tovar_{lang}"]
    unit = config[f"unit_{lang}"]
    label = config[f"label_{lang}"]
    emoji = config["emoji"]

    # Собираем начало сообщения
    if lang == "ru":
        lines = [
            f"📝 **Ваш выбор:**",
            f"━━━━━━━━━━━━━━",
            f"{emoji} **Товар:** {tovar_name}",
            f"🏗 **{label}:** `{product}`",
            f"🔢 **Количество:** `{quantity} {unit}`"
        ]
        if config["has_distance"]:
            lines.append(f"🚚 **Дистанция:** `{distance} км` ")

        if category == "lotok":
            lines.remove(f"🏗 **{label}:** `{product}`")

        lines.append(f"━━━━━━━━━━━━━━")
        summary = "\n".join(lines)
        choose_text = "Выберите действие:"

    else:
        lines = [
            f"📝 **Sizning tanlovingiz:**",
            f"━━━━━━━━━━━━━━",
            f"{emoji} **Mahsulot:** {tovar_name}",
            f"🏗 **{label}:** `{product}`",
            f"🔢 **Miqdori:** `{quantity} {unit}`"
        ]
        if config["has_distance"]:
            lines.append(f"🚚 **Masofa:** `{distance} km` ")

        if category == "lotok":
            lines.remove(f"🏗 **{label}:** `{product}`")

        lines.append(f"━━━━━━━━━━━━━━")
        summary = "\n".join(lines)
        choose_text = "Harakatni tanlang:"

    return summary, choose_text


def making_order_beton(lang,message):
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



