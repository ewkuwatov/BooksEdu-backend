from sqlalchemy import Table, Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

# ======================
# Таблица связки many-to-many
# ======================
subject_directions = Table(
    "subject_directions",
    Base.metadata,
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
    Column("direction_id", Integer, ForeignKey("directions.id", ondelete="CASCADE"), primary_key=True),
)

# ======================
# Основная таблица Subject
# ======================
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    kafedra_id = Column(Integer, ForeignKey("kafedras.id", ondelete="CASCADE"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)

    # --- Relationships ---
    kafedra = relationship("Kafedra", back_populates="subjects")
    directions = relationship("Direction", secondary=subject_directions, back_populates="subjects")
    literature = relationship("Literature", back_populates="subject", cascade="all, delete-orphan")

    # --- Уникальность ---
    __table_args__ = (
        UniqueConstraint("name", "kafedra_id", "university_id", name="uq_subject_name_kafedra_university"),
    )
