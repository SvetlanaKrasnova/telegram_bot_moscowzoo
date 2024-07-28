from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import F, Bot
from aiogram import Router, types
from database.orm_requests import *

admin_router = Router()


class Requests(StatesGroup):
    delete_question = State()  # Удаляем вопрос из базы
    get_name_question = State()  # Получить вопрос, который нужно добавить
    get_answer_question = State()
    add_question = State()


@admin_router.message(Command("admin"))
async def recipes(message: Message, bot: Bot):
    """
    Обработчик команды /admin
    :param message:
    :param command:
    :param state:
    :return:
    """
    if not str(message.chat.id) in bot.admin_user:
        return

    # И выводим его пользователю в виде кнопок
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Получить список всех вопросов'))
    builder.add(types.KeyboardButton(text='Удалить вопрос'))
    builder.add(types.KeyboardButton(text='Добавить вопрос'))
    builder.add(types.KeyboardButton(text='Показать отзывы'))
    builder.adjust(1)

    await message.answer(f"Что вы хотите сделать?", reply_markup=builder.as_markup(resize_keyboard=True))


@admin_router.message(F.text.lower() == "получить список всех вопросов")
async def description(message: types.Message, bot: Bot):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return
    await message.answer('Бот выводит список всех вопросов из БД')


@admin_router.message(F.text.lower() == "удалить вопрос")
async def description(message: types.Message, state: FSMContext, bot: Bot):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        await state.clear()
        return

    await message.answer(f'Введите вопрос, который хотите удалить:')
    await state.set_state(Requests.delete_question.state)


@admin_router.message(Requests.delete_question)
async def recipes_by_category(message: types.Message, session: AsyncSession, state: FSMContext):
    """
    Ожидаем фотографию
    :param message:
    :param state:
    :return:
    """
    await delete_question(session=session, question_name=message.text.lower().strip())
    await message.answer(f'Вопрос "{message.text}" удален из БД')
    await state.clear()


@admin_router.message(F.text.lower() == "добавить вопрос")
async def description(message: types.Message, bot: Bot, state: FSMContext):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    await message.answer('Введите наименование вопроса:')
    await state.set_state(Requests.get_name_question.state)


@admin_router.message(Requests.get_name_question)
async def recipes_by_category(message: types.Message, state: FSMContext):
    """

    :param message:
    :param session:
    :param state:
    :param bot:
    :return:
    """
    await state.set_data({'name_question': message.text})
    await message.answer('Введите варианты ответов через запятую.\n'
                         'Например:\n'
                         'Красный, Синий, Зеленый')
    await state.set_state(Requests.get_answer_question.state)


@admin_router.message(Requests.get_answer_question)
async def recipes_by_category(message: types.Message, state: FSMContext):
    """

    :param message:
    :param state:
    :param bot:
    :return:
    """
    await state.update_data({'list_answer': message.text})
    await message.answer('Введите варианты ответов через запятую. Сохраните порядок ответов '
                         'с ранее введенными вариантами ответов\n'
                         'Пример:\n'
                         '["Енот", "Мохноногий сыч"], ["Песец", "Питон тигровый"], ["Песец", "Фенек"]')
    await state.set_state(Requests.add_question.state)


@admin_router.message(Requests.add_question)
async def recipes_by_category(message: types.Message, state: FSMContext):
    data = state.get_data()

    # TODO Парсим все значения и добавляем их в базу
    await message.answer('Вопрос добавлен в базу данных')
    await state.clear()


@admin_router.message(F.text.lower() == "показать отзывы")
async def description(message: types.Message, session: AsyncSession, bot: Bot):
    if not str(message.chat.id) in bot.admin_user:
        await message.answer('У вас нет доступа к этому разделу')
        return

    user_reviews = await get_review(session)
    text = '\n'.join([f'{review.user} - {review.review}' for review in user_reviews])
    await message.answer(f'Последние 10 отзывов:\n{text}')
