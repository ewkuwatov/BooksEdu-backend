import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import FileResponse

from app.db.session import get_db
from app.models.literature import Literature
from app.schemas.literature import (
    LiteratureCreate,
    LiteratureUpdate,
    LiteratureOut,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/literatures", tags=["Literature"])

UPLOAD_DIR = "uploads/literatures"


# ---------- GET ----------
@router.get("/", response_model=list[LiteratureOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Literature))
    return result.scalars().all()


# ---------- CREATE ----------
@router.post("/", response_model=LiteratureOut)
async def create_literature(
    data: LiteratureCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    literature = Literature(**data.model_dump())
    db.add(literature)
    await db.commit()
    await db.refresh(literature)
    return literature


# ---------- CREATE WITH FILES ----------
@router.post("/upload", response_model=LiteratureOut)
async def create_with_files(
    title: str = Form(...),
    kind: str = Form(...),
    language: str = Form(...),
    font_type: str = Form(...),
    condition: str = Form(...),
    usage_status: str = Form(...),
    year: int = Form(...),
    subject_id: int = Form(...),
    university_id: int = Form(...),
    author: str = Form(None),
    publisher: str = Form(None),
    printed_count: int = Form(None),
    file: UploadFile = File(None),
    file2: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = None
    file_path_2 = None

    if file:
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

    if file2:
        file_path_2 = f"{UPLOAD_DIR}/{file2.filename}"
        with open(file_path_2, "wb") as f:
            f.write(await file2.read())

    literature = Literature(
        title=title,
        kind=kind,
        language=language,
        font_type=font_type,
        condition=condition,
        usage_status=usage_status,
        year=year,
        subject_id=subject_id,
        university_id=university_id,
        author=author,
        publisher=publisher,
        printed_count=printed_count,
        file_path=file_path,
        file_path_2=file_path_2,
    )

    db.add(literature)
    await db.commit()
    await db.refresh(literature)
    return literature


# ---------- UPDATE ----------
@router.put("/{literature_id}", response_model=LiteratureOut)
async def update_literature(
    literature_id: int,
    data: LiteratureUpdate,
    db: AsyncSession = Depends(get_db),
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(404, "Not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(literature, k, v)

    await db.commit()
    await db.refresh(literature)
    return literature


# ---------- UPDATE FILES ----------
@router.put("/upload/{literature_id}", response_model=LiteratureOut)
async def update_files(
    literature_id: int,
    file: UploadFile = File(None),
    file2: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(404, "Not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if file:
        path = f"{UPLOAD_DIR}/{file.filename}"
        with open(path, "wb") as f:
            f.write(await file.read())
        literature.file_path = path

    if file2:
        path = f"{UPLOAD_DIR}/{file2.filename}"
        with open(path, "wb") as f:
            f.write(await file2.read())
        literature.file_path_2 = path

    await db.commit()
    await db.refresh(literature)
    return literature


# ---------- DOWNLOAD ----------
@router.get("/{literature_id}/download/{file_number}")
async def download_file(
    literature_id: int,
    file_number: int,
    db: AsyncSession = Depends(get_db),
):
    literature = await db.get(Literature, literature_id)
    if not literature:
        raise HTTPException(404, "Not found")

    path = (
        literature.file_path
        if file_number == 1
        else literature.file_path_2
    )

    if not path or not os.path.exists(path):
        raise HTTPException(404, "File not found")

    return FileResponse(path)
