import json
from typing import Optional
from pydantic import Field
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix="menu"):
    menu_name: str = 'start_page'
    user_select: Optional[int] = Field(default=0)
    question_id: Optional[int] = 0  # текущий номер вопроса из questions с которым работаем


def get_user_main_btns():
    """
    Это кнопки для самой стартовой страницы
    :param level:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Начать викторину 🦁": "quiz",
        "Узнать сразу 🐥": "program"
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()


def get_user_question_btns(question_id: int, question, menu_main=None):
    """
    Кнопки - варианты ответов на вопрос (для викторины)
    :param question: вопрос из БД
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for i, k in enumerate(list(json.loads(question.answer).keys())):
        keyboard.add(InlineKeyboardButton(text=k,
                                          callback_data=MenuCallBack(user_select=i,
                                                                     menu_name=menu_main if menu_main else 'quiz',
                                                                     question_id=question_id + 1).pack()))

    return keyboard.adjust(*(1,)).as_markup()


def get_result_btns(result_quiz):
    """
    Кнопки - когда пользователю отображается результат пройденной викторины
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Попробовать ещё раз? 🙂": "quiz",  # Возможность перезапуска
        "Программа опеки 🦋": "program",
        "Оставить отзыв": "feedback",  # Механизм обратной связи
        "Поделиться результатом": "send_result",  # Поддержка социальных сетей
        "Связаться с сотрудником": "manager_contact",  # Контактный механизм
    }
    for text, menu_name in btns.items():
        if menu_name == 'send_result':
            keyboard.add(InlineKeyboardButton(text=text,
                                              switch_inline_query=f'\n{result_quiz}'))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(menu_name=menu_name).pack()))
    return keyboard.adjust(1).as_markup()


def get_program_btns():
    """
    Кнопки - когда пользователю отображается информация об опеки
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "В начало 🙂": "restart",
        "Оставить отзыв": "feedback",
        "Связаться с сотрудником ☎️": "manager_contact",
    }
    for text, menu_name in btns.items():
        if menu_name == 'send_result': # switch_inline_query
            keyboard.add(InlineKeyboardButton(text=text,
                                              switch_inline_query='',
                                              callback_data=MenuCallBack(menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()

def get_contacts_btns():
    """
        Кнопки - когда пользовать нажал "Связь с сотрудником"
        :return:
        """
    keyboard = InlineKeyboardBuilder()
    btns = {
        "В начало 🙂": "restart",
        "Оставить отзыв": "feedback",
    }
    for text, menu_name in btns.items():
        keyboard.add(InlineKeyboardButton(text=text,
                                          callback_data=MenuCallBack(menu_name=menu_name).pack()))

    return keyboard.adjust(1).as_markup()