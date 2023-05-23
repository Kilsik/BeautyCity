from contextlib import suppress

from aiogram.dispatcher.filters.state import StatesGroup, State

from bot.keyboard.inline_keyboard import *
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from bot.text.start_text import START_TEXT

callback_keyboard = CallbackData("procedures", "action", "value")
USERS_DATA = {}
today_month = datetime.datetime.today().month


class PersonalData(StatesGroup):
    waiting_for_get_name = State()
    waiting_for_get_phone = State()


async def update_text_fab(message: types.Message, answer_text, get_keyboard):
    with suppress(MessageNotModified):
        await message.edit_text(answer_text,
                                reply_markup=get_keyboard(callback_keyboard))


async def callbacks_change_procedures(call: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    action = callback_data["action"]
    if action == "make_up":
        USERS_DATA[action] = "Мейкап"
        await update_text_fab(call.message,
                              '💄 Процедура "Мейкап" стоит от 900 Руб.', get_keyboard_sign_up)
    elif action == "hair_coloring":
        USERS_DATA[action] = "Покраска волос"
        await update_text_fab(call.message,
                              '🧑🏻‍🎤 Процедура "Покраска волос" стоит от 1200 Руб.', get_keyboard_sign_up)
    elif action == "manicure":
        USERS_DATA[action] = "Маникюр"
        await update_text_fab(call.message,
                              '💅🏼 Процедура "Маникюр" стоит от 1000 Руб.', get_keyboard_sign_up)
    elif action == "back":
        await update_text_fab(call.message, START_TEXT['start_text'], get_keyboard_fab_for_start)
    await call.answer()


async def callbacks_change_date_time(
        call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    action = callback_data["action"]
    if action == "select_date":
        await update_text_fab(call.message,
                              '📅 Выберете удобный для вас день:', get_keyboard_select_date)
    elif action == "back_to_select_procedures":
        await update_text_fab(call.message, "Выберете процедуру:", get_keyboard_select_procedures)

    elif action == "make_an_appointment":
        change_date = callback_data["value"]
        USERS_DATA['date'] = f"{change_date}.{today_month}"
        await update_text_fab(call.message,
                              '📅 Выберете удобное время:', get_keyboard_make_an_appointment)

    elif action == "back_to_select_date":
        await update_text_fab(call.message, "📅 Выберете удобный для вас день:", get_keyboard_select_date)
    elif action == "personal_data":
        change_time = callback_data["value"].split("_")
        hour = change_time[0]
        minuts = change_time[1]
        USERS_DATA['time'] = f"{hour}:{minuts}"
        print(USERS_DATA)
        text = "Для продолжения записи нам понадобятся ваше Имя и номер телефона. " \
               "Продолжая вы даете согласие на обработку персональных данных"
        await update_text_fab(call.message, text, get_keyboard_personal_data)
    elif action == "specify_name":
        text = "Введите ваше имя: "
        await update_text_fab(call.message, text, get_keyboard_change_fab_back)
        await state.set_state(PersonalData.waiting_for_get_name.state)
    await call.answer()


async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(chosen_name=message.text)

    await state.set_state(PersonalData.waiting_for_get_phone.state)
    await message.answer("Теперь введите номер телефона в формате\n79995553388 :")


async def get_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['chosen_name']
    phone = message.text
    USERS_DATA['name'] = name
    USERS_DATA['phone'] = phone
    date_of_admission = USERS_DATA['date']
    time_of_admission = USERS_DATA['time']
    await message.answer(
        f"Спасибо за запись! До встречи {date_of_admission} {time_of_admission} по адресу: ул. улица д. дом")
    await state.finish()


def register_handlers_procedures(dp: Dispatcher):
    dp.register_callback_query_handler(
        callbacks_change_procedures,
        callback_keyboard.filter(action=[
            "make_up",
            "hair_coloring",
            "manicure",
            "back",
        ]))
    dp.register_callback_query_handler(
        callbacks_change_date_time,
        callback_keyboard.filter(action=[
            "select_date",
            "make_an_appointment",
            "back_to_select_procedures",
            "back_to_select_date",
            "personal_data",
            "specify_name",
        ]))
    dp.register_message_handler(get_name, state=PersonalData.waiting_for_get_name)
    dp.register_message_handler(get_phone, state=PersonalData.waiting_for_get_phone)

