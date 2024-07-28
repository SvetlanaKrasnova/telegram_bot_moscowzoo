import os
import logging
from aiogram.types import Message
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import CommandStart
from keyboards.inline import MenuCallBack
from handlers.processing import plus_points, show_result, get_get_main_menu, questions_page, program, contacts
from database.orm_requests import *

user_router = Router()


class Menu(StatesGroup):
    get_feedback = State()  # Получить вопрос, который нужно добавить


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик кнопки /start
    :param message:
    :return:
    """
    text, reply_markup, image = await get_get_main_menu(message.from_user.full_name)
    if image:
        await message.answer_photo(image, caption=text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)

@user_router.callback_query(MenuCallBack.filter(F.menu_name == "restart"))
async def restart_page(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Перезапуск бота вернуться в начало
    :param message:
    :return:
    """
    await state.clear()
    text, reply_markup, image = await get_get_main_menu(callback.message.from_user.full_name)
    await callback.message.delete()
    if image:
        await callback.message.answer_photo(image, caption=text, reply_markup=reply_markup)
    else:
        await callback.message.answer(text, reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "quiz"))
async def quiz_page(callback: types.CallbackQuery,
                    callback_data: MenuCallBack,
                    session: AsyncSession,
                    state: FSMContext):
    """
    Обработчик викторины. Тут будем пока не закончатся вопросы по викторине
    :param callback:
    :param callback_data:
    :param session:
    :param state:
    :return:
    """
    # Начисляем баллы животным (предыдущего шага)
    await plus_points(session=session,
                      state=state,
                      user_select=callback_data.user_select,
                      question_id=callback_data.question_id)

    text, reply_markup = await questions_page(session=session,
                                              question_id=callback_data.question_id,
                                              state=state)
    if callback_data.question_id == 0:
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "show_result"))
async def show_result_page(callback: types.CallbackQuery, state: FSMContext):
    """
    Отображает результат викторины
    :param callback:
    :param callback_data:
    :param session:
    :param state:
    :return:
    """
    text, reply_markup, image = await show_result(state=state)
    if image:
        await callback.message.delete()
        await callback.message.answer_photo(image, caption=text, reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "program"))
async def about_program_page(callback: types.CallbackQuery):
    """
    Показывает информацию о программе опеки
    :param message:
    :param state:
    :return:
    """
    text, reply_markup = await program()

    await callback.message.delete()
    await callback.message.answer(**text.as_kwargs(), reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "feedback"))
async def feedback_page(message: Message, state: FSMContext):
    """
    Предлагает пользователю ввести комментарий (отзыв)
    :param message:
    :param state:
    :return:
    """
    await message.answer('Пожалуйста, напишите ваши впечатления в текстовом поле 😊:')
    await state.set_state(Menu.get_feedback.state)


@user_router.message(Menu.get_feedback)
async def write_feedback(message: Message, state: FSMContext, session: AsyncSession):
    """
    Записывает отзыв в базу данных
    :param message:
    :param state:
    :return:
    """
    await insert_one(session=session,
                     data=ReviewORM(user=message.from_user.full_name,
                                    review=str(message.text.strip())))
    await message.answer('Спасибо! Ваш отзыв сохранен 🙂')
    await state.clear()


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "manager_contact"))
async def contact_page(callback: types.CallbackQuery):
    """
    Связаться с сотрудником для получения подробной информации
    :param message:
    :param state:
    :return:
    """
    text, reply_markup = await contacts()
    try:
        if os.getenv('MANAGER_TELEGRAM_ID'):
            await callback.message.copy_to(chat_id=int(os.getenv('MANAGER_TELEGRAM_ID')))
    except Exception as e:
        logging.exception(e)
        logging.warning('Не удалось переслать сообщение менеджеру')

    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery):
    """
    Что-то непонятное (введенный текст, картинка...)
    :param callback:
    :param callback_data:
    :param session:
    :return:
    """
    await callback.message.answer(text='Не могу понять, что ты хочешь сделать :( '
                                       'Пожалуйста, пользуйс только кнопками и инструкциями, которые'
                                       'я тебе предлагая.')
