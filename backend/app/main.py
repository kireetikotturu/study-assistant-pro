from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import auth_routes, subscription_routes, chat_routes

app = FastAPI(title="Study Assistant Pro API")


@app.on_event("startup")
async def on_startup():
    await init_db()


# Explicitly list allowed origins to prevent CORS errors in both local development and production
origins = [
    settings.frontend_url,                      # Dynamically reads from your .env / Render config
    "https://study-assistant-pro.vercel.app",   # Your live Vercel production frontend
    "http://localhost:5173",                     # Vite local development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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