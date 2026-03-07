import asyncio
import logging
from aiogram import Bot, Dispatcher, types,F
from aiogram.filters.command import Command
from db_middleware import DbSessionMiddleware
from keyboards import *
from price_list import beton
# Включаем логирование, чтобы не пропустить важные сообщения
from aiogram.utils.keyboard import InlineKeyboardBuilder
GROUP_ID = -5146609253
#GROUP_ID=-1001994222785
ADMIN_ID=6201199089
from pydantic import ValidationError
logging.basicConfig(level=logging.INFO)
from sqlalchemy import select,insert,func,update,delete
bot = Bot(token="8629839438:AAEX-m2gvZTdOhJCvZ8lrgGNaC7HrnIfFIM")

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
from database import async_main, async_session
from db_middleware import DbSessionMiddleware
from models import User,Order,OrderStatus
from schemas import DateValidation,UserContact
from pydantic import ValidationError
dp = Dispatcher()
dp.message
async def ask_step_data(message: types.Message, state: FSMContext, step_key: str):
    # Получаем язык из state
    data = await state.get_data()
    lang = data.get("user_lang", "ru")

    # Берем текст из нашего словаря
    text = MESSAGES.get(step_key, {}).get(lang, "Error: text not found")

    # Отправляем сообщение
    sent_msg = await message.answer(text, parse_mode="HTML")

    # Сохраняем ID, чтобы удалить его в следующем хендлере
    await state.update_data(msg_to_delete=sent_msg.message_id)


from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

class OrderSteps(StatesGroup):
    choosing_language = State()
    main_menu = State()
    main_category=State()
    making_order = State()
    entering_distance=State()
    quantity_order=State()
    choosing_plita_width=State()
    choosing_name=State()
    choosing_phone_number=State()
    choosing_date_ready=State()
    choosing_nasos=State()

@dp.message(Command("list"))
async def cmd_list(message: types.Message, session: AsyncSession,state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.clear()





    result = await session.execute(select(func.count(User.id)))
    count = result.scalar()

    await message.answer(
        f"👥 Всего зарегистрировано пользователей: <b>{count}</b>",
        parse_mode="HTML"
    )
    await cmd_start(message=message, state=state, session=session)


@dp.message(Command("send"))
async def cmd_send_all(message: types.Message, session: AsyncSession,state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()


    text_to_send = message.text.replace("/send", "").strip()

    if not text_to_send:
        await message.answer("❌ Введите текст рассылки после команды. Пример: <code>/send Привет!</code>")
        return

    # 3. Берем всех юзеров из БД
    result = await session.execute(select(User.telegram_id))
    users = result.scalars().all()

    count = 0
    blocked = 0

    await message.answer(f"🚀 Рассылка началась для {len(users)} пользователей...")

    # 4. Цикл рассылки
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text_to_send)
            count += 1
            # Небольшая пауза, чтобы Telegram не забанил за спам (Flood Limit)
            await asyncio.sleep(0.05)

        except TelegramForbiddenError:
            # Юзер заблокировал бота
            blocked += 1
        except TelegramRetryAfter as e:
            # Если превысили лимит сообщений в секунду
            await asyncio.sleep(e.retry_after)
            await bot.send_message(chat_id=user_id, text=text_to_send)
            count += 1
        except Exception as e:
            print(f"Ошибка при отправке {user_id}: {e}")

    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"👤 Получили: {count}\n"
        f"🚫 Заблокировали бота: {blocked}",
        parse_mode="HTML"
    )
    await cmd_start(message=message, state=state, session=session)

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


@dp.message(OrderSteps.choosing_name)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("msg_to_delete"):
        await message.bot.delete_message(message.chat.id, data["msg_to_delete"])

    await state.update_data(customer_name=message.text)
    await ask_step_data(message, state, "ask_phone")
    await state.set_state(OrderSteps.choosing_phone_number)
    await message.delete()



