from fastapi import Depends
from sqlmodel import create_engine, Session
from typing import Annotated
from .config import settings

engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

GetSession = Annotated[Session, Depends(get_session)]
