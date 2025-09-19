from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.session import get_db
from app.models.news import News
from app.models.tag import Tag
from app.schemas.news import NewsCreate, NewsUpdate, NewsOut
from app.models.user import User
from app.dependencies import get_current_user
from fastapi import Form, File, UploadFile
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/news", tags=["News"])

# ✅ Создание новости
@router.post("/", response_model=NewsOut)
async def create_news(
    title: str = Form(...),
    description: str = Form(...),
    university_id: int = Form(...),
    tags: Optional[List[str]] = Form(None),
    img: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 🎯 Проверка прав
    if current_user.role == "owner":
        if not university_id:
            raise HTTPException(status_code=400, detail="university_id обязателен для owner")
    elif current_user.role == "superadmin":
        university_id = current_user.university_id
    else:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # 📂 Сохраняем файл
    image_url = None
    if img:
        file_path = f"uploads/{img.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await img.read())
        image_url = file_path

    # ✅ Создаём новость
    new_news = News(
        title=title,
        description=description,
        img=image_url,
        university_id=university_id,
    )

    # ✅ Добавляем теги (если переданы)
    if tags:
        new_tags = []
        for tag_name in tags:
            tag_name = tag_name.lower().strip()
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            new_tags.append(tag)

        new_news.tags = new_tags

    db.add(new_news)
    await db.commit()
    await db.refresh(new_news)

    return new_news

# ✅ Получение всех новостей (с фильтром по тегу)
@router.get("/", response_model=List[NewsOut])
async def get_all_news(
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(News).order_by(News.date.desc())

    if tag:
        query = query.join(News.tags).where(Tag.name == tag.lower())

    result = await db.execute(query)
    return result.scalars().unique().all()


# ✅ Обновление новости
@router.put("/{news_id}", response_model=NewsOut)
async def update_news(
    news_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    img: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Загружаем сразу с тегами
    result = await db.execute(
        select(News).options(selectinload(News.tags)).where(News.id == news_id)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    if title is not None:
        news.title = title
    if description is not None:
        news.description = description

    if img:
        file_path = f"uploads/{img.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await img.read())
        news.img = file_path

    if tags is not None:
        new_tags = []
        for tag_name in tags:
            tag_name = tag_name.lower().strip()
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            new_tags.append(tag)

        # заменяем существующие связи
        news.tags.clear()
        news.tags.extend(new_tags)

    await db.commit()
    await db.refresh(news)
    return news

# ✅ Удаление новости
@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    # 🎯 Проверка прав
    if current_user.role == "superadmin" and news.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.delete(news)
    await db.commit()

    return {"message": "Новость удалена"}