@dp.message(OrderSteps.choosing_phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if data.get("msg_to_delete"):
            await message.bot.delete_message(message.chat.id, data["msg_to_delete"])
        UserContact(phone=message.text)


        await state.update_data(customer_phone=message.text)
        await ask_step_data(message, state, "ask_date")
        await state.set_state(OrderSteps.choosing_date_ready)
        await message.delete()

    except ValidationError as e:

        error_msg = e.errors()[0]['msg']
        await message.answer(f"❌ Ошибка: {error_msg}\nПопробуйте еще раз в формате +998XXXXXXXXX")


@dp.message(OrderSteps.choosing_nasos)
async def process_nasos_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")
    category = data.get("product")
    product = data.get("selected_product")
    dist = int(data.get("distance", 0))
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")
    phone = data.get("customer_phone")
    name = data.get("customer_name")
    msg_id = data.get("last_msg_id")
    withoutcal = data.get("withoutcal")
    date_ready=data.get("date_ready")

    if message.text == "✅ Да":
        nasos=True
        choice_text = "Вы выбрали: <b>Да</b>" if lang == "ru" else "Siz tanladingiz: <b>Ha</b>"


    else:

        nasos = False
        choice_text = "Вы выбрали: <b>Нет</b>" if lang == "ru" else "Siz tanladingiz: <b>Yo'q</b>"

    await state.update_data(nasos=nasos)



    result_text = calculate_total(category=category, lang=lang, product=product, dist=dist, quantity=quantity,
                                  cart=cart, phone=phone, name=name, date=date_ready, withoutcal=withoutcal,nasos=nasos)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=result_text,
        parse_mode="HTML",
        reply_markup=get_final_order_keyboard_last(lang)
    )

    await message.delete()
    await message.answer(choice_text,reply_markup=get_beton_keyboard(lang),parse_mode="HTML")
    await state.set_state(OrderSteps.main_category)









@dp.message(OrderSteps.choosing_date_ready)
async def process_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")
    category = data.get("product")
    product = data.get("selected_product")
    dist = int(data.get("distance", 0))
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")
    phone=data.get("customer_phone")
    name = data.get("customer_name")
    msg_id = data.get("last_msg_id")
    withoutcal = data.get("withoutcal")
    if data.get("msg_to_delete"):
        await message.bot.delete_message(message.chat.id, data["msg_to_delete"])

    try:
        await state.update_data(date_ready=message.text)



        # valid_data = DateValidation(input_date=message.text)
        # chosen_date = valid_data.input_date
        # date=chosen_date.strftime("%d.%m.%Y")


        if category == "beton":
            await message.answer(
                MESSAGES["ask_nasos"][lang],
                reply_markup=get_yes_no_keyboard(lang),
                parse_mode="HTML"
            )
            await state.set_state(OrderSteps.choosing_nasos)



        else:

            result_text = calculate_total(category=category, lang=lang, product=product, dist=dist, quantity=quantity,
                                          cart=cart, phone=phone, name=name, date=message.text, withoutcal=withoutcal)

            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=result_text,
                parse_mode="HTML",
                reply_markup=get_final_order_keyboard_last(lang)
            )

            await message.delete()
            await state.set_state(OrderSteps.main_category)











    except ValidationError as e:
        # Берем текст ошибки из нашего валидатора
        error_text = e.errors()[0]['msg']
        await message.answer(f"❌ {error_text}")


@dp.callback_query(F.data == "confirm_order_last")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext,session:AsyncSession):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")


    category = data.get("product")
    product = data.get("selected_product")
    dist = data.get("distance", 0)
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")
    phone=data.get("customer_phone")
    name = data.get("customer_name")
    date = data.get("date_ready")
    withoutcal=data.get("withoutcal")
    nasos = data.get("nasos")







    result_text=calculate_total(category=category, lang=lang, product=product, dist=dist, quantity=quantity,
                    cart=cart, phone=phone, name=name, date=date,is_manager=True,withoutcal=withoutcal,nasos=nasos)
    try:
        x=await callback.bot.send_message(
            chat_id=GROUP_ID,
            text=result_text,
            reply_markup=get_admin_order_keyboard(user_id=callback.from_user.id),
            parse_mode="HTML"
        )


        msg = "✅ Заявка отправлена! Менеджер свяжется с вами." if lang == "ru" else "✅ Arizangiz yuborildi! Menajer bog'lanadi."
        await callback.message.edit_text(msg)

        stmt = (
            update(Order)
                .where(Order.message_id == callback.message.message_id)
                .values(status=OrderStatus.SENDING,message_id=x.message_id)
        )

        await session.execute(stmt)
        await session.commit()
        await state.clear()
        await state.set_state(OrderSteps.making_order)


    except Exception as e:
        await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)

    await callback.answer()
