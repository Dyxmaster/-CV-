# -*- coding: utf-8 -*-

import sys
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("少帅下飞机")
        self.setWindowIcon(QtGui.QIcon('sssfj.ico'))

        # 初始化视频捕获
        self.video_file = 'sssfj.mp4'
        self.cap = cv2.VideoCapture(self.video_file)
        if not self.cap.isOpened():
            print("Error: Could not open video.")
            sys.exit()

        # 获取视频的宽和高
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 其他参数设置
        self.playing = True
        self.playback_speed = 1.0

        # 创建用于显示视频的 QLabel
        self.label = QtWidgets.QLabel(self)
        self.label.setFixedSize(self.video_width, self.video_height)

        # 设置布局
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)

        self.controls_layout = QtWidgets.QHBoxLayout()

        # 暂停按钮
        self.btn_pause = QtWidgets.QPushButton("Pause", self)
        self.btn_pause.clicked.connect(self.toggle_play)
        self.controls_layout.addWidget(self.btn_pause)

        # 播放速度选择器
        self.speed_selector = QtWidgets.QComboBox(self)
        self.speed_selector.addItems(["0.5x", "0.8x", "1.0x", "1.2x", "1.5x", "2.0x", "3.0x"])
        self.speed_selector.currentIndexChanged.connect(self.change_speed)
        self.controls_layout.addWidget(self.speed_selector)

        # 添加控制布局到主布局
        self.layout.addLayout(self.controls_layout)
        self.setLayout(self.layout)

        # 定时器用于更新视频帧
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # 设置窗口大小和位置
        self.setGeometry(100, 100, self.video_width, self.video_height + 50)
        self.show()

    def update_frame(self):
        if self.playing:
            ret, frame = self.cap.read()
            if not ret:
                # 如果视频播放完，重新开始
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

            # 转换为灰度图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 使用 Canny 边缘检测
            edges = cv2.Canny(gray, 50, 150)

            # 将边缘图像扩展到三个通道
            edges_colored = cv2.merge([edges, edges, edges])

            # 生成伪3D效果，应用颜色通道偏移
            shift = 5  # 偏移量，越大越明显
            b, g, r = cv2.split(edges_colored)

            # 对颜色通道进行偏移，模拟3D效果
            M = np.float32([[1, 0, shift], [0, 1, shift]])
            r_shifted = cv2.warpAffine(r, M, (self.video_width, self.video_height))

            M = np.float32([[1, 0, -shift], [0, 1, -shift]])
            b_shifted = cv2.warpAffine(b, M, (self.video_width, self.video_height))

            # 合并偏移后的通道
            pseudo_3d_frame = cv2.merge([b_shifted, g, r_shifted])

            # 将图像转换为 QImage 格式以显示在 QLabel 中
            height, width, channel = pseudo_3d_frame.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(pseudo_3d_frame.data, width, height, bytes_per_line, QtGui.QImage.Format_BGR888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(q_image))

    def toggle_play(self):
        self.playing = not self.playing
        self.btn_pause.setText("Resume" if not self.playing else "Pause")

    def change_speed(self):
        speed_mapping = {
            0: 0.5,
            1: 0.8,
            2: 1.0,
            3: 1.2,
            4: 1.5,
            5: 2.0,
            6: 3.0
        }
        self.playback_speed = speed_mapping[self.speed_selector.currentIndex()]
        self.timer.setInterval(int(30 / self.playback_speed))

    def closeEvent(self, event):
        # 释放视频资源
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    sys.exit(app.exec_())
