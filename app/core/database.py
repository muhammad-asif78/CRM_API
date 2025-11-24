from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL not found in .env")  # helpful error

engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Only rollback for database-related exceptions
        # HTTPException from FastAPI should not trigger rollback
        from fastapi import HTTPException
        if not isinstance(e, HTTPException):
            db.rollback()
        raise
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
