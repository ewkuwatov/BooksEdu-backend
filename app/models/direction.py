# app/models/direction.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Direction(Base):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    name = Column(String, nullable=False)
    course = Column(Integer, unique=True, nullable=False)
    student_count = Column(Integer, nullable=False)

    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"))
    university = relationship("University", back_populates="directions")

    subjects = relationship(
        "Subject",
        secondary="subject_directions",
        back_populates="directions"
    )

