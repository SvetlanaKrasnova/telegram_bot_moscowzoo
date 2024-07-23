from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import F
from aiogram import Router, types

admin_router = Router()

class Requests(StatesGroup):
    add = State()
    add_input_name_question = State()
    add_input_answer_question = State()
    delete = State()
    delete_input_name_question = State()

@admin_router.message(Command("admin"))
async def recipes(message: Message):
    """
    Обработчик команды /admin
    :param message:
    :param command:
    :param state:
    :return:
    """

    # И выводим его пользователю в виде кнопок
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Получить список всех вопросов'))
    builder.add(types.KeyboardButton(text='Удалить вопрос'))
    builder.add(types.KeyboardButton(text='Добавить вопрос'))
    builder.adjust(1)

    await message.answer(f"Что вы хотите сделать?", reply_markup=builder.as_markup(resize_keyboard=True))

@admin_router.message(F.text.lower() == "Получить список всех вопросов")
async def description(message: types.Message):

    await message.answer('Бот выводит список всех вопросов из БД')

@admin_router.message(F.text.lower() == "удалить вопрос")
async def description(message: types.Message):
    number = 0
    await message.answer(f'Вопрос "{number}" удален из БД')

@admin_router.message(F.text.lower() == "добавить вопрос")
async def description(message: types.Message):

    await message.answer('Вопрос добавлен в БД')