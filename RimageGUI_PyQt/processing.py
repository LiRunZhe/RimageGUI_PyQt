import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRunnable, QThreadPool, QObject
import os
import subprocess
from PIL import Image # Using Pillow to get image size

# Signals for the QRunnable task
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    message = pyqtSignal(str)
    progress = pyqtSignal(int) # Optional, if we want per-task progress

# QRunnable task for processing a single image
class ImageProcessingTask(QRunnable):
    def __init__(self, file_path, rimage_path, output_format, output_quality, resolution_ratio, output_dir):
        super().__init__()
        self.file_path = file_path
        self.rimage_path = rimage_path
        self.output_format = output_format
        self.output_quality = output_quality
        self.resolution_ratio = resolution_ratio
        self.output_dir = output_dir
        self.signals = WorkerSignals() # Create a signals object

    def run(self):
        try:
            # Use Pillow to get image size
            if not os.path.isfile(self.file_path):
                 self.signals.message.emit(f"跳过非文件项：{self.file_path}")
                 self.signals.finished.emit()
                 return

            try:
                with Image.open(self.file_path) as img:
                    original_width, original_height = img.size
            except Exception as img_e:
                self.signals.error.emit(f"无法打开或读取图片文件 {os.path.basename(self.file_path)}：{img_e}")
                self.signals.finished.emit()
                return

            new_width = int(original_width * (self.resolution_ratio / 100))
            new_height = int(original_height * (self.resolution_ratio / 100))

            self.signals.message.emit(f"处理文件：{os.path.basename(self.file_path)} ({original_width} x {original_height}) -> ({new_width} x {new_height})")

            # Determine the actual output directory
            actual_output_dir = self.output_dir
            if not actual_output_dir: # Check if output_dir is empty
                actual_output_dir = os.path.dirname(self.file_path)
                # Ensure the directory exists if using the source directory
                if not os.path.exists(actual_output_dir):
                     try:
                         os.makedirs(actual_output_dir)
                         self.signals.message.emit(f"创建输出目录：{actual_output_dir}")
                     except Exception as e:
                         self.signals.error.emit(f"创建输出目录失败：{e}")
                         self.signals.finished.emit()
                         return

            # Construct the new file name with quality suffix
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            new_file_name = f"{base_name}_q{self.output_quality}.{self.output_format}"

            # Construct the full new file path
            new_file_path = os.path.join(actual_output_dir, new_file_name)

            if os.path.exists(new_file_path):
                self.signals.message.emit(f"文件 {new_file_name} 已存在，跳过。")
            else:
                # Construct the rimage command
                command = [
                    self.rimage_path,
                    self.output_format, # Use format as subcommand
                ]

                # Add quality parameter based on format
                if self.output_format in ["jpg", "webp", "avif"]:
                    command.extend(["--quantization", str(self.output_quality)])
                    command.extend(["--quality", str(self.output_quality)])
                elif self.output_format in ["jpeg_xl", "png", "oxipng"]:
                    command.extend(["--quantization", str(self.output_quality)])

                # Add common parameters
                command.extend([
                    "--dithering", "100",    # Assuming these are fixed based on the original script
                    "--resize", f"{new_width}x{new_height}", # Use --resize with widthxheight format
                    "-d", actual_output_dir, # Use actual_output_dir for output directory
                    "--suffix", f"_q{self.output_quality}", # Add quality suffix
                    self.file_path
                ])

                # Execute the rimage command
                # Use CREATE_NO_WINDOW flag on Windows to hide the console window
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    self.signals.error.emit(f"处理文件 {os.path.basename(self.file_path)} 失败：{stderr.decode('utf-8', errors='ignore')}")
                else:
                    self.signals.message.emit(f"成功处理文件：{os.path.basename(self.file_path)} --> {new_file_name}")

            # self.signals.progress.emit(...) # Emit progress if needed per task

        except Exception as e:
            self.signals.error.emit(f"处理文件 {os.path.basename(self.file_path)} 时发生错误：{e}")
        finally:
            self.signals.finished.emit() # Signal that this task is finished
