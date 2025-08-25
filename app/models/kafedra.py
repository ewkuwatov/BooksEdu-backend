# app/models/kafedra.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Kafedra(Base):
    __tablename__ = "kafedras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"))
    university = relationship("University", back_populates="kafedras")

    subjects = relationship("Subject", back_populates="kafedra", cascade="all, delete-orphan")
