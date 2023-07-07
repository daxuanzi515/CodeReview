from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciStyle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QsciScintilla Example")
        self.resize(800, 600)

        # 创建容器和布局
        container = QWidget()
        layout = QVBoxLayout(container)

        # 创建 QsciScintilla 编辑器
        self.editor = QsciScintilla()
        self.editor.setLexer(QsciLexerPython(self.editor))
        self.editor.setText("Hello World!\nThis is a sample text.\nHello PyQt5!")
        self.editor.setFont(QFont("Courier New"))
        self.editor.setMarginLineNumbers(1, True)

        # 创建查找输入框、查找按钮和标签用于显示匹配次数
        self.find_input = QLineEdit(self)
        self.find_button = QPushButton("Find", self)
        self.find_select_button = QPushButton("Find_select",self)
        self.jump_button = QPushButton("Jump", self)
        self.find_button.clicked.connect(self.find_text)
        self.find_select_button.clicked.connect(self.find_select_text)
        self.jump_button.clicked.connect(self.jump_to_target)
        self.count_label = QLabel()


        self.current_index = 0  # 当前位置索引
        self.keywords_pos = []
        # 添加控件到布局中
        layout.addWidget(self.find_input)
        layout.addWidget(self.find_button)
        layout.addWidget(self.find_select_button)
        layout.addWidget(self.jump_button)
        layout.addWidget(self.count_label)
        layout.addWidget(self.editor)

        # 设置容器为主窗口的中央部件
        self.setCentralWidget(container)

    def find_text(self):
        keyword = self.find_input.text()
        positions = []  # 存储匹配的位置
        line = 0  # 设置起始行号为0
        index = 0  # 设置起始索引为0
        count = 0  # 匹配次数计数器

        while True:
            flag = self.editor.findFirst(keyword, False, False, False, False, True, line, index, True, False, False)
            if not flag:  # 未找到匹配
                break
            found_pos = self.editor.SendScintilla(self.editor.SCI_GETCURRENTPOS)
            found_line = self.editor.SendScintilla(self.editor.SCI_LINEFROMPOSITION, found_pos)
            found_index = found_pos - self.editor.SendScintilla(self.editor.SCI_POSITIONFROMLINE, found_line)-1
            positions.append((found_line, found_index, found_line, found_index + len(keyword)))  # 记录匹配的位置（行号和索引）
            count += 1
            line = found_line  # 更新起始行号，从上一次匹配的行开始继续搜索
            index = found_index + len(keyword)

        print(positions," ", count)
        self.keywords_pos = positions


    # 光标移动

    def jump_to_target(self):
        positions = self.keywords_pos
        if positions:
            position = positions[self.current_index]
            end_line, end_index = position[2], position[3]
            self.editor.setCursorPosition(end_line, end_index)
            self.highlight_text(position)
            self.current_index += 1
            if self.current_index >= len(positions):
                self.current_index = 0

    def highlight_text(self, positions):
        start_line, start_index, end_line, end_index = positions
        self.editor.setSelectionBackgroundColor(QColor('blue'))
        self.editor.setSelectionForegroundColor(QColor('yellow'))
        self.editor.setSelection(start_line, start_index, end_line, end_index)


    def find_select_text(self):
        keyword = self.find_input.text()
        print(keyword)
        # 选定范围内 查
        pos = self.editor.findFirstInSelection(keyword, False, False, False, True, True, False, False)
        if self.editor.text():
            # p = (start_line, start_index,end_line,end_index) index就是单个字符在这一行的第几个位置
            p = self.editor.getSelection()
            print(p)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
