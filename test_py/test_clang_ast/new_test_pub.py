from os.path import split

from PyQt5 import Qsci
from PyQt5.Qsci import QsciScintilla, QsciLexerCPP
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction, QTabWidget

from func_dump import FunctionPreprocessor


class MainWindow(QMainWindow):
    def __init__(self, filename):
        super().__init__()
        self.context_menu = None
        self.setWindowTitle("Test Function Analyse Pub")
        self.resize(800, 600)
        path, name = split(filename)
        self.filename = name

        # 创建容器和布局
        self.tab_obj = QTabWidget(self)
        container = QWidget()
        layout = QVBoxLayout(container)

        # 创建 QsciScintilla 编辑器
        self.editor = QsciScintilla()
        self.editor.setLexer(QsciLexerCPP(self.editor))

        with open(self.filename, 'r', encoding='utf-8') as file:
            contents = file.read()

        self.editor.setText(contents)
        self.editor.setFont(QFont("Courier New"))

        self.editor.setMarginLineNumbers(1, True)
        self.editor.setMarginWidth(1, '0000')
        self.editor.setMarginsForegroundColor(QColor("#006400"))

        self.func_dump = QPushButton('Function Analyse', self)

        self.func_dump.clicked.connect(self.FunctionAnalyseRun)

        layout.addWidget(self.editor)
        layout.addWidget(self.func_dump)

        self.tab_obj.addTab(container, filename)

        self.setCentralWidget(self.tab_obj)

        # 对象
        self.func_dump = None
        # 头文件
        self.headers_function_declaration_list = []
        self.headers_function_definition_list = []
        self.headers_function_callexpress_list = []
        # 源文件
        self.function_declaration_list = None
        self.function_definition_list = None
        self.function_callexpress_list = None
        # 设置默认菜单为自定义菜单
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        # 设置触发
        self.editor.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        self.context_menu = self.editor.createStandardContextMenu()
        # 添加默认选项
        self.context_menu.insertSeparator(self.context_menu.actions()[0])

        action_goto_declaration = QAction("转到声明", self)
        action_goto_declaration.triggered.connect(self.gotoDeclaration)
        action_goto_definition = QAction("转到定义", self)
        action_goto_definition.triggered.connect(self.gotoDefinition)
        action_goto_call_express = QAction("转到调用", self)
        action_goto_call_express.triggered.connect(self.gotoCallExpress)
        # 分隔符
        self.context_menu.insertSeparator(self.context_menu.actions()[0])
        self.context_menu.insertAction(self.context_menu.actions()[0], action_goto_declaration)
        self.context_menu.insertAction(self.context_menu.actions()[1], action_goto_definition)
        self.context_menu.insertAction(self.context_menu.actions()[2], action_goto_call_express)
        # 应用
        self.context_menu.exec_(self.editor.mapToGlobal(point))

    def filter_selected_string(self, input_string):
        import re
        pattern = r'\b(\w+)\s*\('
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)
        words = re.findall(r'\b\w+\b', input_string)  # 提取字符串中的单词列表
        for word in words:
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):  # 判断单词是否符合函数名的命名规则
                return word  # 返回第一个符合要求的单词作为函数名
        return None

    # 槽函数 gotoDeclaration gotoDefinition gotoCallExpress
    def gotoDeclaration(self):
        position, selected_text = self.getSelected_Position_Content()
        location = None
        # 过滤选中的字符
        selected_text = self.filter_selected_string(selected_text)
        if self.func_dump:
            for item in self.function_declaration_list:
                if selected_text == item.function_name and item.declared_location is not None:
                    location = item.declared_location
                    break

            # 头文件
            for path, item in self.headers_function_declaration_list:
                print(path)
                print(item)
                for i in item:
                    if selected_text == i.function_name and i.declared_location is not None:
                        # location = item.declared_location
                        print(i.declared_location)
                        break

            if location is not None:
                start_line = location[0] - 1
                start_index = location[1] - 1
                end_line = location[2] - 1
                end_index = location[3] - 1
                text_location = [(start_line, start_index, end_line, end_index)]
                self.highlight_function_declaration(text_location)
        else:
            pass

    def gotoDefinition(self):
        position, selected_text = self.getSelected_Position_Content()
        location = None
        # 过滤选中的字符
        selected_text = self.filter_selected_string(selected_text)
        if self.func_dump:
            for item in self.function_definition_list:
                if selected_text == item.function_name and item.definition_location is not None:
                    location = item.definition_location
                    break

            if location is not None:
                start_line = location[0] - 1
                start_index = location[1] - 1
                end_line = location[2] - 1
                end_index = location[3] - 1
                text_location = [(start_line, start_index, end_line, end_index)]
                self.highlight_function_definition(text_location)
        else:
            pass

    def gotoCallExpress(self):
        position, selected_text = self.getSelected_Position_Content()
        locations = []
        # 过滤选中的字符
        selected_text = self.filter_selected_string(selected_text)
        if self.func_dump:
            for item in self.function_callexpress_list:
                if selected_text == item.function_name and item.call_express_location is not None:
                    location = item.call_express_location

                    start_line = location[0] - 1
                    start_index = location[1] - 1
                    end_line = location[2] - 1
                    end_index = location[3] - 1
                    text_location = (start_line, start_index, end_line, end_index)

                    locations.append(text_location)
            if locations is not None:
                self.highlight_function_call_express(locations)
        else:
            pass

    def getSelected_Position_Content(self):
        if self.editor.getSelection() != (-1, -1, -1, -1):
            selected_text = self.editor.selectedText()
            start_line = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_LINEFROMPOSITION, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONSTART))  # 设置起始行号为当前选中文本所在行
            start_index = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_GETCOLUMN, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONSTART))  # 设置起始索引为当前选中文本的起始位置
            end_line = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_LINEFROMPOSITION, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONEND))  # 设置结束行号为当前选中文本的结束行
            end_index = self.editor.SendScintilla(Qsci.QsciScintilla.SCI_GETCOLUMN, self.editor.SendScintilla(
                Qsci.QsciScintilla.SCI_GETSELECTIONEND))  # 设置结束索引为当前选中文本的结束位置

            return [(start_line, start_index, end_line, end_index)], selected_text

    def highlight_function_declaration(self, positions):
        # 传入的是整个位置数据....
        indicator_number = 1  # 指示器的编号
        lines = self.editor.lines() - 1
        indexs = self.editor.lineLength(lines)
        indicator_color = QColor('#f05b72')  # 蔷薇色
        if positions:
            self.highlight_handle(positions, lines, indexs, indicator_number, indicator_color)

    def highlight_function_definition(self, positions):
        # 传入的是整个位置数据....
        indicator_number = 2  # 指示器的编号
        lines = self.editor.lines() - 1
        indexs = self.editor.lineLength(lines)
        indicator_color = QColor('#008792')  # 御纳戸色
        if positions:
            self.highlight_handle(positions, lines, indexs, indicator_number, indicator_color)

    def highlight_function_call_express(self, positions):
        # 传入的是整个位置数据....
        indicator_number = 3  # 指示器的编号
        lines = self.editor.lines() - 1
        indexs = self.editor.lineLength(lines)
        indicator_color = QColor('#f47920')  # 橙色
        if positions:
            self.highlight_handle(positions, lines, indexs, indicator_number, indicator_color)

    def highlight_handle(self, positions, lines, indexs, indicator_number, indicator_color):
        self.editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_number)
        # 清除所有指示器的色块填充
        for i in range(1, 4):
            self.editor.clearIndicatorRange(0, 0, lines, indexs, i)
        self.editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0,
                                  self.editor.SendScintilla(QsciScintilla.SCI_GETLINECOUNT))

        for start_line, start_index, end_line, end_index in positions:
            self.editor.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, indicator_number,
                                      QsciScintilla.INDIC_CONTAINER)
            self.editor.SendScintilla(QsciScintilla.SCI_INDICSETFORE, indicator_number,
                                      indicator_color)
            self.editor.fillIndicatorRange(start_line, start_index, end_line, end_index, indicator_number)
            self.editor.setCursorPosition(end_line, end_index)

    def new_tab_widget(self, filename):
        container = QWidget()
        layout = QVBoxLayout(container)

        # 创建 QsciScintilla 编辑器
        editor = QsciScintilla()
        editor.setLexer(QsciLexerCPP(self.editor))

        with open(self.filename, 'r', encoding='utf-8') as file:
            contents = file.read()

        editor.setText(contents)
        editor.setFont(QFont("Courier New"))

        editor.setMarginLineNumbers(1, True)
        editor.setMarginWidth(1, '0000')
        editor.setMarginsForegroundColor(QColor("#006400"))

        func_dump = QPushButton('Function Analyse', self)

        func_dump.clicked.connect(self.FunctionAnalyseRun)

        layout.addWidget(editor)
        layout.addWidget(func_dump)

        self.tab_obj.addTab(container, filename)
        return editor


    def clearAlldata(self):
        self.headers_function_declaration_list.clear()
        self.headers_function_definition_list.clear()
        self.headers_function_callexpress_list.clear()
        self.function_definition_list = None
        self.function_declaration_list = None
        self.function_callexpress_list = None

    def FunctionAnalyseRun(self):
        # 清空六个对象.....
        self.clearAlldata()
        self.func_dump = FunctionPreprocessor(self.filename)
        print('--------------头文件-----------------')
        headers_tuple = self.func_dump.headers_runner(self.filename)  # 可能是函数的声明和定义

        for item in headers_tuple:
            header_path, header_obj = item
            self.headers_function_declaration_list.append((header_path, header_obj.function_declaration_list))
            self.headers_function_definition_list.append((header_path, header_obj.function_definition_list))
            self.headers_function_callexpress_list.append((header_path, header_obj.function_callexpress_list))
            #
            # print("------------")
            # print(header_obj.function_declaration_list)
            # print(header_obj.function_definition_list)
            # print(header_obj.function_callexpress_list)
            # print("------------")
        exclude_headers_objs = self.func_dump.exclude_headers_runner(self.filename)  # 可能是函数的定义和调用
        self.function_declaration_list = exclude_headers_objs.function_declaration_list
        self.function_definition_list = exclude_headers_objs.function_definition_list
        self.function_callexpress_list = exclude_headers_objs.function_callexpress_list


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow('test_headers.cpp')
    window.show()
    app.exec_()
