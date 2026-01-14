import cv2
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from core.detector import SmileDetector
import datetime
import os

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, bool, float)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.detector = SmileDetector()

    def run(self):
        # Capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                # Mirror the frame
                cv_img = cv2.flip(cv_img, 1)
                # Process frame
                processed_img, landmarks, is_smiling, smile_ratio = self.detector.process_frame(cv_img)
                self.change_pixmap_signal.emit(processed_img, is_smiling, smile_ratio)
            else:
                # Handle camera error or end of stream
                pass
        # Shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("人脸笑容识别系统")
        self.resize(1000, 700)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-family: "Microsoft YaHei", "PingFang SC", "Heiti SC", "Arial", sans-serif;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-family: "Microsoft YaHei", "PingFang SC", "Heiti SC", "Arial", sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Video Display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000000; border: 2px solid #444;")
        self.image_label.setMinimumSize(640, 480)
        self.layout.addWidget(self.image_label)

        # Status Display
        self.status_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 等待摄像头启动...")
        self.status_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold)) # PyQt will try to match or fallback
        self.status_layout.addWidget(self.status_label)
        
        self.score_label = QLabel("笑容评分: 0.0")
        self.score_label.setFont(QFont("Microsoft YaHei", 14))
        self.status_layout.addWidget(self.score_label)
        
        self.layout.addLayout(self.status_layout)

        # Controls
        self.controls_layout = QHBoxLayout()
        
        # Camera Button
        self.camera_btn = QPushButton("启动摄像头")
        self.camera_btn.clicked.connect(self.toggle_camera)
        self.controls_layout.addWidget(self.camera_btn)

        # Snapshot Button
        self.snapshot_btn = QPushButton("手动拍照")
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.controls_layout.addWidget(self.snapshot_btn)

        self.layout.addLayout(self.controls_layout)
        
        # Sensitivity Slider
        self.slider_layout = QHBoxLayout()
        self.slider_label = QLabel("灵敏度调节:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(30)
        self.slider.setMaximum(70)
        self.slider.setValue(48) # Default 4.8 * 10
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.update_sensitivity)
        
        self.slider_layout.addWidget(self.slider_label)
        self.slider_layout.addWidget(self.slider)
        self.layout.addLayout(self.slider_layout)

        # Threading
        self.thread = None
        self.current_frame = None
        self.is_camera_active = False
        self.sensitivity_threshold = 4.8

    def toggle_camera(self):
        if not self.is_camera_active:
            self.thread = VideoThread()
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.start()
            self.camera_btn.setText("关闭摄像头")
            self.camera_btn.setStyleSheet("background-color: #dc3545;")
            self.is_camera_active = True
        else:
            self.thread.stop()
            self.camera_btn.setText("启动摄像头")
            self.camera_btn.setStyleSheet("background-color: #0d6efd;")
            self.image_label.clear()
            self.status_label.setText("状态: 摄像头已关闭")
            self.is_camera_active = False

    def update_image(self, cv_img, is_smiling, smile_ratio):
        self.current_frame = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

        # Update Status
        # Check against dynamic threshold from slider
        if smile_ratio > self.sensitivity_threshold:
            self.status_label.setText("状态: 😄 检测到笑容!")
            self.status_label.setStyleSheet("color: #28a745;") # Green
        else:
            self.status_label.setText("状态: 😐 未检测到笑容")
            self.status_label.setStyleSheet("color: #ffffff;") # White
            
        self.score_label.setText(f"笑容评分: {smile_ratio:.2f} (阈值: {self.sensitivity_threshold:.1f})")

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def update_sensitivity(self, value):
        self.sensitivity_threshold = value / 10.0
        
    def take_snapshot(self):
        if self.current_frame is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            QMessageBox.information(self, "拍照成功", f"照片已保存为 {filename}")
        else:
            QMessageBox.warning(self, "错误", "摄像头未启动或无图像")

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        event.accept()
