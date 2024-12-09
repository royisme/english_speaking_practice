#!/usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import time
import queue
import logging

from src.services import SpeechService, AIService, DBService
from src.ui import (
    TextInputComponent, 
    AnalysisComponent, 
    PlaybackComponent,
    PracticeHistoryComponent,
    TextGuidanceComponent
)
from src.models.base import init_db
from src.config.i18n import get_text

logger = logging.getLogger(__name__)

class SimpleAudioRecorder:
    def __init__(self):
        # Recording parameters
        self.sample_rate = 44100  # Standard sampling rate
        self.channels = 1
        self.recording = None
        self.is_recording = False
        self.temp_audio_file = None
        
        # Initialize Streamlit state
        if 'recording_duration' not in st.session_state:
            st.session_state.recording_duration = 0
        if 'last_update_time' not in st.session_state:
            st.session_state.last_update_time = time.time()
        
        # Recording related parameters
        self.recording_duration = 0
        self.recording_thread = None

    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.recording = []
        self.recording_duration = 0
        st.session_state.recording_duration = 0
        st.session_state.last_update_time = time.time()
        
        def audio_callback(indata, frames, time, status):
            """Recording callback function"""
            if status:
                print(status)
            self.recording.append(indata.copy())
        
        # Start recording stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=self.channels,
            callback=audio_callback
        )
        self.stream.start()
        
        current_language = st.session_state.get('language', 'english')
        st.toast(get_text('recording_started', current_language), icon="🔴")

    def stop_recording(self):
        """Stop recording and save file"""
        if not self.is_recording:
            return None
        
        # Stop recording stream
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        self.is_recording = False
        
        # Merge recording data
        if self.recording:
            audio_data = np.concatenate(self.recording, axis=0)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                self.temp_audio_file = temp_file.name
                sf.write(self.temp_audio_file, audio_data, self.sample_rate)
            
            current_language = st.session_state.get('language', 'english')
            st.toast(get_text('recording_stopped', current_language), icon="🟢")
            return self.temp_audio_file
        
        return None

    def play_recording(self):
        """Play recording"""
        current_language = st.session_state.get('language', 'english')
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            # Read audio file
            data, fs = sf.read(self.temp_audio_file)
            
            # Play audio
            sd.play(data, fs)
            sd.wait()
            
            st.toast(get_text('playing_audio', current_language), icon="🎵")
        else:
            st.warning(get_text('no_recording', current_language))

