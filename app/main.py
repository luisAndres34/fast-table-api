from fastapi import FastAPI, Request, status
from sqlmodel import SQLModel
from .routers import items, users
from .database import engine
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": "Integrity Error", "detail": "Duplicated name"})

app.include_router(items.router)
app.include_router(users.router)

@app.on_event("startup")
def on_startup():
   SQLModel.metadata.create_all(engine)
