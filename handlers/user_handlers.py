import asyncio
import aiohttp
from random import choices
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.formatting import Bold, as_list, as_section
from aiogram import F
from aiogram.filters import CommandStart
from keyboards.inline import get_callback_btns
from keyboards.reply import get_keyboard
from utils.db import get_questions

user_router = Router()


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик кнопки /start
    :param message:
    :return:
    """
    await message.answer(
        "Привет 🤗! Рад тебя видетья)\n"
        "Предлагаю тебе пройти викторину \"Какое животное тебя характеризует\"\n"
        "А потом я тебе кое-что расскажу😉."
        "Жду тебя на финише!",
        reply_markup=get_keyboard(
            "Начать викторину 🦁",
            "В другой раз 🐥",
            placeholder="Что вас интересует?",
            sizes=(2, 2)
        ),
    )


@user_router.message(F.text.lower().contains("начать викторину"))
async def commands(message: types.Message, state: FSMContext, session: AsyncSession):
    questions = await get_questions(session)
    selected_questions = choices(questions, k=7)
    await state.set_data({'questions': selected_questions})
    q = selected_questions[0]

    response = as_list(
        as_section(Bold(f"1/({selected_questions.__len__()}) \"{q['question']}\"")),
        as_section('1. Солнце'),
        as_section('2. Луна'),
        as_section('3. Юпитер'))

    await message.answer(**response.as_kwargs(),
                         reply_markup=get_callback_btns(btns={
                             'Следующий ▶': 'question_1'
                         }))


@user_router.callback_query(F.data.startswith('question_'))
async def counter(callback: types.CallbackQuery, state: FSMContext):
    number = int(callback.data.split('_')[-1])

    response = as_list(
        as_section(Bold(f"{number}/9 \"Звезда, которая дает тепло\"")),
        as_section('1. Солнце'),
        as_section('2. Луна'),
        as_section('3. Юпитер'))

    await callback.message.edit_text(
        text=response.as_markdown(),
        reply_markup=get_callback_btns(btns={
            'Следующий ▶': f'question_{number + 1}'
        }))
