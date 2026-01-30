from pydantic import BaseModel


class LibraryFundBase(BaseModel):
    university_id: int

    arm_fond_nomi: int = 0
    arm_fond_nusxada: int = 0

    uz_kiril: int = 0
    uz_lotin: int = 0
    rus: int = 0
    ingliz: int = 0
    boshqa_tillar: int = 0

    bosma: int = 0
    elektron: int = 0
    brayl: int = 0
    audio: int = 0

    oquv_adabiyot: int = 0
    ilmiy_adabiyot: int = 0
    badiiy_adabiyot: int = 0
    xorijiy_adabiyot: int = 0
    boshqa_adabiyot: int = 0


class LibraryFundCreate(LibraryFundBase):
    pass

class LibraryFundUpdate(BaseModel):
    arm_fond_nomi: int | None = None
    arm_fond_nusxada: int | None = None

    uz_kiril: int | None = None
    uz_lotin: int | None = None
    rus: int | None = None
    ingliz: int | None = None
    boshqa_tillar: int | None = None

    bosma: int | None = None
    elektron: int | None = None
    brayl: int | None = None
    audio: int | None = None

    oquv_adabiyot: int | None = None
    ilmiy_adabiyot: int | None = None
    badiiy_adabiyot: int | None = None
    xorijiy_adabiyot: int | None = None
    boshqa_adabiyot: int | None = None


class LibraryFundResponse(LibraryFundBase):
    id: int
    university_name: str

    class Config:
        from_attributes = True
