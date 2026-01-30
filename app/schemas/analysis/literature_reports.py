from pydantic import BaseModel
from typing import Optional


# -------- CREATE --------
class LiteratureCreate(BaseModel):
    university_id: int

    darslik_nomda: int = 0
    darslik_nusxada: int = 0

    oq_qollanma_nomda: int = 0
    oq_qollanma_nusxada: int = 0

    uslubiy_nomda: int = 0
    uslubiy_nusxada: int = 0

    lugat_nomda: int = 0
    lugat_nusxada: int = 0

    uslubiy_korsatma_nomda: int = 0
    uslubiy_korsatma_nusxada: int = 0

    uslubiy_tavsiyanoma_nomda: int = 0
    uslubiy_tavsiyanoma_nusxada: int = 0

    malumotlar_nomda: int = 0
    malumotlar_nusxada: int = 0

    maruzalar_nomda: int = 0
    maruzalar_nusxada: int = 0

    mashqlar_nomda: int = 0
    mashqlar_nusxada: int = 0

    daydjest_nomda: int = 0
    daydjest_nusxada: int = 0

class LiteratureUpdate(BaseModel):
    darslik_nomda: Optional[int] = None
    darslik_nusxada: Optional[int] = None

    oq_qollanma_nomda: Optional[int] = None
    oq_qollanma_nusxada: Optional[int] = None

    uslubiy_nomda: Optional[int] = None
    uslubiy_nusxada: Optional[int] = None

    lugat_nomda: Optional[int] = None
    lugat_nusxada: Optional[int] = None

    uslubiy_korsatma_nomda: Optional[int] = None
    uslubiy_korsatma_nusxada: Optional[int] = None

    uslubiy_tavsiyanoma_nomda: Optional[int] = None
    uslubiy_tavsiyanoma_nusxada: Optional[int] = None

    malumotlar_nomda: Optional[int] = None
    malumotlar_nusxada: Optional[int] = None

    maruzalar_nomda: Optional[int] = None
    maruzalar_nusxada: Optional[int] = None

    mashqlar_nomda: Optional[int] = None
    mashqlar_nusxada: Optional[int] = None

    daydjest_nomda: Optional[int] = None
    daydjest_nusxada: Optional[int] = None

class LiteratureResponse(BaseModel):
    id: int
    university_id: int
    university_name: str

    darslik_nomda: int
    darslik_nusxada: int

    oq_qollanma_nomda: int
    oq_qollanma_nusxada: int

    uslubiy_nomda: int
    uslubiy_nusxada: int

    lugat_nomda: int
    lugat_nusxada: int

    uslubiy_korsatma_nomda: int
    uslubiy_korsatma_nusxada: int

    uslubiy_tavsiyanoma_nomda: int
    uslubiy_tavsiyanoma_nusxada: int

    malumotlar_nomda: int
    malumotlar_nusxada: int

    maruzalar_nomda: int
    maruzalar_nusxada: int

    mashqlar_nomda: int
    mashqlar_nusxada: int

    daydjest_nomda: int
    daydjest_nusxada: int

    class Config:
        orm_mode = True
