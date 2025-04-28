import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QComboBox, QSlider, QHBoxLayout, QProgressBar, QTextEdit, QSpinBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRunnable, QThreadPool, QObject
import os
import subprocess
import multiprocessing # Needed for thread count default

# Assuming ImageProcessingTask and WorkerSignals will be imported from processing.py
# Assuming find_rimage will be imported from utils.py

class RimageGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # Initialize thread pool here or when starting processing
        self.thread_pool = QThreadPool.globalInstance()


    def initUI(self):
        self.setWindowTitle('Rimage Batch Processor')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Input Path
        input_layout = QHBoxLayout()
        self.input_label = QLabel('图片路径：')
        self.input_line = QLineEdit()
        self.input_button = QPushButton('浏览...')
        # Connect browse_input later in main.py or pass handler
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出目录：')
        self.output_line = QLineEdit()
        self.output_button = QPushButton('浏览...')
        # Connect browse_output later in main.py or pass handler
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)

        # Output Format
        format_layout = QHBoxLayout()
        self.format_label = QLabel('输出格式：')
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png", "oxipng", "jpeg_xl", "webp", "avif"])
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Output Quality
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel('输出质量 (1-100):')
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(85) # Default quality
        self.quality_slider.setTickPosition(QSlider.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_value_label = QLabel(str(self.quality_slider.value()))
        self.quality_slider.valueChanged.connect(lambda value: self.quality_value_label.setText(str(value)))
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value_label)
        layout.addLayout(quality_layout)

        # Resolution Ratio
        ratio_layout = QHBoxLayout()
        self.ratio_label = QLabel('分辨率比例 (%):')
        self.ratio_slider = QSlider(Qt.Horizontal)
        self.ratio_slider.setMinimum(1)
        self.ratio_slider.setMaximum(200) # Allow scaling up to 200%
        self.ratio_slider.setValue(100) # Default 100%
        self.ratio_slider.setTickPosition(QSlider.TicksBelow)
        self.ratio_slider.setTickInterval(10)
        self.ratio_value_label = QLabel(str(self.ratio_slider.value()))
        self.ratio_slider.valueChanged.connect(lambda value: self.ratio_value_label.setText(str(value)))
        ratio_layout.addWidget(self.ratio_label)
        ratio_layout.addWidget(self.ratio_slider)
        ratio_layout.addWidget(self.ratio_value_label)
        layout.addLayout(ratio_layout)

        # Thread Count
        thread_layout = QHBoxLayout()
        self.thread_label = QLabel('最大线程数：')
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setMinimum(1)
        # Set default to CPU count, max to CPU count * 2 (adjust as needed)
        default_threads = multiprocessing.cpu_count()
        self.thread_spinbox.setValue(default_threads)
        self.thread_spinbox.setMaximum(default_threads * 2 if default_threads > 0 else 10) # Prevent 0 or negative, set a reasonable max
        thread_layout.addWidget(self.thread_label)
        thread_layout.addWidget(self.thread_spinbox)
        layout.addLayout(thread_layout)

        # Process Button
        self.process_button = QPushButton('开始处理')
        # Connect start_processing later in main.py or pass handler
        layout.addWidget(self.process_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Message Log
        self.message_log = QTextEdit()
        self.message_log.setReadOnly(True)
        layout.addWidget(self.message_log)

        self.setLayout(layout)

    # browse_input and browse_output will be implemented outside this class,
    # likely in the main application logic, and connected to the buttons.
    # start_processing will also be implemented outside and connected.

    # Placeholder methods for connections
    def connect_browse_input(self, handler):
        self.input_button.clicked.connect(handler)

    def connect_browse_output(self, handler):
        self.output_button.clicked.connect(handler)

    def connect_start_processing(self, handler):
        self.process_button.clicked.connect(handler)

    def append_message(self, message):
        self.message_log.append(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def set_process_button_enabled(self, enabled):
        self.process_button.setEnabled(enabled)

    # closeEvent will be handled in the main application class
