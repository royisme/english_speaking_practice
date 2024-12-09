#!/usr/bin/env python
# -*- coding: utf-8 -*-

# src/services/speech_service.py
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
from typing import Dict
import logging
from ..config.i18n import get_text

logger = logging.getLogger(__name__)

load_dotenv()

class SpeechService:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv('AZURE_SPEECH_KEY'),
            region=os.getenv('AZURE_SPEECH_REGION')
        )

    def analyze_pronunciation(self, audio_file: str, reference_text: str) -> Dict[str, float]:
        """Comprehensive pronunciation analysis using Azure Speech Services"""
        try:
            logger.info(f"Starting pronunciation analysis for text length: {len(reference_text)}")
            
            audio_config = speechsdk.AudioConfig(filename=audio_file)
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme
            )
            
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            pronunciation_config.apply_to(speech_recognizer)
            
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
                logger.info("Pronunciation analysis completed successfully")
                
                return {
                    'transcribed_text': result.text,
                    'accuracy_score': pronunciation_result.accuracy_score,
                    'fluency_score': pronunciation_result.fluency_score,
                    'completeness_score': pronunciation_result.completeness_score,
                    'pronunciation_score': pronunciation_result.pronunciation_score
                }
            else:
                logger.error(f"Speech recognition failed with reason: {result.reason}")
                return {
                    'transcribed_text': '',
                    'accuracy_score': 0,
                    'fluency_score': 0,
                    'completeness_score': 0,
                    'pronunciation_score': 0
                }
        except Exception as e:
            logger.error(f"Error in pronunciation analysis: {str(e)}", exc_info=True)
            raise

    def start_real_time_pronunciation_assessment(self, reference_text: str, on_result_callback=None):
        """
        Start real-time pronunciation assessment
        
        Args:
            reference_text (str): Text to compare against
            on_result_callback (callable, optional): Callback function for real-time results
        
        Returns:
            A speech recognizer configured for real-time pronunciation assessment
        """
        # Configure pronunciation assessment
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Word
        )
        
        # Use default microphone for real-time input
        audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Apply pronunciation assessment
        pronunciation_config.apply_to(speech_recognizer)
        
        # Define event handlers
        def recognized(evt):
            result = evt.result
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
                
                assessment_data = {
                    'transcribed_text': result.text,
                    'accuracy_score': pronunciation_result.accuracy_score,
                    'fluency_score': pronunciation_result.fluency_score,
                    'completeness_score': pronunciation_result.completeness_score,
                    'pronunciation_score': pronunciation_result.pronunciation_score
                }
                
                if on_result_callback:
                    on_result_callback(assessment_data)
        
        def session_stopped(evt):
            print("Session stopped.")
            speech_recognizer.stop_continuous_recognition()
        
        def error(evt):
            print(f"Error occurred: {evt}")
        
        # Connect events
        speech_recognizer.recognized.connect(recognized)
        speech_recognizer.session_stopped.connect(session_stopped)
        speech_recognizer.canceled.connect(error)
        
        # Start continuous recognition
        speech_recognizer.start_continuous_recognition()
        
        return speech_recognizer

    def text_to_speech(self, text, language='english', speed=1.0):
        """Convert text to speech using Azure TTS
        
        Args:
            text: Text to convert to speech
            language: Language code ('english' or 'chinese')
            speed: Speech rate (0.5 to 2.0)
        """
        try:
            speech_config = self.speech_config
            
            # Set voice based on language
            if language == 'english':
                voice_name = "en-US-JennyNeural"
                lang_code = "en-US"
            else:
                voice_name = "zh-CN-XiaoxiaoNeural"
                lang_code = "zh-CN"
            
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Create SSML with rate and pitch adjustment
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang_code}">
                <voice name="{voice_name}">
                    <prosody rate="{speed:.0%}" pitch="0%">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Use memory stream
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            
            # Use SSML for speech synthesis
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                logger.error(f"Speech synthesis failed: {result.reason}")
                return None
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise Exception(get_text('tts_error', language, error=str(e)))
