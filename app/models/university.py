from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    location = Column(String, nullable=True)

    admins = relationship("Admin", back_populates="university", cascade="all, delete-orphan")
    directions = relationship("Direction", back_populates="university", cascade="all, delete-orphan")
    kafedras = relationship("Kafedra", back_populates="university", cascade="all, delete-orphan")
