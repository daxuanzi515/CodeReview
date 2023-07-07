import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

## 不用QS的...
def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'header': format([0, 128, 0]),  # 头文件
    'd_header': format([60,179,113]),  # 头文件
    'keyword': format('#2E8B57', 'bold'),
    'operator': format([255, 140, 0]),  # 运算符
    'brace': format([255, 140, 0]),  # 符号
    'defclass': format([0, 80, 50], 'bold'),  # 类名
    'string': format([132, 26, 138]),  # 字符串
    'string2': format([132, 26, 138]),  # 字符串
    'comment': format([107, 147, 186]),  # 注释
    'self': format([150, 85, 140], 'italic'),  # 自身
    'numbers': format([42, 0, 255]),  # 数字
    'constant': format([202, 0, 202], 'bold'),  # 常量
    'deprecated': format([123, 23, 43], 'bold underline'),  # 弃用的成员
    'enums': format([128, 0, 255]),  # 枚举
    'fields': format([128, 0, 128]),  # 变量
    'return': format([255, 0, 85], 'bold'),  # return关键字
    'method_decl': format([255, 128, 64], 'bold'),  # 方法定义
    'method': format([0, 48, 96]),  # 方法
    'others': format([78, 123, 0]),  # 其他
    'static_fields': format([33, 0, 189], 'bold'),  # 静态变量
}


class CppHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the C/C++ language.
    """
    # header
    header = [
        'stdio.h', 'stdlib.h', 'math.h', 'string.h', 'time.h', 'ctype.h',
        'stdbool.h', 'assert.h', 'limits.h', 'float.h', 'stddef.h', 'errno.h',
        'signal.h', 'setjmp.h', 'stdarg.h', 'locale.h', 'wchar.h', 'time.h',
        'unistd.h', 'fcntl.h', 'sys/types.h', 'sys/stat.h', 'dirent.h',
        'pthread.h', 'semaphore.h', 'sys/socket.h', 'netinet/in.h',
        'arpa/inet.h', 'netdb.h', 'sys/time.h', 'sys/wait.h'
    ]
    # C/C++ keywords
    keywords = [
        'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int',
        'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
        'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile',
        'while', 'bool', 'catch', 'class', 'const_cast', 'delete', 'dynamic_cast',
        'explicit', 'false', 'friend', 'inline', 'mutable', 'namespace', 'new',
        'operator', 'private', 'protected', 'public', 'reinterpret_cast',
        'static_cast', 'template', 'this', 'throw', 'true', 'try', 'typeid',
        'typename', 'using', 'virtual', 'wchar_t',
    ]

    # C/C++ operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]
    # C/C++ braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []
        # Header rules: #include<XX.h>
        header_rules1 = [('#include\s*<{}>'.format(a), 0, STYLES['header'])
                         for a in CppHighlighter.header]
        # Header rules: #include "XXX.h"
        header_rules2 = [(r'#include\s*"([^"]+)"', 0, STYLES['d_header']),]

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CppHighlighter.keywords]
        # print(rules)
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CppHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CppHighlighter.braces]
        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string2']),
            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),
            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
             STYLES['numbers']),
        ]
        rules += header_rules1
        rules += header_rules2
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth) + expression.cap(nth).index(expression.cap(nth))
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

if __name__ == "__main__":
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication([])
    editor = QtWidgets.QPlainTextEdit()
    editor.setStyleSheet("""QPlainTextEdit{
        font-family:'Consolas'; 
        background-color: rgb(204,232,207);}""")
    highlight = CppHighlighter(editor.document())
    editor.show()

    # Load sample.cpp into the editor for demo purposes
    infile = open('test.c', 'r', encoding='utf-8')
    editor.setPlainText(infile.read())

    app.exec_()