class EnglishPracticeApp:
    def __init__(self):
        # Initialize services
        self.speech_service = SpeechService()
        self.ai_service = AIService()
        self.db_service = DBService()
        
        # Initialize recorder
        if 'recorder' not in st.session_state:
            st.session_state.recorder = SimpleAudioRecorder()
        
        # Initialize session state
        self._initialize_session_state()
        
    def _initialize_session_state(self):
        """Ensure all necessary session state keys are initialized"""
        default_keys = {
            'practice_text': '',
            'current_text_id': None,
            'audio_file': None,
            'audio_duration': 0,
            'transcribed_text': '',
            'pronunciation_score': 0,
            'feedback': '',
            'practice_history': [],
            'text_input_disabled': False,
            'language': 'english'  # Default language is English
        }
        
        for key, default_value in default_keys.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    def handle_recording_component(self):
        """Recording component"""
        current_language = st.session_state.get('language', 'english')
        st.subheader(get_text('recording_title', current_language))
        
        recorder = st.session_state.recorder
        
        # Recording control columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Start recording button
            if st.button(get_text('start_recording', current_language), 
                        disabled=not st.session_state.get('practice_text') or 
                        st.session_state.get('is_recording', False)):
                if st.session_state.get('practice_text'):
                    recorder.start_recording()
                    st.session_state['is_recording'] = True
                    st.session_state['text_input_disabled'] = True
        
        with col2:
            # Stop recording button
            if st.button(get_text('stop_recording', current_language), 
                        disabled=not st.session_state.get('is_recording', False)):
                audio_file = recorder.stop_recording()
                
                if audio_file:
                    st.session_state['audio_file'] = audio_file
                    st.session_state['audio_duration'] = len(sf.read(audio_file)[0]) / recorder.sample_rate
                    st.session_state['is_recording'] = False
                    st.session_state['text_input_disabled'] = False
                else:
                    st.warning(get_text('no_recording_made', current_language))
        
        # Display recording status
        if st.session_state.get('is_recording', False):
            st.info(get_text('recording_progress', current_language))
        elif st.session_state.get('audio_file'):
            st.success(get_text('recording_saved', current_language, 
                              duration=st.session_state.get('audio_duration', 0)))

    def handle_analysis(self):
        """Analyze recording"""
        if not st.session_state.get('audio_file'):
            return None, None, None
        
        try:
            # Use speech service to analyze pronunciation
            pronunciation_result = self.speech_service.analyze_pronunciation(
                st.session_state['audio_file'], 
                st.session_state.get('practice_text', '')
            )
            
            # Extract analysis results
            transcribed_text = pronunciation_result.get('transcribed_text', '')
            pronunciation_score = pronunciation_result.get('pronunciation_score', 0)
            
            # Get AI feedback
            feedback = self.ai_service.get_pronunciation_feedback(
                st.session_state.get('practice_text', ''),
                transcribed_text,
                language=st.session_state.get('language', 'english')
            )
            
            # Update session state
            st.session_state['transcribed_text'] = transcribed_text
            st.session_state['pronunciation_score'] = pronunciation_score
            st.session_state['feedback'] = feedback
            
            # Save practice record
            if st.session_state.get('current_text_id'):
                self.db_service.create_practice_session(
                    practice_text_id=st.session_state['current_text_id'],
                    audio_file_path=st.session_state['audio_file'],
                    transcribed_text=transcribed_text,
                    pronunciation_score=pronunciation_score,
                    feedback=feedback
                )
            
            return transcribed_text, feedback, pronunciation_result
        
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return None, None, None

    def show_practice_history(self, text_id):
        """Show practice history"""
        try:
            history = self.db_service.get_practice_history(text_id)
            st.session_state['practice_history'] = history
            return history
        except Exception as e:
            current_language = st.session_state.get('language', 'english')
            st.error(get_text('history_error', current_language, error=str(e)))
            return []

    def render(self):
        current_language = st.session_state.get('language', 'english')
        
        # Language selector in sidebar
        with st.sidebar:
            language_options = {
                'english': "English",
                'chinese': "中文"
            }
            
            selected_language = st.selectbox(
                get_text('language_select', language=current_language),
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                index=0 if current_language == 'english' else 1,
                key="language_selector"
            )
            
            if selected_language != current_language:
                st.session_state['language'] = selected_language
                st.toast(
                    get_text(
                        'language_switched',
                        language=selected_language,
                        display_name=language_options[selected_language]
                    )
                )
                st.rerun()
        

def main():
    # Initialize database
    init_db()
    
    # Set page config
    st.set_page_config(
        page_title=get_text('app_title', st.session_state.get('language', 'english')), 
        page_icon="🗣️", 
        layout="wide",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': get_text('app_description', st.session_state.get('language', 'english'))
        }
    )
    
    # Initialize app
    app = EnglishPracticeApp()
    
    # Render app (this will show the sidebar with language selector)
    app.render()
    
    current_language = st.session_state.get('language', 'english')
    
    # Title and description
    st.title(get_text('app_title', current_language))
    st.markdown(get_text('app_description', current_language))
    
    # Create and render components
    text_input_component = TextInputComponent(app)
    text_guidance_component = TextGuidanceComponent(app)
    analysis_component = AnalysisComponent(app)
    playback_component = PlaybackComponent(app)
    practice_history_component = PracticeHistoryComponent(app)
    
    text_input_component.render()
    
    if st.session_state.get('practice_text'):
        text_guidance_component.render()
        app.handle_recording_component()
        analysis_component.render()
        playback_component.render()
        practice_history_component.render()

if __name__ == "__main__":
    main()
