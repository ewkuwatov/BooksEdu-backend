# app/models/literature.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
from enum import Enum as PyEnum

class Literature(Base):
    __tablename__ = "literature"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    author = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    language = Column(String, nullable=False)
    font_type = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    printed_count = Column(Integer, nullable=True)
    condition = Column(String, nullable=False)
    usage_status = Column(String, nullable=False)
    image = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_path_2 = Column(String, nullable=True)

    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    subject = relationship("Subject", back_populates="literature")

    university_id = Column(Integer, ForeignKey("universities.id"))
