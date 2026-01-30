# app/routers/literature.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid

from app.db.session import get_db
from app.models.literature import Literature
from app.schemas.enums import FontTypeEnum, LanguageEnum, ConditionEnum, UsageStatusEnum
from app.schemas.literature import LiteratureCreate, LiteratureUpdate, LiteratureOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/literatures", tags=["literatures"])


# --- Вспомогательная функция для сохранения файлов ---
async def save_upload_file(file: UploadFile, folder="uploads/literatures") -> str:
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return file_path


# ---- Получение всех литератур ----
@router.get("/", response_model=List[LiteratureOut])
async def get_literatures(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Literature))
    return result.scalars().all()


# ---- Создание литературы (owner / superadmin) ----
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


# ---- Обновление литературы (owner / superadmin) ----
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


# ---- Удаление литературы (owner / superadmin) ----
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


# ---- Создание литературы с файлами ----
@router.post("/upload", response_model=LiteratureOut)
async def create_literature_with_files(
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
    file_2: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    file_path = await save_upload_file(file) if file else None
    file_path_2 = await save_upload_file(file_2) if file_2 else None

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
        file_path=file_path,
        file_path_2=file_path_2
    )
    db.add(literature)
    await db.commit()
    await db.refresh(literature)
    return literature


# ---- Обновление литературы с файлами ----
@router.put("/upload/{literature_id}", response_model=LiteratureOut)
async def update_literature_with_files(
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
    file_2: UploadFile = File(None),
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

    if file:
        literature.file_path = await save_upload_file(file)
    if file_2:
        literature.file_path_2 = await save_upload_file(file_2)

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


# ---- Скачивание файлов ----
@router.get("/{literature_id}/download/{file_number}")
async def download_literature_file(
    literature_id: int,
    file_number: int,  # 1 или 2
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")

    path = literature.file_path if file_number == 1 else literature.file_path_2 if file_number == 2 else None
    if not path:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on server")

    filename = os.path.basename(path)
    return FileResponse(path=path, filename=filename)
