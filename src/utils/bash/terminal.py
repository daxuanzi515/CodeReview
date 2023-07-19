import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QEventLoop, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow
from src.utils.log.log import Log
# 自定义线程类
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
        # 把系统输出重定向输出到PrintThread对象
        sys.stdout = self.thr
        self.TextEditor = parent.ui.terminal_c
        self.LineEditor = parent.ui.input_bash
        self.process = None
        self.is_waiting_for_input = False
        self.log_obj = Log()

        self.config_ini = parent.config_ini
        self.user_id = None

    def addData(self, text):
        # 通过print输出的所有内容 将从控制台重定向到界面上
        # 就是说只要print()使用 就会打到界面上
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
            # raise e
            print(e)

    def change_directory(self, directory):
        import os
        try:
            os.chdir(directory)  # 切换工作目录
        except Exception as e:
            # raise e
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
        elif ' ' in msg1 and not self.is_waiting_for_input:
            temp = msg1.split(' ')
            cmd = cmd + temp
            try:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                while True:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    output += line.decode('gbk')  # 将回显内容添加到字符串中
                self.process.wait()
            except Exception as e:
                output = str(e)
        elif not self.is_waiting_for_input and not ' ' in msg1 and not '.exe' in msg1:
            cmd.append(msg1)
            try:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                while True:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    output += line.decode('gbk')  # 将回显内容添加到字符串中
                self.process.wait()
            except Exception as e:
                output = str(e)
        elif '.exe' in msg1 and not self.is_waiting_for_input:  # 限制输入参数？？？ 如果不含参数的话就不调用...
            self.process = subprocess.Popen(msg1, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, universal_newlines=True)
            self.is_waiting_for_input = True
        elif self.is_waiting_for_input:
            # 发送输入给子进程
            self.process.stdin.write(msg1)
            # 缓冲区为空就不调用
            if msg1 == "" or msg1 == '\n':
                pass
            else:
                self.process.stdin.flush()
            self.process.stdin.close()
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                output += line
            self.is_waiting_for_input = False

        header1 = "[in]: "
        header2 = "\n[out]:\n"

        self.log_obj.inputValue(self.user_id, f'使用终端输入命令行内容: {msg1}', '操作安全')
        logging1 = self.log_obj.returnString()
        self.log_obj.inputValue(self.user_id, f'使用终端获取回显内容: {output}', '操作安全')
        logging2 = self.log_obj.returnString()
        self.log_obj.generate_log(logging1 + logging2, (self.config_ini['main_project']['project_name']
                                                        + self.config_ini['log']['log_file']).format(self.user_id,
                                                                                                     'Log'))
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
