from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import Base, engine
from app.routers import auth, university, user, direction, kafedra, subject, literature, stats, statistics
app = FastAPI()

# ===================== CORS =====================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # можно добавить другие источники, если нужно
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # разрешаем фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Routers =====================
app.include_router(auth.router)
app.include_router(university.router)
app.include_router(user.router)
app.include_router(direction.router)
app.include_router(kafedra.router)
app.include_router(subject.router)
app.include_router(literature.router)
app.include_router(stats.router)
app.include_router(statistics.router)

# ===================== Startup =====================
@app.on_event("startup")
async def startup():
    # Создание всех таблиц асинхронно
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
