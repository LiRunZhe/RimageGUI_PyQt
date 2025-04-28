import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QThreadPool, QObject
import os
import subprocess
import multiprocessing

from gui import RimageGUI
from processing import ImageProcessingTask, WorkerSignals
from utils import find_rimage # Assuming find_rimage is moved to utils.py

# Main application logic
class Application(QObject):
    def __init__(self):
        super().__init__()
        self.gui = RimageGUI()
        self.gui.show()

        self.thread_pool = QThreadPool.globalInstance()

        # Connect GUI signals to application logic slots
        self.gui.connect_browse_input(self.browse_input)
        self.gui.connect_browse_output(self.browse_output)
        self.gui.connect_start_processing(self.start_processing)

        self.selected_files_list = []
        self.selected_directory = None
        self.total_files_to_process = 0
        self.processed_files_count = 0

    def browse_input(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self.gui,
                                                "选择一个或多个图片文件",
                                                "",
                                                "Images (*.jpg *.png *.jpeg *.gif *.bmp *.webp *.avif *.jpegxl);;All Files (*)",
                                                options=options)
        if files:
            self.selected_files_list = files
            self.gui.input_line.setText(f"[已选择 {len(files)} 个文件]")
            self.selected_directory = None
        else:
            self.selected_files_list = []
            self.gui.input_line.setText("")
            self.selected_directory = None

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self.gui, "选择输出目录")
        if path:
            self.gui.output_line.setText(path)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                    self.gui.append_message(f"创建输出目录：{path}")
                except Exception as e:
                    self.gui.append_message(f"创建输出目录失败：{e}")

    def start_processing(self):
        output_dir = self.gui.output_line.text()
        output_format = self.gui.format_combo.currentText()
        output_quality = self.gui.quality_slider.value()
        resolution_ratio = self.gui.ratio_slider.value()
        max_threads = self.gui.thread_spinbox.value()

        files_to_process = []

        if self.selected_files_list:
            files_to_process = [f for f in self.selected_files_list if os.path.isfile(f)]
            self.gui.append_message(f"准备处理 {len(files_to_process)} 个选定文件。")
        else:
            input_path_text = self.gui.input_line.text()
            if not input_path_text:
                 self.gui.append_message("错误：请指定输入文件或目录。")
                 return
            if not os.path.exists(input_path_text):
                 self.gui.append_message(f"错误：输入路径不存在：{input_path_text}")
                 return

            if os.path.isdir(input_path_text):
                self.gui.append_message(f"扫描目录：{input_path_text}")
                for root, _, files in os.walk(input_path_text):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                             files_to_process.append(file_path)
                self.gui.append_message(f"在目录中找到 {len(files_to_process)} 个文件进行处理。")
            elif os.path.isfile(input_path_text):
                 files_to_process.append(input_path_text)
                 self.gui.append_message("准备处理单个选定文件。")
            else:
                self.gui.append_message(f"错误：无效的输入数据：{input_path_text}")
                return

        if not files_to_process:
             self.gui.append_message("没有找到需要处理的文件。")
             return

        if not output_dir:
            self.gui.append_message("错误：请指定输出目录。")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.gui.append_message(f"创建输出目录：{output_dir}")
            except Exception as e:
                self.gui.append_message(f"创建输出目录失败：{e}")
                return

        self.gui.message_log.clear()
        self.gui.progress_bar.setValue(0)
        self.gui.set_process_button_enabled(False)

        self.total_files_to_process = len(files_to_process)
        self.processed_files_count = 0
        self.gui.append_message(f"总共需要处理 {self.total_files_to_process} 个文件。")
        self.gui.append_message(f"使用最大线程数：{max_threads}")

        rimage_path = find_rimage() # Use the function from utils.py
        if not rimage_path:
            self.gui.append_message("错误：未找到 rimage.exe。请确保它在 PATH 环境变量中或与脚本在同一目录。")
            self.processing_finished()
            return
        self.gui.append_message(f"使用 rimage.exe 路径：{rimage_path}")

        self.thread_pool.setMaxThreadCount(max_threads)

        for file_path in files_to_process:
            task = ImageProcessingTask(file_path, rimage_path, output_format, output_quality, resolution_ratio, output_dir)
            task.signals.message.connect(self.gui.append_message)
            task.signals.error.connect(self.gui.append_message)
            task.signals.finished.connect(self.task_finished)
            self.thread_pool.start(task)

    def task_finished(self):
        self.processed_files_count += 1
        progress = int((self.processed_files_count / self.total_files_to_process) * 100)
        self.gui.update_progress(progress)

        if self.processed_files_count == self.total_files_to_process:
            self.processing_finished()

    def processing_finished(self):
        self.gui.append_message("所有文件处理完成。")
        self.gui.set_process_button_enabled(True)

    def closeEvent(self, event):
        # This closeEvent is for the main application class, not the GUI widget
        # The QApplication handles the event loop and cleanup
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Create an instance of the main application logic class
    main_app = Application()
    sys.exit(app.exec_())
