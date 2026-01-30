from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import Base, engine
from app.routers import (
    auth, university, user, direction, kafedra,
    subject, literature, stats, general_stats,
    statistics, admin, news,
)

app = FastAPI(title="BooksEdu API")

# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
	"http://localhost:5173",
        "https://localhost:5173",

        "https://booksedu.uz",       # если фронтенд будет тут
        "https://www.booksedu.uz",
	"http://booksedu.uz",
	"http://www.booksedu.uz",        
	"https://bookedu.uz",        # бекенд домен ДОЛЖЕН быть разрешён
        "https://www.bookedu.uz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Routers =====================
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(university.router)
app.include_router(user.router)
app.include_router(direction.router)
app.include_router(kafedra.router)
app.include_router(subject.router)
app.include_router(literature.router)
app.include_router(stats.router)
app.include_router(statistics.router)
app.include_router(general_stats.router)
app.include_router(news.router)



# ===================== Startup =====================
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "🚀 FastAPI + PostgreSQL + Docker работает!"}
