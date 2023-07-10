import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QEventLoop, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow


class PrintThread(QThread):
    signalForText = QtCore.pyqtSignal(str)

    def __init__(self, data, parent=None):
        super(PrintThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.signalForText.emit(str(text))  # 发射信号

    def run(self):
        print(self.data)

    # 报错消除！
    def flush(self):
        pass


class Terminal(QMainWindow):
    def __init__(self, parent=None):
        super(Terminal, self).__init__(parent)
        self.thr = PrintThread(data='')
        self.thr.signalForText.connect(self.addData)
        # 把系统输出重定向输出到PrintThread
        sys.stdout = self.thr
        self.TextEditor = parent.ui.terminal_c
        self.LineEditor = parent.ui.input_bash

    def addData(self, text):
        cursor = self.TextEditor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.TextEditor.setTextCursor(cursor)
        self.TextEditor.ensureCursorVisible()

    def Begin(self):
        try:
            self.t = PrintThread(data=self.getData())
            self.t.start()
        except Exception as e:
            raise e

    def change_directory(self, directory):
        import os
        try:
            os.chdir(directory)  # 切换工作目录
        except Exception as e:
            print(e)

    def getData(self):
        import subprocess
        msg1 = self.LineEditor.text()
        output = ""
        cmd = ["cmd.exe", '/c']
        # 特判 cls/cd
        if msg1 == 'cls':
            self.TextEditor.clear()
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
        header2 = "\n[out]:\n"
        if output != "":
            content = header1 + msg1 + header2 + output
        else:
            content = header1 + msg1
        return content

    def Run(self):
        self.Begin()
        self.LineEditor.clear()
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
