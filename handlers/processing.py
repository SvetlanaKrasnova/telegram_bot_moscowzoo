import os
import json
import random
from typing import Optional
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_user_main_btns, get_user_question_btns, get_result_btns, get_program_btns
from database.orm_requests import *


async def get_get_main_menu(full_name):
    text = f"Привет, {full_name} 🤗!\nРад тебя видетья)\n" \
           "Предлагаю тебе пройти викторину \"Какое у вас тотемное животное\"\n" \
           "А потом я тебе кое-что расскажу😉.\n\n" \
           "Жду тебя на финише!❤️"

    kbds = get_user_main_btns()

    with open(os.path.join(os.getcwd(), "files/image_start.png"), "rb") as image_from_buffer:
        image = BufferedInputFile(image_from_buffer.read(),
                                  filename="image_start.png")

    return text, kbds, image


async def questions_page(session: AsyncSession, question_id, state=None):
    data = await state.get_data()
    questions_id = data.get('questions_id')

    if not questions_id:
        # Если ещё нет вопросов - значит только начали
        all_questions = await get_questions(session)

        # Теперь выбираем случайные, чтоб было интереснее (если, конечно в базе их больше, чем нужно)
        if all_questions.__len__() == int(os.getenv('COL_QUESTIONS')):
            questions = all_questions
        else:
            questions = random.sample(all_questions, int(os.getenv('COL_QUESTIONS')))

        questions_id = [q.id for q in questions]
        await state.set_data({'weights': {}, 'questions_id': questions_id})

    question = await get_question(session, questions_id[question_id])
    text = f'{question_id + 1}/{os.getenv("COL_QUESTIONS")} {question.question}'  # Тут вопрос из базы
    menu_main = None

    # КнопИ Нужно взять значения из базы
    if question_id + 1 == int(os.getenv('COL_QUESTIONS')):
        # Если сейчас будет последний вопрос:
        # Поменять level на меню с результатом
        menu_main = 'show_result'

    kbds = get_user_question_btns(question_id=question_id,
                                  question=question,
                                  menu_main=menu_main)

    return text, kbds


async def plus_points(state: FSMContext, session: AsyncSession, user_select: int, question_id: int = 0):
    """
    Метод запоминает баллы текущей викторины
    :param state:
    :param session:
    :param user_select: Какой вариант выбрал пользователь
    :param question_id: Текущий id вопроса из БД, который был выбран для викторины
    :return:
    """
    data = await state.get_data()
    questions_id = data.get('questions_id')
    if questions_id:
        # Если викторина уже идет
        question = await get_question(session, questions_id[question_id - 1])
        answer = list(json.loads(question.answer).values())[user_select]
        for v in answer:
            if not v in data['weights']:
                data['weights'][v] = 1
            else:
                data['weights'][v] += 1

        await state.update_data({'weights': data['weights']})


async def show_result(state: FSMContext):
    data = await state.get_data()
    max_value, result = 0, ''
    for k, v in data['weights'].items():
        if max_value < v:
            max_value, result = v, k

    path_file, image = None, None
    text = f'Твой результат: "{result}"\nПосмотри какой хорошенький зверёк!😊'
    dir_foto = os.path.join(os.getcwd(), f"modul_quiz/foto")
    for _f in os.listdir(dir_foto):
        if _f.lower().strip().__contains__(result.lower().strip()):
            path_file = os.path.join(dir_foto, _f)
            break
    if path_file:
        with open(path_file, "rb") as image_from_buffer:
            image = BufferedInputFile(image_from_buffer.read(), filename=f"{result}")

    kbds = get_result_btns()

    return text, kbds, image


async def program():
    """
    О програме опеки
    :return:
    """
    text = """
    Возьмите животное под опеку!\n\n

    Опека над животным из Московского зоопарка помогает сохраненить биоразнообразия 
    Земли и, конечно, **это реальная помощь животным Московского зоопарка!**
    Благодаря вам мы можем улучшить условия содержания наших обитателей.
    Участвуйте в жизни Московского зоопарка, почувствуйте причастность к делу сохранения природы. 
    Станте опекуном и поделитесь любовью и заботой со своим подопечным
    
    Опекать – значит помогать любимым животным.
        """
    kbds = get_program_btns()

    return text, kbds


async def get_menu_content(
        menu_name: str,
        session: AsyncSession = None,
        question_id: Optional[int] = None,
        state=None):
    if menu_name == 'program':
        # О программе опеки (с кнопками обратной связи и "Оставить отзыв о боте"
        return await program()
    elif menu_name == 'not_quiz':
        # Тоже рассказать о программе опеки, но поменять текст сообщения
        pass
