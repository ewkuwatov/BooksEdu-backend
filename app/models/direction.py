# app/models/direction.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

class Direction(Base):
    __tablename__ = "directions"

    __table_args__ = (
        UniqueConstraint("number", "name", "course", "university_id", name="uq_direction_unique"),
    )

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    name = Column(String, nullable=False)
    course = Column(Integer, nullable=False)
    student_count = Column(Integer, nullable=True)

    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"))
    university = relationship("University", back_populates="directions")

    subjects = relationship(
        "Subject",
        secondary="subject_directions",
        back_populates="directions"
    )

