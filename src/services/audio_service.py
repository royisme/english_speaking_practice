import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import time
import azure.cognitiveservices.speech as speechsdk

class AudioService:
    def __init__(self, 
                 sample_rate=44100, 
                 channels=1, 
                 max_duration=120, 
                 input_device=None):
        """
        初始化音频服务
        
        参数:
        - sample_rate: 采样率，默认44100Hz
        - channels: 声道数，默认单声道
        - max_duration: 最大录音时长（秒），默认120秒
        - input_device: 输入设备，默认None（自动选择）
        """
        # 录音参数
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = None
        self.is_recording = False
        self.temp_audio_file = None

        # 录音相关参数
        self.recording_duration = 0

        # Azure Speech 配置
        speech_key = os.getenv('AZURE_SPEECH_KEY')
        service_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        self.speech_config.speech_recognition_language = "zh-CN"  # 默认语言

    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        self.recording = []
        self.recording_duration = 0
        
        def audio_callback(indata, frames, time, status):
            """录音回调函数"""
            if status:
                print(status)
            self.recording.append(indata.copy())
        
        # 开始录音流
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=self.channels,
            callback=audio_callback
        )
        self.stream.start()
        
        return True

    def stop_recording(self):
        """停止录音并保存文件"""
        if not self.is_recording:
            return None
        
        # 停止录音流
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        self.is_recording = False
        
        # 合并录音数据
        if self.recording:
            audio_data = np.concatenate(self.recording, axis=0)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                self.temp_audio_file = temp_file.name
                sf.write(self.temp_audio_file, audio_data, self.sample_rate)
            
            return self.temp_audio_file
        
        return None

    def play_recording(self):
        """播放录音"""
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            # 读取音频文件
            data, fs = sf.read(self.temp_audio_file)
            
            # 播放音频
            sd.play(data, fs)
            sd.wait()
            
            return True
        return False

    def get_recording_duration(self):
        """获取录音时长"""
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            data, fs = sf.read(self.temp_audio_file)
            return len(data) / fs
        return 0

    def analyze_pronunciation(self, audio_file, reference_text):
        """
        使用Azure Speech服务评估发音
        
        :param audio_file: 录音文件路径
        :param reference_text: 参考文本
        :return: 发音评估结果字典
        """
        try:
            # 配置发音评估
            audio_config = speechsdk.AudioConfig(filename=audio_file)
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme
            )
            
            # 创建语音识别器
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            # 应用发音评估配置
            pronunciation_config.apply_to(speech_recognizer)
            
            # 识别
            result = speech_recognizer.recognize_once()
            
            # 处理结果
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
                
                return {
                    'transcribed_text': result.text,
                    'pronunciation_score': pronunciation_result.pronunciation_score,
                    'accuracy_score': pronunciation_result.accuracy_score,
                    'fluency_score': pronunciation_result.fluency_score,
                    'completeness_score': pronunciation_result.completeness_score,
                    'detailed_result': pronunciation_result.json
                }
            
            return {
                'transcribed_text': '',
                'pronunciation_score': 0,
                'error': result.reason
            }
        
        except Exception as e:
            return {
                'transcribed_text': '',
                'pronunciation_score': 0,
                'error': str(e)
            }

    def cleanup(self):
        """清理临时文件"""
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            os.unlink(self.temp_audio_file)
            self.temp_audio_file = None