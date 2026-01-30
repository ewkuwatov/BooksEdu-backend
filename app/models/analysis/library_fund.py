from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class LibraryFund(Base):
    __tablename__ = "library_fund"

    id = Column(Integer, primary_key=True, index=True)

    university_id = Column(
        Integer,
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False
    )

    university = relationship("University", backref="library_funds")

    # ARM fond
    arm_fond_nomi = Column(Integer, default=0)
    arm_fond_nusxada = Column(Integer, default=0)

    # Tillar
    uz_kiril = Column(Integer, default=0)
    uz_lotin = Column(Integer, default=0)
    rus = Column(Integer, default=0)
    ingliz = Column(Integer, default=0)
    boshqa_tillar = Column(Integer, default=0)

    # Shakllar
    bosma = Column(Integer, default=0)
    elektron = Column(Integer, default=0)
    brayl = Column(Integer, default=0)
    audio = Column(Integer, default=0)

    # Adabiyotlar
    oquv_adabiyot = Column(Integer, default=0)
    ilmiy_adabiyot = Column(Integer, default=0)
    badiiy_adabiyot = Column(Integer, default=0)
    xorijiy_adabiyot = Column(Integer, default=0)
    boshqa_adabiyot = Column(Integer, default=0)
