from PyQt5 import Qsci
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search&&Replace Example")
        self.resize(800, 600)

        # 创建容器和布局
        container = QWidget()
        layout = QVBoxLayout(container)

        # 创建 QsciScintilla 编辑器
        self.editor = QsciScintilla()
        self.editor.setLexer(QsciLexerPython(self.editor))
        self.editor.setText("I am tripped.\nLet us meet underneath the moonlight.\nI am tripped!\nIs anyone can help me?\n******(8&*&^&^^%^?")
        self.editor.setFont(QFont("Courier New"))
        self.editor.setMarginLineNumbers(1, True)

        # 创建查找输入框、查找按钮和标签用于显示匹配次数
        self.find_input = QLineEdit(self)
        self.replace_input = QLineEdit(self)
        self.find_button = QPushButton("Find", self)
        self.find_select_button = QPushButton("Find_select", self)
        self.jump_button = QPushButton("Jump Down", self)
        self.jump_button_ = QPushButton("Jump Up", self)
        self.replace_button = QPushButton("Replace It", self)
        self.replace_button_ = QPushButton("Replace All", self)
        self.test_button = QPushButton("Test", self)
        self.find_button.clicked.connect(self.find_text)
        self.find_select_button.clicked.connect(self.find_select_text)
        self.jump_button.clicked.connect(self.jump_down_target)
        self.jump_button_.clicked.connect(self.jump_up_target)
        self.replace_button.clicked.connect(self.replace_text)
        self.replace_button_.clicked.connect(self.replace_text_)
        self.test_button.clicked.connect(self.test_func)
        self.count_label = QLabel()

        self.current_index = 0  # 当前位置索引
        self.keywords_pos = []
        self.select_keywords_pos = []
        # 替换位置索引
        self.replace_pos = []
        self.select_replace_pos = []

        # 添加控件到布局中
        layout.addWidget(self.find_input)
        layout.addWidget(self.replace_input)
        layout.addWidget(self.find_button)
        layout.addWidget(self.find_select_button)
        layout.addWidget(self.jump_button)
        layout.addWidget(self.jump_button_)
        layout.addWidget(self.replace_button)
        layout.addWidget(self.replace_button_)
        layout.addWidget(self.test_button)
        layout.addWidget(self.count_label)
        layout.addWidget(self.editor)
        # 设置容器为主窗口的中央部件
        self.setCentralWidget(container)

    def highlight_all_text(self, positions):
        indicator_number = 1  # 指示器的编号
        lines = self.editor.lines()-1
        indexs = self.editor.lineLength(lines)
        self.editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_number)
        self.editor.clearIndicatorRange(0, 0, lines, indexs, indicator_number)
        self.editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.editor.SendScintilla(QsciScintilla.SCI_GETLINECOUNT))
        for start_line, start_index, end_line, end_index in positions:
            self.editor.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, indicator_number,
                                          QsciScintilla.INDIC_CONTAINER)
            self.editor.SendScintilla(QsciScintilla.SCI_INDICSETFORE, indicator_number,
                                      QColor('#4169E1'))
            self.editor.fillIndicatorRange(start_line, start_index, end_line, end_index, indicator_number)


    def test_func(self):
        parameter = 'SCI_GETCURRENTPOS'
        print(getattr(self.editor, parameter))

    def find_text(self):
        # 清空矛盾
        self.select_keywords_pos.clear()
        self.keywords_pos.clear()
        # 关键词
        keyword = self.find_input.text()
        positions = set()  # 存储匹配的位置
        line = 0  # 设置起始行号为0
        index = 0  # 设置起始索引为0
        count = 0  # 匹配次数计数器
        if keyword:
            while True:
                flag = self.editor.findFirst(keyword, False, False, False, False, True, line, index, True, False, False)
                if not flag:  # 未找到匹配
                    break
                found_pos = self.editor.SendScintilla(self.editor.SCI_GETCURRENTPOS)
                found_line = self.editor.SendScintilla(self.editor.SCI_LINEFROMPOSITION, found_pos)
                found_index = found_pos - self.editor.SendScintilla(self.editor.SCI_POSITIONFROMLINE, found_line)-1
                if len(keyword) > 1:
                    positions.add((found_line, found_index-len(keyword)+1, found_line, found_index+1))  # 记录匹配的位置（行号和索引）
                else:
                    positions.add((found_line, found_index, found_line, found_index + len(keyword)))  # 记录匹配的位置（行号和索引）
                count += 1
                line = found_line  # 更新起始行号，从上一次匹配的行开始继续搜索
                index = found_index + len(keyword)

            print(list(positions)," ", count)
            self.keywords_pos = list(positions)
            self.highlight_all_text(self.keywords_pos)

            self.count_label.setText(f'共搜索到关键词: {keyword} {count}次！')


    # 光标移动
    def jump_down_target(self):
        positions = self.isValue()
        if positions:
            position = positions[self.current_index]
            end_line, end_index = position[2], position[3]
            self.editor.setCursorPosition(end_line, end_index)
            self.highlight_text(position)
            self.current_index += 1
            if self.current_index >= len(positions):
                self.current_index = 0

    def jump_up_target(self):
        positions = self.isValue()
        if positions:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = len(positions) - 1
            position = positions[self.current_index]
            end_line, end_index = position[2], position[3]
            self.editor.setCursorPosition(end_line, end_index)
            self.highlight_text(position)

    def highlight_text(self, positions):
        start_line, start_index, end_line, end_index = positions
        self.editor.setSelectionBackgroundColor(QColor('blue'))
        self.editor.setSelectionForegroundColor(QColor('yellow'))
        self.editor.setSelection(start_line, start_index, end_line, end_index)

    # 这还是有问题 但是目前能搜 放进组件里好像就有问题 之后查查
    def find_select_text(self):
        # 点击之前先清空一切阻碍
        self.select_keywords_pos.clear()
        self.keywords_pos.clear()

        self.editor.ensureCursorVisible()
        # 关键词
        keyword = self.find_input.text()
        if self.editor.getSelection() == (-1, -1, -1, -1):
            # 自定义的东西在这里...
            reply = QMessageBox.information(self, 'tips', '请先选中一段文字！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            print(self.editor.getSelection())
        # 有关键词且文本被选择
        if keyword and self.editor.getSelection() != (-1, -1, -1, -1):
            start_line = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_LINEFROMPOSITION, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONSTART))  # 设置起始行号为当前选中文本所在行
            start_index = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_GETCOLUMN, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONSTART))  # 设置起始索引为当前选中文本的起始位置
            end_line = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_LINEFROMPOSITION, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONEND))  # 设置结束行号为当前选中文本的结束行
            end_index = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_GETCOLUMN, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONEND))  # 设置结束索引为当前选中文本的结束位置

            temp_pos = (start_line, start_index, end_line, end_index)  # 记录选择的位置（起始行号、起始索引、结束行号、结束索引）
            print(temp_pos)
            positions = set()  # 存储匹配的位置
            count = 0
            current_line = start_line
            current_index = start_index

            while True:
                if (current_index >= end_index and current_line == end_line) or (current_line >= end_line and current_index > end_index) or (current_line > end_line):
                    break
                flag = self.editor.findFirst(keyword, False, False, False, False, True, current_line, current_index, True, False, False)
                if flag:
                    count += 1
                    found_pos = self.editor.SendScintilla(self.editor.SCI_GETCURRENTPOS)
                    found_line = self.editor.SendScintilla(self.editor.SCI_LINEFROMPOSITION, found_pos)
                    found_index = found_pos - self.editor.SendScintilla(self.editor.SCI_POSITIONFROMLINE, found_line)-1 # 计算当前遍历到的Index
                    current_line = found_line
                    current_index = found_index + len(keyword)
                    # 再判断
                    if current_line > end_line:
                        break
                    if len(keyword) > 1:
                        positions.add(
                            (found_line, found_index - len(keyword) + 1, found_line, found_index + 1))  # 记录匹配的位置（行号和索引）
                        print((found_line, found_index - len(keyword) + 1, found_line, found_index + 1))
                    else:
                        positions.add(
                            (found_line, found_index, found_line, found_index + len(keyword)))  # 记录匹配的位置（行号和索引）
                        print(found_line, found_index - len(keyword) + 1, found_line, found_index + 1)
                else:
                    # 这里是维持光标移动的精髓
                    if current_index <= end_index:
                        current_index += len(keyword)
                    else:
                        if current_line <= end_index:
                            current_index = 0
                            current_line += 1

            print(count)
            print(list(positions))
            self.select_keywords_pos = list(positions)

            self.count_label.setText(f'共搜索到关键词: {keyword} {count}次！')

    def replace_text(self):
        replace_word = self.replace_input.text()
        init_word = self.find_input.text()

        if replace_word:
            isfind = self.editor.findFirst(init_word, False, False, False, True, True, -1, -1, True, False, False)
            # 获取位置 选中 替换...
            if isfind:
                self.editor.replace(replace_word)
                self.count_label.setText('1处被替换成功！')
                # 记录替代位置
                end_line, end_index = self.editor.getCursorPosition()
                start_line = end_line
                start_index = end_index - len(replace_word)
                rpos = (start_line,start_index,end_line,end_index)
                print(rpos)


                self.replace_pos = [rpos]

    def replace_text_(self):
        replace_word = self.replace_input.text()
        init_word = self.find_input.text()
        pos = set()
        if replace_word:
            count = 0
            isfind = self.editor.findFirst(init_word, False, False, False, True, True, -1, -1, True, False, False)
            while isfind:
                self.editor.replace(replace_word)
                end_line, end_index = self.editor.getCursorPosition()
                start_line = end_line
                start_index = end_index - len(replace_word)
                rpos = (start_line,start_index,end_line,end_index)
                print(rpos)
                pos.add(rpos)
                isfind = self.editor.findNext()
                count += 1

            self.count_label.setText(f'{count}处被替换成功！')
            self.replace_pos = list(pos)
            print(self.replace_pos)


    def isValue(self):
        if self.keywords_pos:
            positions = self.keywords_pos
        elif self.select_keywords_pos:
            positions = self.select_keywords_pos
        else:
            positions = []
        # if self.replace_pos:
        #     positions = self.replace_pos
        # else:
        #     positions = []
        return positions

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
