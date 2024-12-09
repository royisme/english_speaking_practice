import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import unittest
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
import httpx

from src.services import (
    SpeechService, 
    AIService, 
    AudioService, 
    DBService
)
from src.models import PracticeText, PracticeSession
from src.models.base import init_db, engine
from sqlalchemy.orm import sessionmaker

class MockHTTPClient:
    """Mock HTTP client to prevent actual API calls during testing"""
    def request(self, *args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
            def json(self):
                return {"choices": [{"message": {"content": "Mock feedback"}}]}
        return MockResponse()

class TestEnglishPracticeApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize database
        init_db()
        cls.Session = sessionmaker(bind=engine)

    def setUp(self):
        # Initialize services with mock HTTP client for AI service
        mock_http_client = MockHTTPClient()
        
        self.speech_service = SpeechService()
        self.ai_service = AIService(http_client=mock_http_client)
        self.audio_service = AudioService()
        self.db_service = DBService()

    def test_audio_recording(self):
        """Test audio recording functionality"""
        # Create a temporary file for recording
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Generate a simple test audio signal
            duration = 2  # seconds
            sample_rate = 16000
            audio_data = np.random.normal(0, 0.1, duration * sample_rate)
            
            # Save the audio file
            sf.write(temp_file.name, audio_data, sample_rate)
            
            # Verify file was created and has content
            self.assertTrue(os.path.exists(temp_file.name))
            self.assertGreater(os.path.getsize(temp_file.name), 0)

    def test_speech_service(self):
        """Test Azure Speech Service pronunciation analysis"""
        # Create a test audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Generate a simple test audio signal
            duration = 2  # seconds
            sample_rate = 16000
            audio_data = np.random.normal(0, 0.1, duration * sample_rate)
            
            # Save the audio file
            sf.write(temp_file.name, audio_data, sample_rate)
            
            # Test pronunciation analysis
            reference_text = "Hello world, this is a test sentence."
            result = self.speech_service.analyze_pronunciation(
                temp_file.name, 
                reference_text
            )
            
            # Verify result structure
            self.assertIn('transcribed_text', result)
            self.assertIn('pronunciation_score', result)
            self.assertIn('accuracy_score', result)
            self.assertIn('fluency_score', result)
            self.assertIn('completeness_score', result)

    def test_ai_service(self):
        """Test AI feedback generation"""
        reference_text = "The quick brown fox jumps over the lazy dog."
        transcribed_text = "The quick brown fox jumps over the lazy dog"
        
        feedback = self.ai_service.get_pronunciation_feedback(
            reference_text, 
            transcribed_text
        )
        
        # Verify feedback is generated
        self.assertIsNotNone(feedback)
        self.assertIsInstance(feedback, str)

    def test_database_operations(self):
        """Test database CRUD operations"""
        # Create a practice text
        practice_text = self.db_service.create_practice_text(
            title="Test Practice Text",
            content="Hello world, this is a test sentence.",
            difficulty_level="beginner",
            category="test"
        )
        
        # Verify text was created
        self.assertIsNotNone(practice_text)
        self.assertIsNotNone(practice_text.id)
        
        # Create a practice session
        practice_session = self.db_service.create_practice_session(
            practice_text_id=practice_text.id,
            audio_file_path="/tmp/test_audio.wav",
            transcribed_text="Hello world",
            pronunciation_score=85.5,
            feedback="Good pronunciation!"
        )
        
        # Verify session was created
        self.assertIsNotNone(practice_session)
        self.assertIsNotNone(practice_session.id)
        
        # Retrieve practice text
        retrieved_text = self.db_service.get_practice_text(practice_text.id)
        self.assertIsNotNone(retrieved_text)
        self.assertEqual(retrieved_text.title, "Test Practice Text")

    def test_integration(self):
        """Test end-to-end integration of services"""
        # Create a practice text
        practice_text = self.db_service.create_practice_text(
            title="Integration Test",
            content="The quick brown fox jumps over the lazy dog.",
            difficulty_level="intermediate",
            category="test"
        )
        
        # Create a test audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Generate a simple test audio signal
            duration = 2  # seconds
            sample_rate = 16000
            audio_data = np.random.normal(0, 0.1, duration * sample_rate)
            
            # Save the audio file
            sf.write(temp_file.name, audio_data, sample_rate)
            
            # Analyze pronunciation
            pronunciation_result = self.speech_service.analyze_pronunciation(
                temp_file.name, 
                practice_text.content
            )
            
            # Generate AI feedback
            feedback = self.ai_service.get_pronunciation_feedback(
                practice_text.content, 
                pronunciation_result.get('transcribed_text', '')
            )
            
            # Create practice session
            practice_session = self.db_service.create_practice_session(
                practice_text_id=practice_text.id,
                audio_file_path=temp_file.name,
                transcribed_text=pronunciation_result.get('transcribed_text', ''),
                pronunciation_score=pronunciation_result.get('pronunciation_score', 0),
                feedback=feedback
            )
            
            # Verify integration
            self.assertIsNotNone(practice_session)
            self.assertEqual(practice_session.practice_text_id, practice_text.id)

    def test_phonetic_guide(self):
        """Test phonetic guide generation"""
        text = "The quick brown fox jumps over the lazy dog."
        
        guide = self.ai_service.get_phonetic_guide(text)
        
        # Verify guide is generated
        self.assertIsNotNone(guide)
        self.assertIsInstance(guide, str)

if __name__ == '__main__':
    unittest.main()
