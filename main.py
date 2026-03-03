import asyncio
import logging
from aiogram import Bot, Dispatcher, types,F
from aiogram.filters.command import Command
from keyboards import *
from price_list import beton
# Включаем логирование, чтобы не пропустить важные сообщения
from aiogram.utils.keyboard import InlineKeyboardBuilder
GROUP_ID = -5146609253
logging.basicConfig(level=logging.INFO)

bot = Bot(token="8629839438:AAEX-m2gvZTdOhJCvZ8lrgGNaC7HrnIfFIM")
# Диспетчер
dp = Dispatcher()
dp.message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State



class OrderSteps(StatesGroup):
    choosing_language = State()
    main_menu = State()
    main_category=State()
    making_order = State()
    entering_distance=State()
    quantity_order=State()
    choosing_plita_width=State()

@dp.message(F.text.in_({"⬅️ Назад", "⬅️ Orqaga"}))
async def go_back(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")



    if current_state == OrderSteps.main_menu:
        await state.set_state(OrderSteps.choosing_language)
        await message.answer("Выберите язык / Tilni tanlang", reply_markup=get_lang_kb())


    elif current_state == OrderSteps.main_category:
        await state.set_state(OrderSteps.main_menu)



        await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...", reply_markup=get_main_menu_kb(lang))

    elif current_state == OrderSteps.making_order:
        if category == "lotok":
            await state.set_state(OrderSteps.main_menu)
            await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...",
                                 reply_markup=get_main_menu_kb(lang))

        else:
            await state.set_state(OrderSteps.main_category)
            await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...",
                                 reply_markup=get_cat_menu(lang))



# Обработка кнопки "Выполнено"
@dp.callback_query(F.data.startswith("order_done_"))
async def admin_done(callback: types.CallbackQuery):
    # Достаем ID пользователя из callback_data
    user_id = int(callback.data.split("_")[2])

    # 1. Обновляем текст в группе
    new_text = callback.message.text + f"\n\n✅ **ВЫПОЛНЕНО**\n(Кем: {callback.from_user.first_name})"
    await callback.message.edit_text(new_text)

    # 2. Отправляем сообщение пользователю
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="🎉 **Ваш заказ выполнен!** Благодарим за сотрудничество."
        )
    except Exception:
        await callback.answer("Не удалось отправить уведомление юзеру (бот заблокирован)", show_alert=True)

    await callback.answer("Заказ завершен")


# Обработка кнопки "Отмена"
@dp.callback_query(F.data.startswith("order_cancel_"))
async def admin_cancel(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[2])

    # 1. Обновляем текст в группе
    new_text = callback.message.text + f"\n\n❌ **ОТМЕНЕНО АДМИНОМ**"
    await callback.message.edit_text(new_text)

    # 2. Отправляем сообщение пользователю
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="❌ **Ваш заказ был отменен администратором.**"
        )
    except Exception:
        pass

    await callback.answer("Заказ отменен")


@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")

    # Извлекаем все данные из состояния
    category = data.get("product")  # Категория (бетон/fbs)
    product = data.get("selected_product")
    dist = data.get("distance", 0)
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")


    result_text=calculate_total(category=category,lang=lang,product=product,dist=dist,quantity=quantity,cart=cart,is_manager=True)
    try:
        await callback.bot.send_message(
            chat_id=GROUP_ID,
            text=result_text,
            reply_markup=get_admin_order_keyboard(user_id=callback.from_user.id),
            parse_mode="Markdown"
        )

        # Ответ пользователю в боте
        msg = "✅ Заявка отправлена! Менеджер свяжется с вами." if lang == "ru" else "✅ Arizangiz yuborildi! Menajer bog'lanadi."
        await callback.message.edit_text(msg)

        # Очищаем данные после успешной отправки


    except Exception as e:
        await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)

    await callback.answer()


# Хендлер ОТМЕНИТЬ
@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем данные
    await callback.message.delete()  # Удаляем всё сообщение с расчетом
    await callback.answer("Отменено / Bekor qilindi")

@dp.callback_query(F.data == "calculate_total")
async def final_calculation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")
    category = data.get("product")
    product = data.get("selected_product")
    dist = int(data.get("distance", 0))
    quantity=int(data.get("quantity",0))
    cart = data.get("cart")


    result_text=calculate_total(category=category,lang=lang,product=product,dist=dist,quantity=quantity,cart=cart)




    await callback.message.edit_text(result_text, reply_markup=get_final_order_keyboard(lang))
    await callback.answer()
    #await state.update_data(cart=[])


