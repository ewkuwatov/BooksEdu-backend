# app/routers/literature.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import FileResponse
import os


from app.db.session import get_db
from app.models.literature import Literature
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


@router.get("/{literature_id}/download")
async def download_literature(
    literature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    literature = await db.get(Literature, literature_id)
    if not literature or not literature.file_path:
        raise HTTPException(status_code=404, detail="File not found")

    # Проверка доступа
    if current_user.role == "superadmin" and literature.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    # Проверка существования файла на сервере
    if not os.path.exists(literature.file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    # Отдаём файл
    filename = os.path.basename(literature.file_path)
    return FileResponse(path=literature.file_path, filename=filename)