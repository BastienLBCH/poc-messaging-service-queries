import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.settings import Settings

settings = Settings()

dir = os.path.dirname(os.path.abspath(__file__)) # This is your file dir

SessionLocal = None
if settings.env == "DEV":
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{dir}/sql_app.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

