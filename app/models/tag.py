from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

# Ассоциация many-to-many: новости ↔ теги
news_tags = Table(
    "news_tags",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    news = relationship("News", secondary=news_tags, back_populates="tags")