@dp.callback_query(F.data.startswith("order_done_"))
async def admin_done(callback: types.CallbackQuery,session:AsyncSession):
    user_id = int(callback.data.split("_")[2])
    stmt = delete(Order).where(
        Order.message_id == callback.message.message_id,
        Order.user_id == user_id
    )
    await session.execute(stmt)
    await session.commit()


    new_text = callback.message.text + f"\n\n✅ **ВЫПОЛНЕНО**\n(Кем: {callback.from_user.first_name})"
    await callback.message.edit_text(new_text)


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
async def admin_cancel(callback: types.CallbackQuery,session:AsyncSession):
    user_id = int(callback.data.split("_")[2])
    stmt = delete(Order).where(
        Order.message_id == callback.message.message_id,
        Order.user_id == user_id
    )
    await session.execute(stmt)
    await session.commit()

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
async def confirm_order(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")

    category = data.get("product")
    product = data.get("selected_product")
    dist = data.get("distance", 0)
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")



    result_text = calculate_total(
        category=category, lang=lang, product=product,
        dist=dist, quantity=quantity, cart=cart
    )
    await state.update_data(
        last_msg_id=callback.message.message_id,
    )




    await callback.message.edit_text(result_text,parse_mode="HTML")


    # stmt = (
    #     update(Order)
    #         .where(Order.message_id == callback.message.message_id)
    #         .values(order_text=result_text, status=OrderStatus.CALCULATION)
    # )


    await state.set_state(OrderSteps.choosing_name)
    await ask_step_data(callback.message, state, "ask_name")


@dp.callback_query(F.data == "confirm_order_withoutcal")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")

    category = data.get("product")
    product = data.get("selected_product")
    dist = data.get("distance", 0)
    quantity = int(data.get("quantity", 0))
    cart = data.get("cart")

    await state.update_data(withoutcal=True)
    result_text = calculate_total(
        category=category, lang=lang, product=product,
        dist=dist, quantity=quantity, cart=cart,withoutcal=True
    )


    await state.update_data(
        last_msg_id=callback.message.message_id,
    )
    await callback.message.edit_text(result_text, parse_mode="HTML")







    # stmt = (
    #     update(Order)
    #         .where(Order.message_id == callback.message.message_id)
    #         .values(order_text=result_text, status=OrderStatus.CALCULATION)
    # )


    await state.set_state(OrderSteps.choosing_name)
    await ask_step_data(callback.message, state, "ask_name")




@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    # 1. Удаляем запись из базы данных
    # Используем message_id и user_id для точности
    stmt = delete(Order).where(
        Order.message_id == callback.message.message_id,
        Order.user_id == callback.from_user.id
    )
    await session.execute(stmt)
    await session.commit()
    await state.update_data(cart=[])

    # 2. Очищаем состояние FSM
    await state.set_state(OrderSteps.making_order)

    # 3. Удаляем само сообщение в Telegram
    try:
        await callback.message.delete()
    except Exception as e:
        # На случай, если сообщение уже удалено или прошло более 48 часов
        print(f"Ошибка удаления сообщения: {e}")


    await callback.answer("Отменено / Bekor qilindi")

@dp.callback_query(F.data == "calculate_total")
async def final_calculation(callback: types.CallbackQuery, state: FSMContext,session:AsyncSession):
    data = await state.get_data()
    lang = data.get("user_lang", "ru")
    category = data.get("product")
    product = data.get("selected_product")
    dist = int(data.get("distance", 0))
    quantity=int(data.get("quantity",0))
    cart = data.get("cart")




    result_text=calculate_total(category=category,lang=lang,product=product,dist=dist,quantity=quantity,cart=cart)





    await callback.message.edit_text(result_text, reply_markup=get_final_order_keyboard(lang),parse_mode="HTML")
    current_msg_id = callback.message.message_id


    stmt = (
        update(Order)
            .where(Order.message_id == callback.message.message_id)
            .values(order_text=result_text, status=OrderStatus.CALCULATION)
    )


    await session.execute(stmt)
    await session.commit()

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
async def handle_cart_options(message: types.Message, state: FSMContext,session:AsyncSession):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    choice = message.text
    category = user_data.get("product")
    distance=user_data.get("distance")
    category = user_data.get("product")

    # 1. Если пользователь хочет добавить еще одну плиту
    if choice in ["➕ Добавить еще", "➕ Yana qo'shish"]:

        await state.update_data(selected_product=None, plita_width=None)


        text = "🏗 **Выберите ширину для следующей плиты:**" if lang == "ru" else "🏗 **Keyingi plita kengligini tanlang:**"
        if category == "plita":
            await message.answer(text, reply_markup=get_plita_width_kb(lang))
        else:
            await message.answer(text, reply_markup=get_fbs_keyboard(lang))




    elif choice in ["✅ Далее", "✅ Davom etish"]:
        cart = user_data.get("cart", [])

        if not cart:
            await message.answer("Ваша корзина пуста!" if lang == "ru" else "Savat bo'sh!")
            return







        summary, text_info = get_summary_text(category=category,lang=lang,cart=cart,distance=distance)
        sent_message = await message.answer(
            summary,
            reply_markup=get_calculate_inline(lang),
            parse_mode="HTML"


        )


        msg_id = sent_message.message_id
        new_order = Order(
            user_id=message.from_user.id,
            message_id=msg_id,
            order_text=summary,
            status=OrderStatus.PENDING
        )

        session.add(new_order)
        await session.commit()
        await message.answer(text_info, reply_markup=back_menu(category, lang))



    await state.set_state(OrderSteps.making_order)






@dp.message(OrderSteps.quantity_order)
async def process_quantity_order(message: types.Message, state: FSMContext,session:AsyncSession):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")
    product = user_data.get("selected_product")
    distance = user_data.get("distance", 0)

    await message.delete()


    try:
        quantity = int(message.text.strip())
        await state.update_data(quantity=quantity)
    except ValueError:
        error_text = "Введите число!" if lang == "ru" else "Raqam kiriting!"
        await message.answer(error_text)
        return








    if category == "plita" or category == "fbs" :
        cart = user_data.get("cart", [])
        await state.update_data(cart=cart)


        cart.append({
            "product": product,
            "quantity": quantity,
            "distance":distance
        })




        text, keyboard=plita_loop(category,lang)
        await message.answer(text, reply_markup=keyboard)

        await state.set_state(OrderSteps.choosing_plita_width)

    else:

        summary, text_info = get_summary_text(category=category, quantity=quantity, lang=lang, product=product,
                                              distance=distance)

        sent_message = await message.answer(
            summary,
            reply_markup=get_calculate_inline(lang),
            parse_mode="HTML"

        )


        msg_id = sent_message.message_id
        new_order = Order(
            user_id=message.from_user.id,
            message_id=msg_id,  # Сохраняем именно ID ответа бота
            order_text=summary,  # Тот самый текст, который над кнопкой
            status=OrderStatus.PENDING
        )

        session.add(new_order)
        await session.commit()

        await message.answer(text_info, reply_markup=back_menu(category, lang))

        if category == "lotok":
            await state.set_state(OrderSteps.main_category)

        else:
            await state.set_state(OrderSteps.making_order)









@dp.message(OrderSteps.making_order)
async def process_beton_mark(message: types.Message, state: FSMContext):
    await state.update_data(selected_product=message.text)

    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    category = user_data.get("product")


    config = CATEGORIES_CONFIG.get(category)


    try:
        if config.get("has_distance"):
            await state.set_state(OrderSteps.entering_distance)
            text = making_order_text(lang, category, message.text)  # Specific text for distance
        else:
            # For FBS, Lotok, and anything else without distance
            await state.set_state(OrderSteps.quantity_order)
            text = get_quantity_text(lang)  # Generic "Enter quantity" text

        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    except:
        await state.set_state(OrderSteps.making_order)



@dp.message(OrderSteps.main_category)
async def set_product_category(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")


    choice = message.text



    if "Товарный бетон" in choice or "Tayyor beton" in choice:
        await state.update_data(product="beton")
        await state.set_state(OrderSteps.making_order)

        text = "🏗 **Выберите марку бетона:**" if lang == "ru" else "🏗 **Beton markasini tanlang:**"
        kb = get_beton_keyboard(lang)


    elif "Фундаментальные блоки" in choice or "Bloklar" in choice:
        await state.update_data(product="fbs")
        await state.set_state(OrderSteps.making_order)

        text = "🧱 **Выберите тип ФБС блока:**" if lang == "ru" else "🧱 **FBS blok turini tanlang:**"
        kb = get_fbs_keyboard(lang)



    elif "Лотки 6м" in choice or "Lotoklar" in choice:
        await state.update_data(product="lotok")
        await state.set_state(OrderSteps.quantity_order)
        text = get_quantity_text(lang)
        kb=None


    elif "Плиты перекрытия ПБ" in choice or "Qavat plitalari" in choice:
        await state.update_data(product="plita")
        text = "🏗 **Выберите ширину плиты:**" if lang == "ru" else "🏗 **Plita kengligini tanlang:**"
        await state.set_state(OrderSteps.making_order)
        kb = get_plita_width_kb(lang)





    else:
        await message.answer(error_message(lang),reply_markup=get_cat_menu(lang))
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
    lang = user_data.get("user_lang","ru")


    #await choosing_language(message)
    if "Русский" in message.text:
        lang = "ru"
        await message.answer("Установлен русский язык. Добро пожаловать! 👋",reply_markup=get_main_menu_kb(lang))
    elif "O'zbek tili" in message.text:
        lang = "uz"
        await message.answer("O'zbek tili tanlandi. Xush kelibsiz! 👋",reply_markup=get_main_menu_kb(lang))
    else:
        await message.answer(error_message(lang),reply_markup=get_lang_kb())
        return
    await state.set_state(OrderSteps.main_menu)
    await state.update_data(user_lang=lang)


@dp.message(F.text.in_(["🧾Мои заявки", "🧾 Mening buyurtmalarim"]))
async def show_my_orders(message: types.Message, state: FSMContext, session: AsyncSession):
    # 1. Получаем заказы
    query = (
        select(Order)
            .where(
            Order.user_id == message.from_user.id,
            Order.status == OrderStatus.SENDING
        )
            .order_by(Order.created_at.desc())
            .limit(10)  # Рекомендую добавить лимит, чтобы не спамить
    )

    result = await session.execute(query)
    orders = result.scalars().all()

    # Определение языка (лучше брать из state)
    data = await state.get_data()
    lang = data.get("user_lang", "ru")

    if not orders:
        text = "📭 У вас нет активных заявок." if lang == "ru" else "📭 Sizda faol buyurtmalar yo'q."
        await message.answer(text)
        return

    # Заголовок
    header = "📋 <b>Ваши активные заявки:</b>" if lang == "ru" else "📋 <b>Sizning faol buyurtmalaringiz:</b>"
    await message.answer(header, parse_mode="HTML")

    # 2. Отправляем каждый заказ отдельным сообщением
    for i, order in enumerate(orders, 1):
        date_str = order.created_at.strftime("%d.%m.%Y %H:%M")

        # Формируем текст одного конкретного заказа
        order_info = (
            f"<b>Заказ №{i}</b> ({date_str}):\n"
            f"━━━━━━━━━━━━━━\n"
            f"{order.order_text}\n"
        )

        # Отправляем сразу. Если текст одного заказа > 4096 (вряд ли),
        # то ошибка не вылетит на общую кучу.
        try:
            await message.answer(order_info, parse_mode="HTML")
        except Exception:
            # Если даже один заказ слишком длинный, обрезаем его
            await message.answer(order_info[:4000] + "...", parse_mode="HTML")

    await state.set_state(OrderSteps.main_menu)






    # elif current_state == OrderSteps.quantity_order:
    #     await state.set_state(OrderSteps.main_category)
    #     await message.answer("Возвращаемся в меню..." if lang == "ru" else "Menyuga qaytamiz...",
    #                          reply_markup=get_cat_menu(lang))

    #elif current_state == OrderSteps.









@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):

    result = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
    user = result.scalar_one_or_none()

    if not user:

        new_user = User(
            telegram_id=message.from_user.id
        )
        session.add(new_user)
        await session.commit()

    await message.answer(
        "<b>Выберите язык / Tilni tanlang</b> 🌍",
        reply_markup=get_lang_kb(),
        parse_mode="HTML"
    )
    await state.set_state(OrderSteps.choosing_language)



async def main():

    await async_main()


    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))

    # 3. Запуск бота
    # Рекомендуется пропускать накопившиеся сообщения при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")