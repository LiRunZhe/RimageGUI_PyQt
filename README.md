# Rimage Batch Processor

一个基于 PyQt5 的图形用户界面工具，用于批量处理图片文件，利用外部的 `rimage.exe` 工具进行高效的图片格式转换、质量调整和分辨率缩放。

Vibe Coding 自娱自乐项目，全程基于 Gemini-2.5-pro 以及 Gemini-2.5-flash 开发。

## 特性

*   支持批量处理多个图片文件或整个目录。
*   支持多种输出格式：JPG, PNG, Oxipng, JPEGXL, WebP, AVIF。
*   可调整输出图片的质量和分辨率比例。
*   利用多线程进行并行处理，提高效率。
*   直观的图形用户界面。

## 依赖项

*   Python 3.x
*   PyQt5
*   Pillow (PIL)
*   **`rimage.exe` 外部工具**: 本项目依赖于一个名为 `rimage.exe` 的外部命令行工具来执行实际的图片处理任务。请确保 `rimage.exe` 可执行文件位于系统的 PATH 环境变量中，或者将其放置在与 `main.py` 脚本相同的目录中。您可以从 [rimage 项目地址](https://github.com/your-rimage-repo) 获取 `rimage.exe`（请将此链接替换为实际的 rimage 项目地址）。

## 安装

1.  克隆本仓库到本地。
2.  确保您已安装 Python 3.x。
3.  安装项目所需的 Python 依赖：
    ```bash
    pip install -r requirements.txt
    ```

## 如何运行

1.  确保已安装所有依赖项，并且 `rimage.exe` 可用。
2.  运行主脚本：
    ```bash
    python RimageGUI_PyQt/main.py
    ```

## 如何构建可执行文件 (可选)

本项目包含一个 `main.spec` 文件，可以使用 PyInstaller 构建独立的可执行文件。

1.  安装 PyInstaller：
    ```bash
    pip install pyinstaller
    ```
2.  在项目根目录运行：
    ```bash
    pyinstaller main.spec
    ```
    构建好的可执行文件将在 `dist/` 目录中找到。

## 使用方法

1.  打开 Rimage Batch Processor 应用程序。
2.  点击“浏览...”按钮选择要处理的图片文件或包含图片的目录。
3.  点击“浏览...”按钮选择处理后图片的输出目录。
4.  选择输出格式、调整质量和分辨率比例。
5.  设置最大线程数。
6.  点击“开始处理”按钮。
7.  处理进度和消息将显示在界面下方。

## 许可证

本项目采用 MIT 许可证。详情请参阅 `LICENSE` 文件。

## 贡献

欢迎提交问题和拉取请求。
