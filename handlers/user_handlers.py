from random import choices
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.formatting import Bold, as_list, as_section
from aiogram import F
from aiogram.filters import CommandStart
from keyboards.inline import get_callback_btns, MenuCallBack
from database.orm_requests import get_questions
from handlers.processing import get_menu_content

user_router = Router()


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик кнопки /start
    :param message:
    :return:
    """
    text, reply_markup = await get_menu_content(level=0, menu_name="main")
    await message.answer(text,
                         reply_markup=reply_markup,
                         placeholder="Что вас интересует?")

@user_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    """
    Обработчик викторины
    :param callback:
    :param callback_data: данный
    :param session:
    :return:
    """
    # TODO Начисляем баллы животным (предыдущего шага)

    text, reply_markup = await get_menu_content(
        session=session,
        page=callback_data.page,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        question_id=callback_data.question_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()
