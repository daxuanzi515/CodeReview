import os

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QRectF, Qt, QFile
from PyQt5.QtGui import QPainter, QPaintEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QFrame, QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout


class WelcomePage(QFrame):
    def __init__(self, parent, target_img):
        super().__init__(parent)
        self.background_image = QPixmap(target_img)
        self.current_line = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateBackground)
        self.timer_interval = 10  # 每行绘制的间隔时间，单位为毫秒

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        rect = self.rect()
        line_height = rect.height() / self.background_image.height()
        painter.setClipRect(rect)
        painter.setOpacity(1.0)

        for i in range(self.current_line + 1):
            line_rect = QRectF(rect.left(), rect.top(), rect.width(), (i + 1) * line_height)
            painter.drawPixmap(line_rect, self.background_image, QRectF(0, 0, self.background_image.width(), (i + 1) * line_height))

    def updateBackground(self):
        self.current_line += 1
        self.update()
        if self.current_line >= self.background_image.height():
            self.timer.stop()

    def startAnimation(self):
        self.current_line = 0
        self.timer.start(self.timer_interval)

# 自定义对话窗口
class CustomMessageBox(QDialog):
    def __init__(self, icon, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)
        self.setFixedSize(300, 150)  # 设置对话框的固定大小
        # 隐藏？
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()
        label = QLabel(text)
        button = QPushButton('确认')
        button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

# 自定义保存对话框
class SaveMessage(QDialog):
    # 保存信号
    save = QtCore.pyqtSignal()
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提示")
        self.setWindowIcon(icon)
        self.setFixedSize(350, 100)  # 设置对话框的固定大小
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        label = QLabel("是否保存当前文件？")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        label.setAlignment(Qt.AlignCenter)  # 将文本水平和垂直居中显示
        v_layout.addWidget(label)

        button1 = QPushButton('保存文件')
        button2 = QPushButton('取消保存')
        button1.clicked.connect(self.save_file)
        button2.clicked.connect(self.reject)
        h_layout.addWidget(button1)
        h_layout.addWidget(button2)
        v_layout.addLayout(h_layout)

    def save_file(self):
        self.save.emit()
        self.accept()


class ReplaceMessage(QDialog):
    def __init__(self, icon, filename, absolute_path, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.absolute_path = absolute_path
        self.setWindowTitle("提示")
        self.setWindowIcon(icon)
        self.setFixedSize(300, 100)  # 设置对话框的固定大小
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        label = QLabel(f"路径下存在同名文件{filename}，是否替换？")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        label.setAlignment(Qt.AlignCenter)  # 将文本水平和垂直居中显示
        v_layout.addWidget(label)

        button1 = QPushButton('替换文件')
        button2 = QPushButton('取消')
        button1.clicked.connect(self.replace_file)
        button2.clicked.connect(self.reject)
        h_layout.addWidget(button1)
        h_layout.addWidget(button2)
        v_layout.addLayout(h_layout)

    def replace_file(self):
        file = QFile(self.absolute_path)
        if file.open(QFile.WriteOnly | QFile.Text):
            content = ""
            file.write(content.encode())
            file.close()
            message_box = CustomMessageBox(self.icon, '提示', '文件已经替换！')
            message_box.exec_()
            self.accept()  # 关闭替换窗口
        else:
            message_box = CustomMessageBox(self.icon, '提示', '文件无法替换！')
            message_box.exec_()
            self.accept()  # 关闭替换窗口


# 移除文件窗口
class RemoveMessage(QDialog):
    def __init__(self, icon, filename, absolute_path, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.absolute_path = absolute_path
        self.complete_path = absolute_path + '/' + filename
        self.setWindowTitle("提示")
        self.setWindowIcon(icon)
        self.setFixedSize(280, 100)  # 设置对话框的固定大小
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        label = QLabel(f"是否删除当前文件:{filename}？")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        label.setAlignment(Qt.AlignCenter)  # 将文本水平和垂直居中显示
        v_layout.addWidget(label)

        button1 = QPushButton('删除')
        button2 = QPushButton('取消')
        button1.clicked.connect(self.remove_files_to_trash)
        button2.clicked.connect(self.reject)
        h_layout.addWidget(button1)
        h_layout.addWidget(button2)
        v_layout.addLayout(h_layout)

    def remove_files_to_trash(self):
        from send2trash import send2trash
        # 规范化路径
        file_path = os.path.normpath(self.complete_path)
        try:
            send2trash(file_path)
            print('删除成功！')
            self.accept()
        except:
            print('删除失败！')
            self.accept()