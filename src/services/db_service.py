from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from ..models import PracticeText, PracticeSession
from ..models.base import get_db

class DBService:
    def __init__(self):
        self.db = next(get_db())

    def create_practice_text(self, title: str, content: str, 
                           difficulty_level: str, category: str) -> PracticeText:
        db_text = PracticeText(
            title=title,
            content=content,
            difficulty_level=difficulty_level,
            category=category
        )
        self.db.add(db_text)
        self.db.commit()
        self.db.refresh(db_text)
        return db_text

    def get_practice_text(self, text_id: int) -> Optional[PracticeText]:
        return self.db.query(PracticeText).filter(PracticeText.id == text_id).first()

    def get_all_practice_texts(self) -> List[PracticeText]:
        return self.db.query(PracticeText).all()

    def create_practice_session(self, practice_text_id: int, audio_file_path: str,
                              transcribed_text: str, pronunciation_score: float,
                              feedback: str) -> PracticeSession:
        db_session = PracticeSession(
            practice_text_id=practice_text_id,
            audio_file_path=audio_file_path,
            transcribed_text=transcribed_text,
            pronunciation_score=pronunciation_score,
            feedback=feedback
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_practice_sessions(self, text_id: Optional[int] = None) -> List[PracticeSession]:
        query = self.db.query(PracticeSession)
        if text_id:
            query = query.filter(PracticeSession.practice_text_id == text_id)
        return query.all()

    def get_practice_session(self, session_id: int) -> Optional[PracticeSession]:
        return self.db.query(PracticeSession).filter(PracticeSession.id == session_id).first()

    def get_practice_history(self, text_id: int) -> List[PracticeSession]:
        """
        Retrieve practice sessions for a specific text
        
        :param text_id: ID of the practice text
        :return: List of PracticeSession objects
        """
        return self.get_practice_sessions(text_id)

    def get_preset_texts(self, category: str = 'preset') -> List[dict]:
        """
        获取预设文本列表
        
        :param category: 文本类别，默认为'preset'
        :return: 预设文本列表，每个文本为字典格式
        """
        preset_texts = self.db.query(PracticeText).filter(PracticeText.category == category).all()
        
        # 如果没有预设文本，创建一些默认文本
        if not preset_texts:
            default_texts = [
                {
                    'title': '自我介绍',
                    'content': 'Hello, my name is Roy. I am a software engineer from San Francisco. I love coding and learning new technologies.',
                    'difficulty_level': 'beginner',
                    'category': 'preset'
                },
                {
                    'title': '日常生活',
                    'content': 'Every morning, I wake up at 6 AM and start my day with a cup of coffee. I enjoy reading books and listening to podcasts during my free time.',
                    'difficulty_level': 'intermediate',
                    'category': 'preset'
                },
                {
                    'title': '职业规划',
                    'content': 'As a software developer, I am passionate about creating innovative solutions that can make people\'s lives easier. I believe in continuous learning and staying updated with the latest technological trends.',
                    'difficulty_level': 'advanced',
                    'category': 'preset'
                }
            ]
            
            # 创建并保存默认文本
            for text_data in default_texts:
                db_text = PracticeText(**text_data)
                self.db.add(db_text)
            
            self.db.commit()
            preset_texts = self.db.query(PracticeText).filter(PracticeText.category == category).all()
        
        # 转换为字典列表
        return [
            {
                'id': text.id, 
                'title': text.title,
                'content': text.content, 
                'difficulty': text.difficulty_level
            } for text in preset_texts
        ]
