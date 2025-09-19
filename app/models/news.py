from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.tag import news_tags
from app.db.session import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    img = Column(String, nullable=True)  # путь к картинке (опционально)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)  # дата публикации

    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)

    university = relationship("University", back_populates="news")
    tags = relationship("Tag", secondary=news_tags, back_populates="news")
