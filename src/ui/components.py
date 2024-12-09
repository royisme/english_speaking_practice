#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if no handlers exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

import streamlit as st
import time
import numpy as np
import queue
from src.config.i18n import get_text

class TextInputComponent:
    def __init__(self, app):
        self.app = app

    def render(self):
        current_language = st.session_state.get('language', 'english')
        st.subheader(get_text('text_selection_title', current_language))
        
        # Check if text input is disabled
        disabled = st.session_state.get('text_input_disabled', False)
        
        # Text selection mode
        text_mode = st.radio(
            get_text('text_mode_select', current_language), 
            [
                get_text('preset_text', current_language),
                get_text('custom_text', current_language)
            ], 
            disabled=disabled
        )
        
        if text_mode == get_text('preset_text', current_language):
            # Get preset text list
            preset_texts = self.app.db_service.get_preset_texts()
            
            # Text selection dropdown
            selected_text_id = st.selectbox(
                get_text('text_selection_title', current_language), 
                options=[text['id'] for text in preset_texts],
                format_func=lambda x: next(text['content'] for text in preset_texts if text['id'] == x),
                disabled=disabled
            )
            
            # Display selected text details
            if selected_text_id:
                selected_text = next(text for text in preset_texts if text['id'] == selected_text_id)
                st.session_state['practice_text'] = selected_text['content']
                st.session_state['current_text_id'] = selected_text_id
                
                st.markdown(f"**{get_text('text_content', current_language)}**\n{selected_text['content']}")
                st.markdown(f"**{get_text('difficulty', current_language)}** {selected_text.get('difficulty', get_text('unknown', current_language))}")
        
        else:
            # Custom text input
            custom_text = st.text_area(
                get_text('enter_text', current_language), 
                height=200, 
                disabled=disabled
            )
            
            if st.button(get_text('confirm_text', current_language), disabled=disabled):
                if custom_text and len(custom_text.strip()) > 0:
                    st.session_state['practice_text'] = custom_text
                    st.session_state['current_text_id'] = None
                    st.success(get_text('text_saved', current_language))
                else:
                    st.warning(get_text('invalid_text', current_language))

class RecordingComponent:
    def __init__(self, app):
        self.app = app
        self.audio_service = app.audio_service

    def render(self):
        current_language = st.session_state.get('language', 'english')
        
        st.subheader(get_text('recording_title', current_language))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(get_text('start_recording', current_language)):
                if not st.session_state.get('practice_text'):
                    st.error(get_text('select_text_first', current_language))
                else:
                    recording_result = self.audio_service.start_recording()
                    if recording_result:
                        st.session_state['is_recording'] = True
                        # 重置分析相关的状态
                        st.session_state['analysis_completed'] = False
                        st.session_state['pronunciation_result'] = None
                        st.session_state['ai_feedback'] = None
                        st.toast("🎙️ Recording started", icon="🔴")
        
        with col2:
            # Stop Recording Button
            if st.button(get_text('stop_recording', current_language)):
                # Stop recording and save file
                audio_file = self.audio_service.stop_recording()
                
                if audio_file:
                    # Update session state
                    st.session_state['audio_file'] = audio_file
                    st.session_state['audio_duration'] = self.audio_service.get_recording_duration()
                    st.session_state['is_recording'] = False
                    
                    st.toast(get_text('recording_stopped', current_language), icon="🟢")
                else:
                    st.warning(get_text('no_recording_made', current_language))
        
        with col3:
            # Play Recording Button
            if st.button(get_text('play_recording', current_language)):
                if st.session_state.get('audio_file'):
                    self.audio_service.play_recording()
                else:
                    st.warning(get_text('no_recording', current_language))
        
        # Display recording status
        if st.session_state.get('is_recording', False):
            st.info(get_text('recording_progress', current_language))
        elif st.session_state.get('audio_file'):
            st.success(get_text('recording_saved', current_language, 
                              duration=st.session_state.get('audio_duration', 0)))

