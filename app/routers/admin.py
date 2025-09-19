from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminOut, AdminUpdate
from app.utils.security import get_password_hash

router = APIRouter(prefix="/admins", tags=["admins"])


# ----------- Создание ----------
@router.post("/", response_model=AdminOut)
async def create_admin(admin_in: AdminCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = get_password_hash(admin_in.password)
    new_admin = Admin(
        email=admin_in.email,
        hashed_password=hashed_pw,
        role=admin_in.role,
        university_id=admin_in.university_id
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin


# ----------- Получение всех ----------
@router.get("/", response_model=list[AdminOut])
async def get_admins(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin))
    return result.scalars().all()


# ----------- Получение по ID ----------
@router.get("/{admin_id}", response_model=AdminOut)
async def get_admin(admin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


# ----------- Обновление ----------
@router.put("/{admin_id}", response_model=AdminOut)
async def update_admin(admin_id: int, admin_in: AdminUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin_in.email is not None:
        admin.email = admin_in.email
    if admin_in.role is not None:
        admin.role = admin_in.role
    if admin_in.university_id is not None:
        admin.university_id = admin_in.university_id
    if admin_in.password is not None:
        admin.hashed_password = get_password_hash(admin_in.password)

    await db.commit()
    await db.refresh(admin)
    return admin


# ----------- Удаление ----------
@router.delete("/{admin_id}", response_model=dict)
async def delete_admin(admin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    await db.delete(admin)
    await db.commit()
    return {"msg": "Admin deleted"}
