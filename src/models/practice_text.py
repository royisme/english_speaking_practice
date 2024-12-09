from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class PracticeText(Base):
    __tablename__ = "practice_texts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    difficulty_level = Column(String(50))  # beginner, intermediate, advanced
    category = Column(String(100))  # conversation, business, academic, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with practice sessions
    practice_sessions = relationship("PracticeSession", back_populates="practice_text")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "difficulty_level": self.difficulty_level,
            "category": self.category,
            "created_at": self.created_at.isoformat()
        }