class AnalysisComponent:
    def __init__(self, app):
        self.app = app
        self.analysis_start_time = None

    def render(self):
        current_language = st.session_state.get('language', 'english')
        
        st.subheader(get_text('analysis_title', current_language))
        
        if not st.session_state.get('audio_file'):
            st.info(get_text('no_recording', current_language))
            return

        # Initialize session state variables
        if 'pronunciation_result' not in st.session_state:
            st.session_state.pronunciation_result = None
        if 'ai_feedback' not in st.session_state:
            st.session_state.ai_feedback = None
        if 'analysis_completed' not in st.session_state:
            st.session_state.analysis_completed = False
        if 'analysis_error' not in st.session_state:
            st.session_state.analysis_error = False

        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Only show analysis button if not completed or error occurred
            if not st.session_state.analysis_completed or st.session_state.analysis_error:
                if st.button(get_text('start_analysis', current_language)):
                    with st.spinner(get_text('analyzing', current_language)):
                        logger.info("Starting pronunciation analysis...")
                        self.analysis_start_time = time.time()
                        
                        try:
                            practice_text = st.session_state.get('practice_text', '')
                            audio_file = st.session_state.get('audio_file')
                            
                            logger.info(f"Calling Azure Speech assessment, text length: {len(practice_text)}")
                            st.session_state.pronunciation_result = self.app.speech_service.analyze_pronunciation(
                                audio_file, 
                                practice_text
                            )
                            logger.info("Azure Speech assessment completed")
                            
                            st.session_state.analysis_completed = True
                            st.session_state.analysis_error = False
                        except Exception as e:
                            error_msg = get_text('unknown_error', current_language, error=str(e))
                            logger.error(error_msg)
                            st.error(error_msg)
                            st.session_state.analysis_error = True
        
        with col2:
            if self.analysis_start_time:
                st.write(get_text('analysis_time', current_language, 
                    time=time.time() - self.analysis_start_time))

        # Display analysis results
        if st.session_state.analysis_completed and st.session_state.pronunciation_result:
            st.markdown(f"### {get_text('recognized_text', current_language)}")
            st.text(st.session_state.pronunciation_result.get('transcribed_text', ''))
            
            st.markdown(f"### {get_text('score_details', current_language)}")
            
            score_metrics = [
                ('pronunciation_score', get_text('total_score', current_language)),
                ('accuracy_score', get_text('accuracy_score', current_language)),
                ('fluency_score', get_text('fluency_score', current_language)),
                ('completeness_score', get_text('completeness_score', current_language))
            ]
            
            for metric_key, metric_name in score_metrics:
                score = st.session_state.pronunciation_result.get(metric_key, 0)
                st.markdown(f"#### {metric_name}: {score:.2f}/100")
                st.progress(score / 100)
            
            # AI feedback button
            if st.button(get_text('get_ai_feedback', current_language)):
                with st.spinner(get_text('getting_feedback', current_language)):
                    try:
                        logger.info(f"Preparing AI service call, text length: {len(st.session_state.get('practice_text', ''))}")
                        logger.info(f"Recognized text length: {len(st.session_state.pronunciation_result.get('transcribed_text', ''))}")
                        
                        st.session_state.ai_feedback = self.app.ai_service.get_pronunciation_feedback(
                            st.session_state.get('practice_text', ''),
                            st.session_state.pronunciation_result.get('transcribed_text', ''),
                            language=st.session_state.get('language', 'english'),
                            azure_details=st.session_state.pronunciation_result
                        )
                        
                        logger.info(f"AI feedback received, length: {len(st.session_state.ai_feedback)}")
                        logger.info(f"AI feedback preview: {st.session_state.ai_feedback[:100]}...")
                        
                        # Add success message
                        st.success(get_text('completed', current_language))
                    except Exception as e:
                        error_msg = get_text('unknown_error', current_language, error=str(e))
                        logger.error(error_msg)
                        st.error(error_msg)
            
            # Display AI feedback
            if st.session_state.ai_feedback:
                st.markdown(f"### {get_text('ai_feedback_title', current_language)}")
                st.info(st.session_state.ai_feedback)
                logger.info("AI feedback display completed")

        # Only show retry button if analysis failed
        if st.session_state.get('analysis_error'):
            if st.button(get_text('retry_analysis', current_language)):
                logger.info("Resetting analysis state...")
                st.session_state.analysis_completed = False
                st.session_state.pronunciation_result = None
                st.session_state.ai_feedback = None
                st.session_state.analysis_error = False
                self.analysis_start_time = None

class PlaybackComponent:
    def __init__(self, app):
        self.app = app

    def render(self):
        # Check if audio file exists
        audio_file = st.session_state.get('audio_file')
        if not audio_file:
            return

        st.subheader(get_text('playback_title', st.session_state.get('language', 'english')))
        
        # Play audio file
        with open(audio_file, 'rb') as audio_bytes:
            st.audio(audio_bytes.read(), format='audio/wav')

class PracticeHistoryComponent:
    def __init__(self, app):
        self.app = app

    def render(self):
        current_language = st.session_state.get('language', 'english')
        st.subheader(get_text('history_title', current_language))
        
        # Get current text ID
        current_text_id = st.session_state.get('current_text_id')
        if not current_text_id:
            return

        # Get practice history
        practice_history = self.app.show_practice_history(current_text_id)
        
        if practice_history:
            for session in practice_history:
                st.markdown(f"**{get_text('practice_time', current_language)}** {session.created_at}")
                st.markdown(f"**{get_text('score', current_language)}** {session.pronunciation_score}")
                st.markdown("---")

