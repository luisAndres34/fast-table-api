from fastapi import FastAPI, Request, status
from sqlmodel import SQLModel
from .models import Item, User, Category
from .routers import items, users, categories
from .database import engine
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "Integrity Error", "detail": "Duplicated name"})

app.include_router(items.router)
app.include_router(users.router)
app.include_router(categories.router)

