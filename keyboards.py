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


def get_summary_text(category, lang,quantity=None, product=None, distance=None, cart=None):
    config = CATEGORIES_CONFIG.get(category, CATEGORIES_CONFIG["beton"])
    tovar_name = config[f"tovar_{lang}"]
    unit = config[f"unit_{lang}"]
    label = config[f"label_{lang}"]
    emoji = config["emoji"]

    # --- ЛОГИКА ДЛЯ ПЛИТ (КОРЗИНА) ---
    if category == "plita" and cart:
        if lang == "ru":
            lines = [
                f"📝 **Ваш заказ (Плиты):**",
                f"━━━━━━━━━━━━━━"
            ]
            for i, item in enumerate(cart, 1):
                lines.append(f"{i}. {item['product']} — {item['quantity']} {unit} ({item['distance']} м)")

            lines.append(f"━━━━━━━━━━━━━━")
            summary = "\n".join(lines)
            choose_text = "Выберите действие:"
        else:
            lines = [
                f"📝 **Sizning buyurtmangiz (Plitalar):**",
                f"━━━━━━━━━━━━━━"
            ]
            for i, item in enumerate(cart, 1):
                lines.append(f"{i}. {item['product']} — {item['quantity']} {unit} ({item['distance']} m)")

            lines.append(f"━━━━━━━━━━━━━━")
            summary = "\n".join(lines)
            choose_text = "Harakatni tanlang:"

        return summary, choose_text

    # --- ЛОГИКА ДЛЯ ОСТАЛЬНЫХ (БЕТОН, ФБС, ЛОТКИ) ---
    # (Твой оригинальный код здесь без изменений)
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
    category,
    lang,
    quantity,
    product=None,
    dist=None,
    cart=None,
    phone=None,
    name=None,
    date=None,
    is_manager=False
):

    config = CATEGORIES_CONFIG.get(category, CATEGORIES_CONFIG["beton"])
    tovar_name = config[f"tovar_{lang}"]
    emoji = config["emoji"]
    label = config[f"label_{lang}"]
    price_dict = config.get("price_dict", {})

    # форматирование чисел
    def fmt(val):
        return f"{int(val):,}".replace(",", " ")

    # =========================
    # ПЛИТЫ
    # =========================
    if category == "plita":

        total_sum = 0
        items_lines = []

        for item in cart:
            p_name = item["product"]
            p_qty = int(item["quantity"])
            p_dist = item["distance"]

            p_price = calculate_price_plita(p_name, p_dist)

            subtotal = p_price * p_qty
            total_sum += subtotal

            items_lines.append(
                f"🔹 {p_name} ({p_dist} м)\n"
                f"   {p_qty} шт. x {fmt(p_price)} = {fmt(subtotal)} сум"
            )

        items_text = "\n".join(items_lines)
        p_tot_formatted = fmt(total_sum)

        result_text = (
            f"📊 <b>{'Итоговый расчет' if lang == 'ru' else 'Yakuniy hisob'} (Плиты):</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{items_text}\n"
            f"━━━━━━━━━━━━━━\n"
            f"✨ <b>{'ИТОГО' if lang == 'ru' else 'JAMI'}: {p_tot_formatted} {'сум' if lang == 'ru' else 'so`m'}</b>"
        )

    # =========================
    # БЕТОН / FBS / ЛОТОК
    # =========================
    else:

        if category == "lotok":
            price_material = price_dict
        else:
            price_material = price_dict.get(product, 0)

        current_delivery = 0

        if category == "beton" and dist is not None:
            if dist <= distance_from:
                current_delivery = price_beton
            else:
                current_delivery = price_beton + (
                    (dist - distance_from) * price_distance
                )

        total_sum = quantity * (price_material + current_delivery)

        p_mat_formatted = fmt(price_material)
        p_del_formatted = fmt(current_delivery)
        p_tot_formatted = fmt(total_sum)

        res_header = "Итоговый расчет" if lang == "ru" else "Yakuniy hisob"

        dist_line = (
            f"📍 <b>{'Дистанция' if lang == 'ru' else 'Masofa'}:</b> {dist} км\n"
            if category == "beton"
            else ""
        )

        del_line = (
            f"🚛 <b>{'Доставка' if lang == 'ru' else 'Yetkazish'}:</b> {p_del_formatted} сум\n"
            if category == "beton"
            else ""
        )

        result_text = (
            f"📊 <b>{res_header}:</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{emoji} <b>{'Категория' if lang == 'ru' else 'Kategoriya'}:</b> {tovar_name}\n"
            f"🏗 <b>{label}:</b> {product}\n"
            f"🔢 <b>{'Количество' if lang == 'ru' else 'Miqdor'}:</b> {quantity_or_unit(lang, category, quantity)}\n"
            f"{dist_line}"
            f"━━━━━━━━━━━━━━\n"
            f"💵 <b>{'Цена' if lang == 'ru' else 'Narx'}:</b> {p_mat_formatted} сум\n"
            f"{del_line}"
            f"✨ <b>{'ИТОГО' if lang == 'ru' else 'JAMI'}: {p_tot_formatted} сум</b>"
        )

    # =========================
    # ДОБАВЛЯЕМ ДАННЫЕ КЛИЕНТА (RU / UZ)
    # =========================

    extra_lines = []

    if name:
        extra_lines.append(
            f"👤 <b>{'Заказчик' if lang == 'ru' else 'Buyurtmachi'}:</b> {name}"
        )

    if phone:
        extra_lines.append(
            f"📞 <b>{'Тел' if lang == 'ru' else 'Telefon'}:</b> {phone}"
        )

    if date:
        extra_lines.append(
            f"🚛 <b>{'Дата Отгрузки' if lang == 'ru' else 'Yuklash sanasi'}:</b> {date}"
        )

    if extra_lines:
        result_text += "\n\n" + "\n".join(extra_lines)

    # =========================
    # СООБЩЕНИЕ МЕНЕДЖЕРУ
    # =========================

    if is_manager:

        header = (
            f"🚀 <b>НОВЫЙ ЗАКАЗ!</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 <b>Заказчик:</b> {name}\n"
            f"📞 <b>Тел:</b> {phone}\n\n"
            f"🏗 <b>Категория:</b> {tovar_name}\n"
        )

        footer = (
            f"\n━━━━━━━━━━━━━━\n"
            f"✨ <b>ИТОГО К ОПЛАТЕ: {p_tot_formatted} сум</b>\n\n"
            f"🚛 <b>Дата Отгрузки:</b> {date}"
        )

        if category == "plita":
            result_text = f"{header}{items_text}{footer}"
        else:

            body = (
                f"🔹 <b>{product}:</b>\n"
                f"   {quantity} шт. x {p_mat_formatted} = {p_tot_formatted} сум\n"
            )

            if category == "beton":
                body += f"🚛 Доставка ({dist} км): {p_del_formatted} сум\n"

            result_text = f"{header}{body}{footer}"

    return result_text

def plita_loop(lang):
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


