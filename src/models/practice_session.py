from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    practice_text_id = Column(Integer, ForeignKey("practice_texts.id"))
    audio_file_path = Column(String(500))
    transcribed_text = Column(Text)
    pronunciation_score = Column(Float)  # Overall pronunciation score
    feedback = Column(Text)  # AI feedback
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with practice text
    practice_text = relationship("PracticeText", back_populates="practice_sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "practice_text_id": self.practice_text_id,
            "audio_file_path": self.audio_file_path,
            "transcribed_text": self.transcribed_text,
            "pronunciation_score": self.pronunciation_score,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat()
        }