class TextGuidanceComponent:
    def __init__(self, app):
        self.app = app

    def render(self):
        current_language = st.session_state.get('language', 'english')
        
        if not st.session_state.get('practice_text'):
            return

        st.subheader(get_text('text_study_title', current_language))
        
        # AI Reading section with speed control
        col1, col2 = st.columns([3, 1])
        
        # Store speech rate in session state
        if 'speech_rate' not in st.session_state:
            st.session_state.speech_rate = 1.0
            
        with col2:
            # Speech rate adjustment
            st.session_state.speech_rate = st.slider(
                get_text('speech_rate', current_language),
                min_value=-2.0,
                max_value=2.0,
                value=st.session_state.speech_rate,
                step=0.1,
                key='speech_rate_slider'
            )
        
        with col1:
            if st.button(get_text('ai_read_text', current_language), use_container_width=False):
                with st.spinner(get_text('generating_audio', current_language)):
                    try:
                        audio_data = self.app.speech_service.text_to_speech(
                            st.session_state.get('practice_text', ''),
                            language='english',
                            speed=st.session_state.speech_rate
                        )
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
                    except Exception as e:
                        st.error(get_text('audio_gen_failed', current_language))
                        logger.error(f"Audio generation failed: {str(e)}")

        # Display text content
        st.markdown("### " + get_text('text_content', current_language))
        
        # Display the text
        text = st.session_state.get('practice_text', '')
        st.markdown(text)
        
        # Word selection input
        selected_word = st.text_input(
            get_text('word_selection_prompt', current_language),
            key="word_input",
            help=get_text('word_selection_help', current_language)
        )
        
        # Show pronunciation guide for selected word
        if selected_word:
            with st.expander(
                f"'{selected_word}' " + get_text('pronunciation_guide', current_language),
                expanded=True
            ):
                try:
                    with st.spinner(get_text('getting_guide', current_language)):
                        # Get pronunciation guide
                        guide = self.app.ai_service.get_word_pronunciation_guide(
                            selected_word,
                            language=current_language
                        )
                        
                        # Display guide
                        st.markdown(guide)
                        
                        # Add pronunciation playback button
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if st.button(
                                get_text('play_pronunciation', current_language),
                                key=f"play_{selected_word}"
                            ):
                                audio_data = self.app.speech_service.text_to_speech(
                                    selected_word,
                                    language='english',
                                    speed=1.0
                                )
                                if audio_data:
                                    st.audio(audio_data, format='audio/wav')
                except Exception as e:
                    st.error(get_text('guide_failed', current_language))
                    logger.error(f"Guide generation failed: {str(e)}")

class App:
    def __init__(self, db_service, speech_service, ai_service, audio_service):
        self.db_service = db_service
        self.speech_service = speech_service
        self.ai_service = ai_service
        self.audio_service = audio_service

    def render(self):
        # Add custom CSS for language selector
        st.markdown("""
            <style>
            div[data-testid="stSelectbox"] > label {
                display: none !important;
            }
            div[data-testid="stSelectbox"] {
                min-width: 100px;
                max-width: 150px;
            }
            .stApp header {
                background-color: transparent;
            }
            </style>
        """, unsafe_allow_html=True)
        
        current_language = st.session_state.get('language', 'english')
        
        # Create top bar with language selector
        with st.container():
            # Empty column for spacing
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col3:
                language_options = {
                    'english': "English",
                    'chinese': "中文"
                }
                
                selected_language = st.selectbox(
                    label="Language",  # This will be hidden by CSS
                    options=list(language_options.keys()),
                    format_func=lambda x: language_options[x],
                    index=0 if current_language == 'english' else 1,
                    key="language_selector"
                )
                
                if selected_language != current_language:
                    st.session_state['language'] = selected_language
                    st.toast(get_text('language_switched', selected_language, 
                        language=language_options[selected_language]))
                    st.rerun()
        
        # Main content
        st.title(get_text('app_title', current_language))
        st.markdown(get_text('app_description', current_language))
        
        # Components
        text_input = TextInputComponent(self)
        text_input.render()
        
        if st.session_state.get('practice_text'):
            st.session_state['text_input_disabled'] = True
            TextGuidanceComponent(self).render()
            RecordingComponent(self).render()
            PlaybackComponent(self).render()
            AnalysisComponent(self).render()
            
            if st.session_state.get('current_text_id'):
                PracticeHistoryComponent(self).render()
