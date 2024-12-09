import streamlit as st
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import plotly.graph_objs as go
import threading
import time
import queue

class SimpleAudioRecorder:
    def __init__(self):
        # 录音参数
        self.sample_rate = 44100  # 标准采样率
        self.channels = 1
        self.recording = None
        self.is_recording = False
        self.temp_audio_file = None
        self.max_queue_size = 1000  # 控制显示的采样点数量
        
        # 创建本地队列
        self.waveform_queue = queue.Queue(maxsize=self.max_queue_size)
        
        # 初始化Streamlit状态
        if 'recording_duration' not in st.session_state:
            st.session_state.recording_duration = 0
        if 'waveform_data' not in st.session_state:
            st.session_state.waveform_data = []
        if 'last_update_time' not in st.session_state:
            st.session_state.last_update_time = time.time()
        
        # 录音相关参数
        self.recording_duration = 0
        self.recording_thread = None

    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        self.recording = []
        self.recording_duration = 0
        st.session_state.recording_duration = 0
        st.session_state.waveform_data = []
        st.session_state.last_update_time = time.time()
        
        # 清空之前的波形队列
        while not self.waveform_queue.empty():
            self.waveform_queue.get()
        
        def audio_callback(indata, frames, time, status):
            """录音回调函数"""
            if status:
                print(status)
            self.recording.append(indata.copy())
            
            # 将数据放入波形队列
            try:
                if self.waveform_queue.qsize() >= self.max_queue_size:
                    self.waveform_queue.get()
                self.waveform_queue.put(indata.flatten())
            except Exception as e:
                print(f"Error in audio callback: {e}")
        
        # 开始录音流
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=self.channels,
            callback=audio_callback
        )
        self.stream.start()
        
        st.toast("🎙️ 录音已开始", icon="🔴")

    def stop_recording(self):
        """停止录音"""
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
            
            st.toast("✅ 录音已结束", icon="🟢")
            return audio_data
        
        return None

    def play_recording(self):
        """播放录音"""
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            # 读取音频文件
            data, fs = sf.read(self.temp_audio_file)
            
            # 播放音频
            sd.play(data, fs)
            sd.wait()
            
            st.toast("🔊 播放录音", icon="🎵")
        else:
            st.warning("没有可播放的录音")

def main():
    st.title("🎙️ 实时录音应用")
    
    # 初始化录音器
    if 'recorder' not in st.session_state:
        st.session_state.recorder = SimpleAudioRecorder()
    
    recorder = st.session_state.recorder
    
    # 实时波形图占位符
    waveform_placeholder = st.empty()
    
    # 录音控制列
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 开始录音按钮
        if st.button("🔴 开始录音"):
            recorder.start_recording()
    
    with col2:
        # 停止录音按钮
        if st.button("⏹️ 停止录音"):
            recorder.stop_recording()
    
    with col3:
        # 播放录音按钮
        if st.button("▶️ 播放录音"):
            recorder.play_recording()
    
    # 显示录音状态和时长
    status_col, duration_col = st.columns(2)
    
    with status_col:
        if recorder.is_recording:
            st.write(f"录音状态: {'录音中' if recorder.is_recording else '未录音'}")
            st.write(f"录音时长: {st.session_state.recording_duration:.1f} 秒")
    
    with duration_col:
        pass
    
    # 实时更新录音时长和波形图
    current_time = time.time()
    if recorder.is_recording and current_time - st.session_state.last_update_time >= 0.1:
        # 更新录音时长
        st.session_state.recording_duration += 0.1
        st.session_state.last_update_time = current_time
        
        # 更新波形图
        if not recorder.waveform_queue.empty():
            # 收集最新的波形数据
            latest_data = list(recorder.waveform_queue.queue)
            st.session_state.waveform_data = latest_data
        
        # 创建波形图
        if st.session_state.waveform_data:
            fig = go.Figure(data=go.Scatter(
                y=st.session_state.waveform_data, 
                mode='lines', 
                line=dict(color='blue', width=1)
            ))
            fig.update_layout(
                title='实时声波',
                xaxis_title='采样点',
                yaxis_title='振幅',
                height=300
            )
            
            # 更新波形图
            waveform_placeholder.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
