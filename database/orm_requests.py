from typing import List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import QuestionsORM

async def get_questions(session: AsyncSession):
    """
    Получаем все вопросы, которые есть сейчас в базе
    :return:
    """
    query = select(QuestionsORM)
    result = await session.execute(query)
    return result.scalars().all()

async def delete_question(session: AsyncSession, question_name: str):
    """
    Удалить вопрос
    :param session:
    :return:
    """
    query = delete(QuestionsORM).where(QuestionsORM.question == question_name)
    await session.execute(query)
    await session.commit()

async def delete_all_questions(session: AsyncSession, data: List[QuestionsORM]):
    """
    Удалить все вопросы
    :param session:
    :return:
    """
    for q in data:
        query = delete(QuestionsORM).where(QuestionsORM.question == q.question)
        await session.execute(query)
        await session.commit()


async def add_question(session: AsyncSession, data: List[QuestionsORM]):
    """
    Добавить вопрос
    :param session:
    :return:
    """
    session.add_all(data)
    await session.commit()

def add_review():
    """
    Добавить отзыв
    :return:
    """