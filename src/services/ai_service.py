#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openai import OpenAI
import os
from dotenv import load_dotenv
import httpx
import logging
from ..config.i18n import get_text
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

class AIService:
    def __init__(self, http_client=None):
        # If no http_client is provided, create a default one without proxies
        if http_client is None:
            http_client = httpx.Client()
        
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=http_client
        )

    def get_pronunciation_feedback(self, text, recorded_text, language='english', azure_details=None):
        """Get AI feedback on pronunciation using OpenAI
        
        Args:
            text (str): Original text
            recorded_text (str): Transcribed speech text
            language (str): Feedback language ('english' or 'chinese')
            azure_details (dict): Additional pronunciation details from Azure
        """
        try:
            logger.info(f"Generating pronunciation feedback for text length: {len(text)}")
            
            # 根据语言选择系统提示和分析提示
            system_role = {
                'english': "You are an expert English pronunciation coach. Provide feedback in English.",
                'chinese': "你是一位专业的英语发音教练。请用中文提供反馈。"
            }.get(language, "You are an expert English pronunciation coach.")

            analysis_prompt = {
                'english': f"""
                    Compare the original text and the transcribed speech, then provide feedback:
                    Original text: {text}
                    Transcribed speech: {recorded_text}
                    
                    Please analyze:
                    1. Pronunciation accuracy
                    2. Common mistakes
                    3. Specific improvement suggestions
                    4. Phonetic tips for difficult words
                    """,
                'chinese': f"""
                    请对比原文和语音识别结果，并提供发音反馈：
                    原文：{text}
                    识别结果：{recorded_text}
                    
                    请分析以下几点：
                    1. 发音准确度
                    2. 常见错误
                    3. 具体改进建议
                    4. 难词的发音技巧
                    """
            }.get(language, "")

            # 如果有Azure详细信息，添加到提示中
            if azure_details:
                score_info = {
                    'english': f"""
                        Additional pronunciation scores:
                        - Overall pronunciation score: {azure_details.get('pronunciation_score', 'N/A')}
                        - Accuracy score: {azure_details.get('accuracy_score', 'N/A')}
                        - Fluency score: {azure_details.get('fluency_score', 'N/A')}
                        - Completeness score: {azure_details.get('completeness_score', 'N/A')}
                        
                        Please incorporate these scores in your feedback.
                        """,
                    'chinese': f"""
                        额外的发音评分：
                        - 总体发音得分：{azure_details.get('pronunciation_score', 'N/A')}
                        - 准确性得分：{azure_details.get('accuracy_score', 'N/A')}
                        - 流畅度得分：{azure_details.get('fluency_score', 'N/A')}
                        - 完整度得分：{azure_details.get('completeness_score', 'N/A')}
                        
                        请将这些分数纳入你的反馈中。
                        """
                }.get(language, "")
                analysis_prompt += score_info

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            logger.info("Successfully generated AI feedback")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}", exc_info=True)
            error_msg = {
                'english': f"Error generating feedback: {str(e)}",
                'chinese': f"生成反馈时出错：{str(e)}"
            }.get(language, str(e))
            return error_msg

    def get_phonetic_guide(self, text):
        """Get phonetic guidance for the text"""
        try:
            prompt = f"""
            Please provide phonetic guidance for the following text:
            {text}
            
            Focus on:
            1. Stress patterns
            2. Difficult sounds
            3. Word linking
            4. Natural rhythm
            Include IPA symbols where helpful.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in English phonetics and pronunciation."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
             
            return f"Error generating phonetic guide: {str(e)}"

    def get_word_pronunciation_guide(self, word, language='english'):
        """Get pronunciation guide for a specific word
        
        Args:
            word (str): The word to analyze
        """
        try:
            prompt = f"""
            Please provide a detailed pronunciation guide for the word: "{word}"
            
            Include:
            1. IPA transcription
            2. Syllable breakdown
            3. Stress pattern
            4. Common pronunciation mistakes
            5. Similar sounding words
            6. Example sentences
            
            Format the response in markdown.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in English pronunciation and phonetics."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return get_text('guide_error', language, error=str(e))
