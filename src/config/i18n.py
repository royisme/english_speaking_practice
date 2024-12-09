#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Internationalization configuration for the application.
Provides translations for all user-facing text in multiple languages.
"""

TRANSLATIONS = {
    'english': {
        # common    
        'app_title': "English Speaking Practice Assistant",
        'loading': "Loading...",
        'error': "Error",
        'success': "Success",
        
        # text selection
        'text_selection_title': "📝 Select Practice Text",
        'language_select': "Select Language",
        'text_mode_select': "Select Text Mode",
        'preset_text': "Preset Text",
        'custom_text': "Custom Text",
        'enter_text': "Enter your practice text",
        'confirm_text': "Confirm Text",
        'text_saved': "Custom text saved",
        'invalid_text': "Please enter valid text",
        
        # text study
        'text_study_title': "📖 Text Study",
        'ai_read_text': "🔊 AI Read Text",
        'generating_audio': "Generating audio...",
        'audio_gen_failed': "Audio generation failed",
        'word_guide_title': "Click words for pronunciation guide",
        'pronunciation_guide': "Pronunciation Guide for",
        'play_pronunciation': "🔊 Play Pronunciation",
        'getting_guide': "Getting pronunciation guide...",
        'guide_failed': "Failed to get pronunciation guide",
        
        # recording
        'recording_title': "🎙️ Record Your Speech",
        'start_recording': "🔴 Start Recording",
        'stop_recording': "⏹️ Stop Recording",
        'play_recording': "▶️ Play Recording",
        'recording_progress': "🔴 Recording in progress...",
        'recording_saved': "✅ Recording saved: {duration:.2f} seconds",
        'no_recording': "No recording available",
        'select_text_first': "Please select or enter a practice text first",
        
        # analysis
        'analysis_title': "📊 Pronunciation Analysis",
        'start_analysis': "🔍 Start Analysis",
        'analyzing': "Analyzing pronunciation...",
        'original_text': "Original Text",
        'recognized_text': "Recognized Text",
        'score_details': "Score Details",
        'total_score': "Total Pronunciation Score",
        'accuracy_score': "Accuracy Score",
        'fluency_score': "Fluency Score",
        'completeness_score': "Completeness Score",
        'get_ai_feedback': "🤖 Get AI Feedback",
        'getting_feedback': "Getting AI feedback...",
        'ai_feedback_title': "AI Feedback",
        'retry_analysis': "🔄 Retry Analysis",
        
        # history
        'history_title': "📜 Practice History",
        'practice_time': "Practice Time",
        'score': "Score",
        
        # text content
        'text_content': "Text Content:",
        'difficulty': "Difficulty:",
        'unknown': "Unknown",
        'recording_stopped': "✅ Recording stopped",
        'no_recording_made': "No recording was made",
        'playback_title': "🔊 Recording Playback",
        
        # language selection
        'interface_language': "Interface Language",
        'english_name': "English",
        'chinese_name': "Chinese",
        
        # analysis related
        'analysis_time': "Analysis time: {time:.2f}s",
        'analysis_failed': "Analysis failed: {error}",
        
        # word guide related
        'click_for_guide': "Click for pronunciation guide",
        'word_guide_help': "Click any word to get detailed pronunciation guidance",
        'word_guide_loading': "Loading word guide...",
        
        # error messages
        'tts_error': "Text-to-speech failed: {error}",
        'guide_error': "Failed to get pronunciation guide: {error}",
        'network_error': "Network error: {error}",
        'unknown_error': "An unknown error occurred: {error}",
        
        # status messages
        'processing': "Processing...",
        'completed': "Completed",
        'failed': "Failed",
        
        # language selection
        'language_selector': "Language",
        'switch_language': "Switch language",
        'language_switched': "Language switched to {display_name}",
        
        # difficulty levels
        'difficulty_beginner': "Beginner",
        'difficulty_intermediate': "Intermediate",
        'difficulty_advanced': "Advanced",
        'difficulty_unknown': "Unknown",
        
        # interface hints
        'loading_hint': "Loading...",
        'select_hint': "Select an option",
        'processing_hint': "Processing your request...",
        'success_hint': "Operation completed successfully",
        'error_hint': "An error occurred",
        
        # operation hints
        'click_to_select': "Click to select",
        'click_to_play': "Click to play audio",
        'click_to_stop': "Click to stop",
        'click_for_details': "Click for details",
        
        # App description
        'app_description': """
        Improve your English pronunciation through interactive practice!
        
        ### How to use:
        1. Select or enter practice text
        2. Record your speech
        3. Get instant pronunciation feedback
        """,
        
        # Recording related
        'recording_started': "🎙️ Recording started",
        'playing_audio': "🔊 Playing audio",
        'history_error': "Error getting practice history: {error}",
        
        'speech_rate': "Speech Rate",
        'word_pronunciation': "Word Pronunciation",
        
        # Word study
        'word_ipa': "IPA:",
        'word_syllables': "Syllables:",
        'word_stress': "Stress Pattern:",
        'word_examples': "Example Sentences:",
        'word_similar': "Similar Words:",
        'word_tips': "Pronunciation Tips:",
        
        # Speech control
        'speech_speed_tip': "Adjust reading speed",
        'normal_speed': "Normal",
        'slow_speed': "Slow",
        'fast_speed': "Fast",
        
        # Word selection
        'word_selection_prompt': "Enter a word to get pronunciation guide",
        'word_selection_help': "Type or paste a word from the text above to see its pronunciation guide",
    },
    'chinese': {
        # 通用
        'app_title': "英语口语练习助手",
        'loading': "加载中...",
        'error': "错误",
        'success': "成功",
        
        # 文本选择
        'text_selection_title': "📝 选择练习文本",
        'language_select': "选择语言",
        'text_mode_select': "选择文本方式",
        'preset_text': "预设文本",
        'custom_text': "自定义文本",
        'enter_text': "输入您的练习文本",
        'confirm_text': "确认文本",
        'text_saved': "自定义文本已保存",
        'invalid_text': "请输入有效的文本",
        
        # 文本学习
        'text_study_title': "📖 文本学习",
        'ai_read_text': "🔊 AI朗读全文",
        'generating_audio': "生成语音中...",
        'audio_gen_failed': "生成语音失败",
        'word_guide_title': "点击单词获取发音指导",
        'pronunciation_guide': "发音指导 -",
        'play_pronunciation': "🔊 播放发音",
        'getting_guide': "获取发音指导中...",
        'guide_failed': "获取发音指导失败",
        
        # 录音
        'recording_title': "🎙️ 录音",
        'start_recording': "🔴 开始录音",
        'stop_recording': "⏹️ 停止录音",
        'play_recording': "▶️ 播放录音",
        'recording_progress': "🔴 录音进行中...",
        'recording_saved': "✅ 录音已保存：{duration:.2f} 秒",
        'no_recording': "没有可用的录音",
        'select_text_first': "请先选择或输入练习文本",
        
        # 分析
        'analysis_title': "📊 发音分析",
        'start_analysis': "🔍 开始分析",
        'analyzing': "正在分析发音...",
        'original_text': "原始文本",
        'recognized_text': "识别文本",
        'score_details': "得分详情",
        'total_score': "总发音得分",
        'accuracy_score': "准确性得分",
        'fluency_score': "流畅度得分",
        'completeness_score': "完整度得分",
        'get_ai_feedback': "🤖 获取AI反馈",
        'getting_feedback': "正在获取AI反馈...",
        'ai_feedback_title': "AI反馈建议",
        'retry_analysis': "🔄 重新分析",
        
        # 历史记录
        'history_title': "📜 练习历史",
        'practice_time': "练习时间",
        'score': "得分",
        
        # 文本内容
        'text_content': "文本内容：",
        'difficulty': "难度：",
        'unknown': "未知",
        'recording_stopped': "✅ 录音已停止",
        'no_recording_made': "没有录制到音频",
        'playback_title': "🔊 录音回放",
        
        # 语言选择
        'interface_language': "界面语言",
        'english_name': "英语",
        'chinese_name': "中文",
        
        # 分析相关
        'analysis_time': "分析耗时：{time:.2f}秒",
        'analysis_failed': "分析失败：{error}",
        
        # 单词指导相关
        'click_for_guide': "点击获取发音指导",
        'word_guide_help': "点击任意单词获取详细发音指导",
        'word_guide_loading': "加载单词指导中...",
        
        # 错误信息
        'tts_error': "语音合成失败：{error}",
        'guide_error': "获取发音指导失败：{error}",
        'network_error': "网络错误：{error}",
        'unknown_error': "发生未知错误：{error}",
        
        # 状态信息
        'processing': "处理中...",
        'completed': "已完成",
        'failed': "失败",
        
        # 语言选择
        'language_selector': "语言",
        'switch_language': "切换语言",
        'language_switched': "已切换到{display_name}",
        
        # 难度级别
        'difficulty_beginner': "初级",
        'difficulty_intermediate': "中级",
        'difficulty_advanced': "高级",
        'difficulty_unknown': "未知",
        
        # 界面提示
        'loading_hint': "加载中...",
        'select_hint': "请选择",
        'processing_hint': "正在处理您的请求...",
        'success_hint': "操作成功完成",
        'error_hint': "发生错误",
        
        # 操作提示
        'click_to_select': "点击选择",
        'click_to_play': "点击播放",
        'click_to_stop': "点击停止",
        'click_for_details': "点击查看详情",
        
        # App description
        'app_description': """
        通过交互式练习提高英语发音！
        
        ### 使用方法：
        1. 选择或输入练习文本
        2. 录制您的语音
        3. 获取即时发音反馈
        """,
        
        # Recording related
        'recording_started': "🎙️ 开始录音",
        'playing_audio': "🔊 播放音频",
        'history_error': "获取练习历史出错：{error}",
        
        'speech_rate': "语速",
        'word_pronunciation': "单词发音",
        
        # Word study
        'word_ipa': "国际音标：",
        'word_syllables': "音节划分：",
        'word_stress': "重音模式：",
        'word_examples': "例句：",
        'word_similar': "相似单词：",
        'word_tips': "发音技巧：",
        
        # Speech control
        'speech_speed_tip': "调整朗读速度",
        'normal_speed': "正常",
        'slow_speed': "慢速",
        'fast_speed': "快速",
        
        # Word selection
        'word_selection_prompt': "输入单词获取发音指导",
        'word_selection_help': "输入或粘贴上方文本中的单词以查看其发音指导",
    }
}

def get_text(key: str, language: str = 'english', **kwargs) -> str:
    """Get text for a given language
    
    Args:
        key: Text key
        language: Language code ('english' or 'chinese')
        **kwargs: Formatting parameters
    """
    translations = TRANSLATIONS.get(language, TRANSLATIONS['english'])
    text = translations.get(key, TRANSLATIONS['english'][key])
    
    if kwargs:
        try:
            if 'language' in kwargs:
                del kwargs['language']
            return text.format(**kwargs)
        except:
            return text
    return text 