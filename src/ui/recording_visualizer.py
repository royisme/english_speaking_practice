import streamlit as st
import plotly.graph_objs as go
import numpy as np
import threading
import time
import logging
import queue

logger = logging.getLogger(__name__)

class RecordingVisualizer:
    def __init__(self, audio_service):
        self.audio_service = audio_service
        self.is_recording = False
        self.data_queue = queue.Queue()
        self.max_duration = 60  # 最大录音时长

    def _update_recording_data(self):
        """
        实时更新录音数据并放入队列
        """
        last_status = None
        while self.is_recording:
            try:
                # 获取当前录音帧
                status = self.audio_service.get_recording_status()
                
                # 检查录音帧是否存在且非空
                if status.get('recorded_frames') and len(status['recorded_frames']) > 0:
                    try:
                        # 尝试合并录音帧
                        current_data = np.concatenate(status['recorded_frames'], axis=0)
                        
                        # 将数据放入队列
                        self.data_queue.put({
                            'data': current_data,
                            'duration': status['current_duration']
                        })
                    except Exception as concat_error:
                        logger.error(f"合并录音帧时出错: {concat_error}")
                        logger.error(f"录音帧详情: {status['recorded_frames']}")
                
                # 仅在状态发生变化时才休眠
                if status != last_status:
                    time.sleep(0.1)  # 控制更新频率
                    last_status = status
            
            except Exception as e:
                logger.error(f"录音数据更新错误: {e}")
                # 短暂休眠防止过快重试
                time.sleep(0.5)

    def start_recording(self):
        """
        开始录音并启动数据更新线程
        """
        # 清空队列
        while not self.data_queue.empty():
            self.data_queue.get()
        
        # 开始录音
        recording_started = self.audio_service.start_recording()
        
        if recording_started:
            self.is_recording = True
            
            # 启动数据更新线程
            threading.Thread(target=self._update_recording_data, daemon=True).start()

    def stop_recording(self):
        """
        停止录音
        """
        self.is_recording = False
        self.audio_service.stop_recording()

    def render(self):
        """
        渲染录音可视化界面
        """
        st.header("🎙️ 录音可视化")

        # 创建两列布局
        col1, col2 = st.columns([3, 1])

        with col1:
            # 声波图表占位符
            waveform_placeholder = st.empty()
        
        with col2:
            # 录音时间占位符
            duration_placeholder = st.empty()

        # 录音控制按钮
        col3, col4 = st.columns(2)
        with col3:
            if st.button("开始录音", key="start_recording_viz"):
                # 重置可视化状态
                if 'recording_viz_running' in st.session_state:
                    del st.session_state['recording_viz_running']
                self.start_recording()
        
        with col4:
            if st.button("停止录音", key="stop_recording_viz"):
                self.stop_recording()

        # 状态显示占位符
        status_placeholder = st.empty()

        # 可视化更新函数
        def visualize_recording():
            try:
                while self.is_recording:
                    try:
                        # 非阻塞获取最新数据
                        if not self.data_queue.empty():
                            latest_data = self.data_queue.get_nowait()
                            
                            # 安全检查数据
                            if latest_data['data'] is not None and len(latest_data['data']) > 0:
                                # 更新声波图
                                fig = go.Figure(data=go.Scatter(
                                    y=latest_data['data'], 
                                    mode='lines', 
                                    line=dict(color='blue', width=1)
                                ))
                                fig.update_layout(
                                    title='实时声波',
                                    xaxis_title='采样点',
                                    yaxis_title='振幅',
                                    height=300
                                )
                                
                                # 更新图表和时间
                                waveform_placeholder.plotly_chart(fig, use_container_width=True)
                                duration_placeholder.metric(
                                    label="录音时长", 
                                    value=f"{latest_data['duration']:.2f} 秒"
                                )
                                
                                # 更新状态
                                status_placeholder.success(f"正在录音... {latest_data['duration']:.2f} 秒")
                        
                        time.sleep(0.5)
                    
                    except queue.Empty:
                        # 队列为空时休眠
                        time.sleep(0.1)
                    
                    except Exception as inner_error:
                        logger.error(f"可视化内部错误: {inner_error}")
                        break
                
                # 录音结束后的清理
                status_placeholder.info("录音已停止")
            
            except Exception as outer_error:
                logger.error(f"可视化主线程错误: {outer_error}")
            
            finally:
                # 确保状态被重置
                st.session_state['recording_viz_running'] = False

        # 启动可视化线程
        if not st.session_state.get('recording_viz_running', False):
            st.session_state['recording_viz_running'] = True
            threading.Thread(target=visualize_recording, daemon=True).start()
