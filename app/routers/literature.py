# app/routers/literature.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import FileResponse
import os
from fastapi import UploadFile, File, Form


from app.db.session import get_db
from app.models.literature import Literature
from app.schemas.enums import FontTypeEnum, LanguageEnum, ConditionEnum, UsageStatusEnum
from app.schemas.literature import LiteratureCreate, LiteratureUpdate, LiteratureOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/literatures", tags=["literatures"])

@router.get("/", response_model=List[LiteratureOut])
async def get_literatures(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Literature))
    return result.scalars().all()

# ---- Создание ---- (owner / superadmin)
@router.post("/", response_model=LiteratureOut)
async def create_literature(
    data: LiteratureCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature_data = data.model_dump()

    if current_user.role == "superadmin":
        literature_data["university_id"] = current_user.university_id
    elif current_user.role == "owner":
        if "university_id" not in literature_data or not literature_data["university_id"]:
            raise HTTPException(status_code=400, detail="university_id is required for owner")
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    literature = Literature(**literature_data)
    db.add(literature)
    await db.commit()
    await db.refresh(literature)
    return literature




# ---- Обновление ---- (owner / superadmin)
@router.put("/{literature_id}", response_model=LiteratureOut)
async def update_literature(
    literature_id: int,
    data: LiteratureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")

    if current_user.role == "superadmin" and literature.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(literature, field, value)

    await db.commit()
    await db.refresh(literature)
    return literature


# ---- Удаление ---- (owner / superadmin)
@router.delete("/{literature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_literature(
    literature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")

    if current_user.role == "superadmin" and literature.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(literature)
    await db.commit()
    return None


# ---- Загрузка файла ----
@router.post("/upload", response_model=LiteratureOut)
async def create_literature_with_file(
    title: str = Form(...),
    kind: str = Form(...),
    author: str = Form(None),
    publisher: str = Form(None),
    language: LanguageEnum = Form(...),
    font_type: FontTypeEnum = Form(...),
    year: int = Form(...),
    printed_count: int = Form(None),
    condition: ConditionEnum = Form(...),
    usage_status: UsageStatusEnum = Form(...),
    subject_id: int = Form(...),
    university_id: int = Form(...),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    file_path = None
    if file:
        # Абсолютный путь
        upload_dir = os.path.join(os.getcwd(), "uploads/literatures")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

    literature = Literature(
        title=title,
        kind=kind,
        author=author,
        publisher=publisher,
        language=language,
        font_type=font_type,
        year=year,
        printed_count=printed_count,
        condition=condition,
        usage_status=usage_status,
        subject_id=subject_id,
        university_id=university_id,
        file_path=file_path
    )
    db.add(literature)
    await db.commit()
    await db.refresh(literature)
    return literature

# ---- Скачивание файла ----
@router.get("/{literature_id}/download")
async def download_literature_file(
    literature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature or not literature.file_path:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(literature.file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    # Отдаём файл как FileResponse
    filename = os.path.basename(literature.file_path)
    return FileResponse(path=literature.file_path, filename=filename)

# ---- Обновление с файлом ----
@router.put("/upload/{literature_id}", response_model=LiteratureOut)
async def update_literature_with_file(
    literature_id: int,
    title: str = Form(...),
    kind: str = Form(...),
    author: str = Form(None),
    publisher: str = Form(None),
    language: LanguageEnum = Form(...),
    font_type: FontTypeEnum = Form(...),
    year: int = Form(...),
    printed_count: int = Form(None),
    condition: ConditionEnum = Form(...),
    usage_status: UsageStatusEnum = Form(...),
    subject_id: int = Form(...),
    university_id: int = Form(...),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")

    if current_user.role == "superadmin" and literature.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    # если пришёл новый файл — перезаписываем
    if file:
        upload_dir = os.path.join(os.getcwd(), "uploads/literatures")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        literature.file_path = file_path

    # обновляем остальные поля
    literature.title = title
    literature.kind = kind
    literature.author = author
    literature.publisher = publisher
    literature.language = language
    literature.font_type = font_type
    literature.year = year
    literature.printed_count = printed_count
    literature.condition = condition
    literature.usage_status = usage_status
    literature.subject_id = subject_id
    literature.university_id = university_id

    await db.commit()
    await db.refresh(literature)
    return literature
