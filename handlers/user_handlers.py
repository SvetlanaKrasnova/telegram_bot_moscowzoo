from aiogram.types import Message
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import CommandStart
from keyboards.inline import MenuCallBack
from handlers.processing import get_menu_content, plus_points, show_result, get_get_main_menu, questions_page, program
from database.orm_requests import *

user_router = Router()


class Requests(StatesGroup):
    get_feedback = State()  # Получить вопрос, который нужно добавить


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик кнопки /start
    :param message:
    :return:
    """
    text, reply_markup, image = await get_get_main_menu(message.from_user.full_name)
    await message.answer_photo(image, caption=text, reply_markup=reply_markup)


@user_router.callback_query(MenuCallBack.filter(F.menu_name == "quiz"))
async def quiz_page(callback: types.CallbackQuery,
                    callback_data: MenuCallBack,
                    session: AsyncSession,
                    state: FSMContext):
    """
    Обработчик викторины
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
    text, reply_markup, image = await show_result(state)
    if image:
        await callback.message.delete()
        await callback.message.answer_photo(image, caption=text, reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await state.clear()

@user_router.message(MenuCallBack.filter(F.menu_name == "program"))
async def about_program(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Записывает отзыв в базу
    :param message:
    :param state:
    :return:
    """
    text, reply_markup = await program()

    await callback.message.delete()

    await callback.message.answer('Спасибо! Ваш отзыв сохранен 🙂')
    await state.clear()

@user_router.callback_query(MenuCallBack.filter(F.menu_name == "feedback"))
async def feedback_page(message: Message, state: FSMContext):
    """
    Предлагает пользователю ввести комментарий (отзыв)
    :param message:
    :param state:
    :return:
    """
    await message.answer('Пожалуйста, напишите ваши впечатления в текстовом поле 😊:')
    await state.set_state(Requests.get_feedback.state)


@user_router.message(Requests.get_feedback)
async def write_feedback(message: Message, state: FSMContext, session: AsyncSession):
    """
    Записывает отзыв в базу
    :param message:
    :param state:
    :return:
    """
    await insert_one(session=session,
                     data=ReviewORM(user=message.from_user.full_name,
                                    review=str(message.text.strip())))
    await message.answer('Спасибо! Ваш отзыв сохранен 🙂')
    await state.clear()


@user_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery,
                    callback_data: MenuCallBack,
                    session: AsyncSession,
                    state: FSMContext):
    """

    :param callback:
    :param callback_data:
    :param session:
    :return:
    """

    text, reply_markup = await get_menu_content(
        session=session,
        menu_name=callback_data.menu_name,
        question_id=callback_data.question_id,
        state=state)

    await callback.message.answer(text=text, reply_markup=reply_markup)