@dp.message(OrderSteps.entering_distance)
async def process_distance_manual(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")

    await message.delete()

    try:
        # Заменяем запятую на точку, чтобы принимало 3.9 или 3,9
        value = float(message.text.strip().replace(",", "."))
    except ValueError:
        error_text = "Введите число!" if lang == "ru" else "Raqam kiriting!"
        await message.answer(error_text)
        return

    # Логика проверки в зависимости от категории
    if category == "plita":
        # Проверка длины плиты (например, от 1.9 до 9.0 метров)
        if 1.9 <= value <= 9.0:
            await state.update_data(distance=value)  # сохраняем в то же поле для удобства
            await state.set_state(OrderSteps.quantity_order)
            await message.answer(get_quantity_text(lang))
        else:
            limit_text = "Длина плиты должна быть от 1.9 до 9.0 м!" if lang == "ru" else "Plita uzunligi 1.9 dan 9.0 m gacha bo'lishi kerak!"
            await message.answer(limit_text)

    else:
        # Логика для БЕТОНА (дистанция)
        if 1 <= value <= 70:
            await state.update_data(distance=int(value))
            await state.set_state(OrderSteps.quantity_order)
            await message.answer(get_quantity_text(lang))
        else:
            limit_text = "Доставка только от 1 до 70 км!" if lang == "ru" else "Yetkazib berish faqat 1 dan 70 km gacha!"
            await message.answer(limit_text)


@dp.message(OrderSteps.choosing_plita_width)
async def handle_cart_options(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    choice = message.text
    category = user_data.get("product")
    distance=user_data.get("distance")

    # 1. Если пользователь хочет добавить еще одну плиту
    if choice in ["➕ Добавить еще", "➕ Yana qo'shish"]:

        await state.update_data(selected_product=None, plita_width=None)


        text = "🏗 **Выберите ширину для следующей плиты:**" if lang == "ru" else "🏗 **Keyingi plita kengligini tanlang:**"
        await message.answer(text, reply_markup=get_plita_width_kb(lang))




    elif choice in ["✅ Далее", "✅ Davom etish"]:
        cart = user_data.get("cart", [])

        if not cart:
            await message.answer("Ваша корзина пуста!" if lang == "ru" else "Savat bo'sh!")
            return







        summary, text_info = get_summary_text(category=category,lang=lang,cart=cart,distance=distance)
        await message.answer(summary, reply_markup=get_calculate_inline(lang))
        await message.answer(text_info, reply_markup=back_menu(category, lang))



    await state.set_state(OrderSteps.making_order)






@dp.message(OrderSteps.quantity_order)
async def process_quantity_order(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")
    product = user_data.get("selected_product")
    distance = user_data.get("distance", 0)

    await message.delete()

    # 1. Проверка числа
    try:
        quantity = int(message.text.strip())
        await state.update_data(quantity=quantity)
    except ValueError:
        error_text = "Введите число!" if lang == "ru" else "Raqam kiriting!"
        await message.answer(error_text)
        return

    # 2. Получаем текущую корзину или создаем новую, если её нет






    if category == "plita":
        cart = user_data.get("cart", [])
        await state.update_data(cart=cart)


        cart.append({
            "product": product,
            "quantity": quantity,
            "distance":distance
        })




        text, keyboard=plita_loop(lang)
        await message.answer(text, reply_markup=keyboard)

        await state.set_state(OrderSteps.choosing_plita_width)

    else:
        # Для бетона или ФБС оставляем как было (сразу к итогу)
        summary, text_info = get_summary_text(category=category, quantity=quantity, lang=lang, product=product,
                                              distance=distance)
        await message.answer(summary, reply_markup=get_calculate_inline(lang))
        await message.answer(text_info, reply_markup=back_menu(category, lang))
        await state.set_state(OrderSteps.making_order)






@dp.message(OrderSteps.making_order)
async def process_beton_mark(message: types.Message, state: FSMContext):
    await state.update_data(selected_product=message.text)

    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")

    # Get configuration for this category
    config = CATEGORIES_CONFIG.get(category)

    # DRY LOGIC: Check if this category needs distance
    if config.get("has_distance"):
        await state.set_state(OrderSteps.entering_distance)
        text = making_order_text(lang, category,message.text)  # Specific text for distance
    else:
        # For FBS, Lotok, and anything else without distance
        await state.set_state(OrderSteps.quantity_order)
        text = get_quantity_text(lang)  # Generic "Enter quantity" text

    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message(OrderSteps.main_category)
async def set_product_category(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")


    choice = message.text



    if "Бетон" in choice or "Beton" in choice:
        await state.update_data(product="beton")
        await state.set_state(OrderSteps.making_order)

        text = "🏗 **Выберите марку бетона:**" if lang == "ru" else "🏗 **Beton markasini tanlang:**"
        kb = get_beton_keyboard(lang)


    elif "ФБС" in choice or "FBS" in choice:
        await state.update_data(product="fbs")
        await state.set_state(OrderSteps.making_order)

        text = "🧱 **Выберите тип ФБС блока:**" if lang == "ru" else "🧱 **FBS blok turini tanlang:**"
        kb = get_fbs_keyboard(lang)



    elif "Лотки" in choice or "Lotoklar" in choice:
        await state.update_data(product="lotok")
        await state.set_state(OrderSteps.quantity_order)
        text = get_quantity_text(lang)
        kb=None


    elif "Плиты перекрытия" in choice or "Plitalar" in choice:
        await state.update_data(product="plita")
        text = "🏗 **Выберите ширину плиты:**" if lang == "ru" else "🏗 **Plita kengligini tanlang:**"
        await state.set_state(OrderSteps.making_order)
        kb = get_plita_width_kb(lang)





    else:
        error_text = "Пожалуйста, выберите категорию из меню 👇" if lang == "ru" else "Iltimos, menyudan tanlang 👇"
        await message.answer(error_text)
        return


    #await message.delete()


    await message.answer(text, reply_markup=kb)






@dp.message(F.text.contains("Заказать") | F.text.contains("Buyurtma berish"))
async def set_categories(message: types.Message, state: FSMContext):

    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")


    await state.set_state(OrderSteps.main_category)


    if lang == "ru":
        await message.answer("Выберите тип продукции: 🏗", reply_markup=get_cat_menu(lang))
    else:
        await message.answer("Mahsulot turini tanlang: 🏗", reply_markup=get_cat_menu(lang))


@dp.message(OrderSteps.choosing_language)
async def set_language(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang")


    #await choosing_language(message)
    if "Русский" in message.text:
        lang = "ru"
        await message.answer("Установлен русский язык. Добро пожаловать! 👋",reply_markup=get_main_menu_kb(lang))
    else:
        lang = "uz"

        await message.answer("O'zbek tili tanlandi. Xush kelibsiz! 👋",reply_markup=get_main_menu_kb(lang))

    await state.set_state(OrderSteps.main_menu)
    await state.update_data(user_lang=lang)




@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = (
        "<b>🦾 Главное меню команд:</b>\n\n"
        "🚀 /start — Запустить бота и обновить данные\n"
        "✅ /готово — Отметить продукцию как выполненную\n"
        "📋 /список — Посмотреть актуальный список заказов\n"
        "🆘 /помощь — Вызвать эту инструкцию\n\n"
        "<i>Просто выберите нужную команду или введите её вручную.</i>"
    )

    await message.answer(help_text, parse_mode="HTML")




    # elif current_state == OrderSteps.quantity_order:
    #     await state.set_state(OrderSteps.main_category)
    #     await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...",
    #                          reply_markup=get_cat_menu(lang))

    #elif current_state == OrderSteps.





@dp.message(Command("start"))
async def cmd_start(message: types.Message,state: FSMContext):
    await message.answer("<b>Выберите язык / Tilni tanlang</b> 🌍", reply_markup=get_lang_kb(), parse_mode="HTML")
    await state.set_state(OrderSteps.choosing_language)

@dp.message(Command("готово"))
async def cmd_start(message: types.Message):
    await message.answer("готово!")

@dp.message(Command("список"))
async def cmd_start(message: types.Message):
    await message.answer("список")

@dp.message(Command("помощь"))
async def cmd_start(message: types.Message):
    await message.answer("помощь")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())