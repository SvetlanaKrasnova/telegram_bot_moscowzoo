from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import QuestionsORM, ReviewORM


async def insert_one(session: AsyncSession, data):
    session.add(data)
    await session.commit()
    return data.id


async def get_questions(session: AsyncSession):
    """
    Получаем все вопросы, которые есть сейчас в базе
    :return:
    """
    query = select(QuestionsORM)
    result = await session.execute(query)
    return result.scalars().all()


async def get_question(session: AsyncSession, id_question):
    """
    Получаем вопрос по его id
    :return:
    """
    query = select(QuestionsORM).where(QuestionsORM.id == id_question)
    result = await session.execute(query)
    return result.scalar()


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


async def get_review(session: AsyncSession):
    """
    Получить последние 10 отзывов
    :param session:
    :return:
    """
    result = await session.query(ReviewORM).order_by(ReviewORM.id.desc()).limit(10)
    return result.scalars().all()
