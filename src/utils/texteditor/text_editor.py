import re
from PyQt5.Qsci import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MeQsciScintilla(QsciScintilla):
    # 继承编辑器类 重写键盘按键方法
    def __init__(self, parent=None):
        super(MeQsciScintilla, self).__init__(parent)

    def keyPressEvent(self, e):
        ''' 测试按下按键 '''
        if e.key() == Qt.Key_Escape:
            pass
        super().keyPressEvent(e)

    def wheelEvent(self, e):
        ''' Ctrl + 滚轮 控制字体缩放 '''
        if e.modifiers() == Qt.ControlModifier:
            da = e.angleDelta()
            if da.y() > 0:
                self.zoomIn(1)  # QsciScintilla 自带缩放
            elif da.y() < 0:
                self.zoomOut(1)
        else:
            super().wheelEvent(e)


class TextEditorWidget(QWidget):
    def __init__(self, filename, filepath):
        super(TextEditorWidget, self).__init__(parent=None)
        # 可访问成员变量
        self.filename = filename
        self.filepath = filepath
        self.status = False

        # 创建布局
        self.__layout = QVBoxLayout(self)
        self.__frame = QFrame(self)
        self.__frameLayout = QVBoxLayout(self.__frame)
        self.__layout.addWidget(self.__frame)

        # 创建编辑器
        self.__editor = MeQsciScintilla(self.__frame)
        # 这里设置自定义词法解析器CPP
        self.__lexer = MeLexer(self.__editor)
        # 配置MeLexer 里面有自定义的高亮风格
        self.__editor.setLexer(self.__lexer)

        # 设置自动补全敏感字数
        self.__editor.setAutoCompletionThreshold(1)
        self.__editor.setAutoCompletionSource(QsciScintilla.AcsAll)
        # 设置自动补全对象
        self.__api = QsciAPIs(self.__lexer)
        # 设置自动补全敏感
        self.__editor.setAutoCompletionCaseSensitivity(True)
        # 设置自动补全替换
        self.__editor.setAutoCompletionReplaceWord(True)
        # 设置自动填充
        self.__editor.setAutoCompletionFillupsEnabled(True)
        # 显示全部调用 不受上下文限制
        self.__editor.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
        # 自动补全选项在下面
        self.__editor.setCallTipsPosition(QsciScintilla.CallTipsBelowText)
        self.__editor.setCallTipsVisible(0)

        autocompletions = [
            '#include', 'using', 'namespace', 'std',
            'scanf', 'printf', 'return', 'char', '{}',
            '[]', '()', 'int', 'double', 'long', 'float',
            'string', 'endl', 'stdio.h', 'stdlib.h', 'iostream', '<>',
            'free', 'malloc', 'new', 'delete', 'public', 'private', 'protected',
            'sum(int a,int b)',
            'add(float a,float b)',
            'merge(double a,double b)',
            'divide(long a,long b)',
            'some_func()',
            'add(int a,int b)',
            'test(int a,int b,int c)',
            'func(float a,float b,float c)',
            'test1(double a,double b,double c)',
            'test2(long a,long b,long c)',
        ]
        for ac in autocompletions:
            self.__api.add(ac)
        self.__api.prepare()
        self.__editor.setCallTipsBackgroundColor(QColor('#D8BFD8'))
        # 设置自动补全字体颜色
        self.__editor.setCallTipsForegroundColor(QColor('#F08080'))

        # utf-8
        self.__editor.setUtf8(True)

        # 将编辑器添加到布局中
        self.__frameLayout.addWidget(self.__editor)

        # 细节
        # 设置背景色
        self.__editor.setPaper(QColor("#CCE8CF"))
        # 显示自动换行
        self.__editor.setWrapMode(QsciScintilla.WrapWord)
        self.__editor.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        self.__editor.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # 使用tab
        self.__editor.setIndentationsUseTabs(True)
        # 设置换行符长度4
        self.__editor.setTabWidth(4)
        # 设置Tab自动对齐
        self.__editor.setAutoIndent(True)
        # 设置鼠标光标颜色 前景色...
        self.__editor.setCaretForegroundColor(QColor("#0000CD"))
        # 设置选中行颜色
        self.__editor.setCaretLineVisible(True)
        self.__editor.setCaretLineBackgroundColor(QColor("#AAEDCB"))
        # 行号/页边距颜色
        # 显示行号 行号范围
        self.__editor.setMarginLineNumbers(1, True)
        self.__editor.setMarginWidth(1, '0000')
        self.__editor.setMarginsForegroundColor(QColor("#006400"))
        # 设置结束符是windows的\r\n 不设是默认\n
        # self.__editor.setEolMode(QsciScintilla.EolWindows)

        # 默认未修改
        self.__editor.setModified(False)

    # 这里是添加内容
    def addText(self, content):
        # 防止有憨憨放列表进来...
        input_content = ''
        if isinstance(content, list):
            if '\r' or '\n' in content:
                input_content = ''.join(content)
            else:
                input_content = '\n'.join(content)
        elif isinstance(content, str):
            input_content = content

        self.__editor.setText(input_content)

    # 得到当前文本
    def getText(self):
        content = self.__editor.text()
        print(type(content))
        print(content)
        return content

    # 得到编辑器当前状态
    def getStatus(self):
        # bool
        status = self.__editor.isModified()
        return status

    # 修改当前编辑器状态
    def changeStatus(self, flag):
        self.__editor.setModified(flag)

    # 得到搜索结果....
    def search_interface(self, keyword, *state):
        """
        obj = QsciScintilla()
        flag = obj.findFirst(self,expr,re,cs,wo,wrap,forward,line,index,show,posix,cxx11)->bool
        :param keyword: 你的关键词
        :param state: 元组(***)
        tips -> [虽然是 Any 但默认写 bool]
        expr: Any, --> 匹配词 keyword
        re: Any, --> 是否使用正则表达式匹配 -> 默认向后搜索 regexp
        cs: Any, --> 是否区分大小写匹配
        wo: Any, --> 是否匹配整个关键词 --> 不需要完整匹配 --> False
        wrap: Any, --> 是否在匹配结束之后回到搜索起点 --> 默认是 True
        forward: bool, --> 向前搜索: False, 向后搜索: True; 一般是True即向后搜索... 这里注意不要搞反
        line: -1, --> 搜索的起始行号 表示从当前行开始... 0~N
        index: -1, --> 搜索的起始索引 表示从当前行的当前光标开始 0~N
        show: True, --> 是否显示搜索结果 默认高亮...显示
        posix: False, --> 是否使用POSIX正则表达式匹配 默认False
        username: False, --> 是否用用户名模式匹配 我的用户名: cxx11
        :return: bool --> 返回一个布尔值 表明是否找到...
        """
        return self.__editor.findFirst(keyword, *state)  # bool

    def search_interface_(self):
        # 直接找下一个....
        return self.__editor.findNext()

    def send_signal(self, parameter1, parameter2=None):
        v1 = getattr(self.__editor, parameter1)
        if parameter2 is None:
            return self.__editor.SendScintilla(v1)
        else:
            return self.__editor.SendScintilla(v1, parameter2)

    def send_signal_(self, item1, item2):
        item3 = self.__editor.SendScintilla(item2)
        return self.__editor.SendScintilla(item1, item3)

    # 必须搭配findFirst()/findNext()食用 在目标被选中的前提下替换
    def replace_interface(self, keywords):
        self.__editor.replace(keywords)

    def moveCursor(self, line, index):
        self.__editor.setCursorPosition(line, index)

    def highlight_text(self, positions):
        start_line, start_index, end_line, end_index = positions
        self.__editor.setSelectionBackgroundColor(QColor('#4169E1')) # 蓝
        self.__editor.setSelectionForegroundColor(QColor('#FF8C00')) # 橘
        self.__editor.setSelection(start_line, start_index, end_line, end_index)

    def getSelectionState(self):
        return self.__editor.getSelection()

    def getCursorLocation(self):
        return self.__editor.getCursorPosition()


