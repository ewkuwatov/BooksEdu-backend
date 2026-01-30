from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class LiteratureReport(Base):
    __tablename__ = "literature_reports"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)

    darslik_nomda = Column(Integer, default=0)
    darslik_nusxada = Column(Integer, default=0)

    oq_qollanma_nomda = Column(Integer, default=0)
    oq_qollanma_nusxada = Column(Integer, default=0)

    uslubiy_nomda = Column(Integer, default=0)
    uslubiy_nusxada = Column(Integer, default=0)

    lugat_nomda = Column(Integer, default=0)
    lugat_nusxada = Column(Integer, default=0)

    uslubiy_korsatma_nomda = Column(Integer, default=0)
    uslubiy_korsatma_nusxada = Column(Integer, default=0)

    uslubiy_tavsiyanoma_nomda = Column(Integer, default=0)
    uslubiy_tavsiyanoma_nusxada = Column(Integer, default=0)

    malumotlar_nomda = Column(Integer, default=0)
    malumotlar_nusxada = Column(Integer, default=0)

    maruzalar_nomda = Column(Integer, default=0)
    maruzalar_nusxada = Column(Integer, default=0)

    mashqlar_nomda = Column(Integer, default=0)
    mashqlar_nusxada = Column(Integer, default=0)

    daydjest_nomda = Column(Integer, default=0)
    daydjest_nusxada = Column(Integer, default=0)

    university = relationship("University", back_populates="literature")
