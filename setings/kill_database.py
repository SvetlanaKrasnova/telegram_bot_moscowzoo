from database.models import Base
from sqlalchemy import create_engine

engine = create_engine(f"sqlite:///database_bot.db")
Base.metadata.drop_all(bind=engine)
