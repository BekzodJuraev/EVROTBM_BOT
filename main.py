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

@dp.message(F.text.in_({"⬅️ Назад", "⬅️ Orqaga"}))
async def go_back(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")


    if current_state == OrderSteps.main_menu:
        await state.set_state(OrderSteps.choosing_language)
        await message.answer("Выберите язык / Tilni tanlang", reply_markup=get_lang_kb())


    elif current_state == OrderSteps.main_category:
        await state.set_state(OrderSteps.main_menu)



        await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...", reply_markup=get_main_menu_kb(lang))

    elif current_state == OrderSteps.making_order:

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
    dist = int(data.get("distance", 0))
    quantity = int(data.get("quantity", 0))

    # 1. Считаем цену за единицу товара
    if category == "fbs":
        price_material = fbs_prices.get(product, 0)
        cat_emoji = "🧱"
        prod_label = "Тип блока" if lang == "ru" else "Blok turi"
    else:
        price_material = beton.get(product, 0)
        cat_emoji = "💧"
        prod_label = "Марка" if lang == "ru" else "Markasi"

    # 2. Логика расчета доставки (твои переменные)
    if dist <= distance_from:
        current_delivery = price_beton
    else:
        extra_km = dist - distance_from
        current_delivery = price_beton + (extra_km * price_distance)

    # Итоговая сумма: (Цена товара + Доставка) * Количество
    total_sum = quantity * (price_material + current_delivery)
    p_tot_formatted = f"{total_sum:,}".replace(",", " ")

    # Получаем красиво отформатированное количество (вызываем твою функцию)
    q_unit = quantity_or_unit(lang, category, quantity)

    # --- ТЕКСТ ДЛЯ ГРУППЫ (Точно как у пользователя) ---
    report = (
        f"🚀 **НОВЫЙ ЗАКАЗ!**\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 **Клиент:** {callback.from_user.full_name} (@{callback.from_user.username})\n"
        f"{cat_emoji} **Категория:** {category.upper()}\n"
        f"🏗 **{prod_label}:** {product}\n"
        f"🔢 **Количество:** {q_unit}\n"
        f"📍 **Дистанция:** {dist} км\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 **ИТОГО К ОПЛАТЕ: {p_tot_formatted} сум**\n"
        f"━━━━━━━━━━━━━━"
    )

    # Отправка в группу менеджерам
    try:
        await callback.bot.send_message(
            chat_id=GROUP_ID,
            text=report,
            reply_markup=get_admin_order_keyboard(user_id=callback.from_user.id),
            parse_mode="Markdown"
        )

        # Ответ пользователю в боте
        msg = "✅ Заявка отправлена! Менеджер свяжется с вами." if lang == "ru" else "✅ Arizangiz yuborildi! Menajer bog'lanadi."
        await callback.message.edit_text(msg)

        # Очищаем данные после успешной отправки
        await state.clear()

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

    result_text=calculate_total(category=category,lang=lang,product=product,dist=dist,quantity=quantity)

    await callback.message.edit_text(result_text, reply_markup=get_final_order_keyboard(lang))
    await callback.answer()

@dp.message(OrderSteps.entering_distance)
async def process_distance_manual(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    await message.delete()


    try:
        distance = int(message.text.strip())
    except ValueError:
        error_text = "Введите число (1-70)!" if lang == "ru" else "Raqam kiriting (1-70)!"
        await message.answer(error_text)
        return

    if 1 <= distance <= 70:
        await state.update_data(distance=distance)
        await state.set_state(OrderSteps.quantity_order)
        text = get_quantity_text(lang)
        sent_msg = await message.answer(text)



    else:
        limit_text = "Доставка только от 1 до 70 км!" if lang == "ru" else "Yetkazib berish faqat 1 dan 70 km gacha!"
        await message.answer(limit_text)


@dp.message(OrderSteps.quantity_order)
async def process_quantity_order(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")
    product = user_data.get("selected_product")
    distance = int(user_data.get("distance", 0))
    await message.delete()



    try:
        quantity = int(message.text.strip())
    except ValueError:
        error_text = "Введите число !" if lang == "ru" else "Raqam kiriting !"
        await message.answer(error_text)
        return

    await state.update_data(quantity=quantity)

    summary, text=get_summary_text(category=category,quantity=quantity,lang=lang,product=product,distance=distance)

    await message.answer(summary, reply_markup=get_calculate_inline(lang))


    await message.answer(text, reply_markup=back_menu(category,lang))


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
        text = making_order_beton(lang, message.text)  # Specific text for distance
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
    lang = user_data.get("user_lang", "ru")


    await choosing_language(message)

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