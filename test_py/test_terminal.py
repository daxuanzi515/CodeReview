from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import qtawesome
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer, QThread, QTime
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit


class MyThread(QThread):
    signalForText = pyqtSignal(str)

    def __init__(self, data, parent=None):
        super(MyThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.signalForText.emit(str(text))  # 发射信号

    def run(self):
        # 演示代码
        print(self.data)


class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.th = MyThread(data='')
        self.th.signalForText.connect(self.onUpdateText)
        sys.stdout = self.th

    def onUpdateText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def init_ui(self):
        self.setFixedSize(800, 400)
        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName('widget')
        self.layout = QtWidgets.QGridLayout()
        self.widget.setLayout(self.layout)  # 设置部件布局为网格

        self.main_layout.addWidget(self.widget, 0, 2, 12, 10)
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        self.bar_widget = QtWidgets.QWidget()  # 顶部搜索框部件
        self.bar_layout = QtWidgets.QGridLayout()  # 顶部搜索框网格布局
        self.bar_widget.setLayout(self.bar_layout)
        self.search_button = QtWidgets.QPushButton(qtawesome.icon('fa.comment', color='red'), "搜索")
        self.search_button.clicked.connect(self.genMastClicked)


        self.search_button.setObjectName('button')
        self.search_button.setFont(qtawesome.font('fa', 16))
        self.bar_widget_search_input = QtWidgets.QLineEdit()  # 搜索框
        self.bar_widget_search_input.setPlaceholderText("输入搜索内容")

        self.bar_widget_search_input.returnPressed.connect(self.genMastClicked)
        self.bar_layout.addWidget(self.search_button, 0, 0, 1, 1)
        self.bar_layout.addWidget(self.bar_widget_search_input, 0, 1, 1, 8)

        self.layout.addWidget(self.bar_widget, 0, 0, 1, 9)

        self.recommend_label = QtWidgets.QLabel("进程显示：")
        self.recommend_label.setObjectName('lable')

        self.recommend_widget = QtWidgets.QWidget()
        self.recommend_layout = QtWidgets.QGridLayout()
        self.recommend_widget.setLayout(self.recommend_layout)

        self.process = QTextEdit(self, readOnly=True)
        self.process.setLineWrapMode(500)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(500)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setFixedWidth(500)
        self.process.setFixedHeight(250)
        self.process.move(30, 50)

        self.recommend_layout.addWidget(self.process, 0, 1)
        self.layout.addWidget(self.recommend_label, 1, 0, 1, 9)
        self.layout.addWidget(self.recommend_widget, 2, 0, 2, 9)

        # 使用QSS和部件属性美化窗口部件
        self.bar_widget_search_input.setStyleSheet(
            '''QLineEdit{
                    border:1px solid gray;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
            }''')
        self.widget.setStyleSheet('''
            QWidget#widget{
                color:#232C51;
                background:white;
                border-top:1px solid darkGray;
                border-bottom:1px solid darkGray;
                border-right:1px solid darkGray;
            }
            QLabel#lable{
                border:none;
                font-size:16px;
                font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            QPushButton#button:hover{border-left:4px solid red;font-weight:700;}
            QTextEdit {
                color: #FF8BFF;  /* 设置文本颜色为骚粉 */
                background-color: #143113;  /* 设置背景颜色为黑绿 */
                font-family: "Consolas", monospace;
            }
        ''')

    def search(self):
        try:
            self.t = MyThread(data=self.mydata())
            self.t.start()
        except Exception as e:
            raise e

    def change_directory(self, directory):
        import os
        try:
            os.chdir(directory)  # 切换工作目录
        except Exception as e:
            print(e)

    def mydata(self):
        import subprocess
        msg1 = self.bar_widget_search_input.text()
        output = ""
        cmd = ["cmd.exe", '/c']
        # 特判 cls
        if msg1 == 'cls':
            self.process.clear()
        elif 'cd' in msg1:
            temp = msg1.split(' ')
            self.change_directory(temp[1])
        elif ' ' in msg1:
            temp = msg1.split(' ')
            cmd = cmd + temp
        else:
            cmd.append(msg1)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                output += line.decode('gbk')  # 将回显内容添加到字符串中
            process.wait()
        except Exception as e:
            output = str(e)

        header1 = "[in]: "
        header2 = "\n[out]: "
        if output != "":
            content = header1 + msg1 + header2 + output
        else:
            content = header1 + msg1
        return content

    def genMastClicked(self):
        """Runs the main function."""
        # print('Running...')
        self.search()

        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    gui = MainUi()
    gui.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