# 用户自定义的lexer高亮
# 一定要写self.description(self,...)函数 否则直接拒绝构建
class MeLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(MeLexer, self).__init__(parent)
        # 父类是编辑器
        # 设置默认颜色
        # 设置默认背景
        # 设置默认字号
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#CCE8CF"))  # 背景 豆沙绿
        self.setDefaultFont(QFont("Consolas", 13))

        # 样式表 0-1-2-3-4
        # 0: 关键字 1: 运算符 2: 格式符 3: 数字 4: 默认 5: 注释
        # 颜色
        self.setColor(QColor("#3CB371"), 0)
        self.setColor(QColor("#6A5ACD"), 1)
        self.setColor(QColor("#20B2AA"), 2)
        self.setColor(QColor("#4169E1"), 3)
        self.setColor(QColor("#2D7C7F"), 4)
        self.setColor(QColor("#C0C0C0"), 5)

        # 字体 consolas DevC++的默认字体 字号自定
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 0)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 1)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 2)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 3)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 4)
        self.setFont(QFont("Consolas", 13), 5)
        self.font(5).setItalic(True)

        # 定义关键词列表
        self.keywords_list = [
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int',
            'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile',
            'while', 'bool', 'catch', 'class', 'const_cast', 'delete', 'dynamic_cast',
            'explicit', 'false', 'friend', 'inline', 'mutable', 'namespace', 'new',
            'operator', 'private', 'protected', 'public', 'reinterpret_cast',
            'static_cast', 'template', 'this', 'throw', 'true', 'try', 'typeid',
            'typename', 'using', 'virtual', 'wchar_t', 'include', 'std',
            "byte", "word", "dword",
            "int8_t", "uint8_t", "int16_t", "uint16_t",
            "int32_t", "uint32_t", "int64_t", "uint64_t",
            "int8", "uint8", "int16", "uint16",
            "int32", "uint32", "int64", "uint64"
        ]
        # 定义运算符列表
        self.operator_list = [
            '=',
            # Comparison
            '==', '!=', '<', '<=', '>', '>=',
            # Arithmetic
            '+', '-', '*', '/', '%',
            # In-place
            '+=', '-=', '*=', '/=', '%=',
            # Bitwise
            '^', '|', '&', '~', '>>', '<<', '"', '%s', '%f', '%d', '%ld'
        ]
        # 定义格式符列表
        self.format_list = [
            '{', '}', '(', ')', '[', ']', '#', ';', ','
        ]

    def description(self, style):
        if style == 0:
            return "keyword_style"
        elif style == 1:
            return "operate_style"
        elif style == 2:
            return "format_style"
        elif style == 3:
            return "number_style"
        elif style == 4:
            return "default_style"
        elif style == 5:
            return "tips_style"
        ### 无需返回值 但需要定义内容
        return ""

    def styleText(self, start, end):
        # 1. 初始化风格类
        self.startStyling(start)

        # 2. 切片数据
        text = self.parent().text()[start:end]

        # 3. 词法分析
        # p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")# /**/
        # p = re.compile(r"\*|\*|//.*?(?=\r?\n|$)|\s+|\w+|\W") # //
        p = re.compile(r"\*\/|\/\*|//.*?(?=\r?\n|$)|\s+|\w+|\W")  # // and /**/

        # 关键词列表里是这样的元组  (token_name, token_len) :（关键词内容,关键词长度）
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        # print(token_list)
        # 4. 风格化
        # 4.1 分支
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = True
        # 4.2 循环风格化
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                # 处于块注释状态，使用样式5进行风格化
                self.setStyling(token[1], 5)
                if token[0] == "*/":
                    multiline_comm_flag = False
            elif token[0].startswith("//"):
                line_number = self.parent().SendScintilla(self.parent().SCI_LINEFROMPOSITION, start)
                line_start = self.parent().SendScintilla(self.parent().SCI_POSITIONFROMLINE, line_number)
                line_end = self.parent().SendScintilla(self.parent().SCI_GETLINEENDPOSITION, line_number)
                self.startStyling(line_start)
                self.setStyling(line_end - line_start + 1, 5)
                break  # 结束循环，不再继续处理该行后面的内容
            else:
                # 其他情况根据关键词、运算符、格式符、数字进行风格化
                if token[0] in self.keywords_list:
                    self.setStyling(token[1], 0)
                elif token[0] in self.operator_list:
                    self.setStyling(token[1], 1)
                elif token[0] in self.format_list:
                    self.setStyling(token[1], 2)
                elif token[0].isdigit():
                    self.setStyling(token[1], 3)
                elif token[0] == "/*":
                    multiline_comm_flag = True
                    self.setStyling(token[1], 5)
                else:
                    self.setStyling(token[1], 4)

# if __name__ == '__main__':
#     app = QApplication([])
#
#     me_editor = TextEditorWidget('test.c')
#     me_editor.show()
#     path_c = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\test\init_data\test_cpp\test_data\test.c'
#     with open(path_c, 'r', encoding='utf-8') as file:
#         target_str = file.read()
#     file.close()
#     # print(target_str)
#     me_editor.addText(target_str)
#     app.exec_()
