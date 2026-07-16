from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import auth_routes, subscription_routes, chat_routes

app = FastAPI(title="Study Assistant Pro API")


@app.on_event("startup")
async def on_startup():
    await init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(subscription_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
async def root():
    return {"status": "Study Assistant Pro API is running"}
