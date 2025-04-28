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

            new_file_name = os.path.splitext(os.path.basename(self.file_path))[0] + f".{self.output_format}"
            new_file_path = os.path.join(self.output_dir, new_file_name)

            if os.path.exists(new_file_path):
                self.signals.message.emit(f"文件 {new_file_name} 已存在，跳过。")
            else:
                # Construct the rimage command
                command = [
                    self.rimage_path,
                    self.output_format, # Use format as subcommand
                ]

                # Add quality parameter based on format
                if self.output_format == "jpg": # Specifically handle jpg
                    command.extend(["--quantization", str(self.output_quality)])
                    command.extend(["--quality", str(self.output_quality)])
                elif self.output_format == "webp": # Specifically handle webp
                    command.extend(["--quantization", str(self.output_quality)])
                    command.extend(["--quality", str(self.output_quality)]) # Assuming --quality is also needed/preferred
                elif self.output_format == "avif": # Keep -q for avif (assuming it's correct for now)
                    command.extend(["-q", str(self.output_quality)])
                elif self.output_format in ["png", "oxipng", "jpegxl"]:
                     command.extend(["--quantization", str(self.output_quality)]) # Assuming this is correct for these formats

                # Add common parameters
                command.extend([
                    "--dithering", "100",    # Assuming these are fixed based on the original script
                    "--resize", f"{new_width}x{new_height}", # Use --resize with widthxheight format
                    "-d", self.output_dir, # Use -d for output directory
                    self.file_path
                ])

                # Execute the rimage command
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
