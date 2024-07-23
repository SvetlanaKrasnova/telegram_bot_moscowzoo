import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv
from database.models import QuestionsORM
from database.models import Base

load_dotenv()

"""
Модуль по разворачиванию/удалению базы
"""

engine = create_engine(f"sqlite:///database_bot.db")


def create_db():
    Base.metadata.create_all(bind=engine)


@contextmanager
def session() -> sessionmaker:
    s = sessionmaker(bind=engine)
    session = s()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def add_one(data):
    with session() as s:
        s.add(data)
        s.flush()
        return data.id


def adding_questions():
    with open('../modul_quiz/questions_db.json', encoding='utf-8') as f:
        json_data = json.load(f)

    for q in json_data['questions']:
        add_one(QuestionsORM(
            question=q['question'],
            answer=json.dumps(q['answer'], ensure_ascii=False)
        ))


create_db()
adding_questions()
