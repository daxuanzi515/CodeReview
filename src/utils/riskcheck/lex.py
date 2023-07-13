import re

# token比较大的分类
TOKEN_STYLE = [
    'KEY_WORD', 'IDENTIFIER', 'DIGIT_CONSTANT',
    'OPERATOR', 'SEPARATOR', 'STRING_CONSTANT'
]

# 将关键字、运算符、分隔符进行具体化
DETAIL_TOKEN_STYLE = {
    'include': 'INCLUDE',
    'int': 'INT',
    'break': 'BREAK',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'goto': 'GOTO',
    'long': 'LONG',
    'bool': 'BOOL',
    'void': 'VOID',
    'float': 'FLOAT',
    'char': 'CHAR',
    'double': 'DOUBLE',
    'for': 'FOR',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'return': 'RETURN',
    '=': 'ASSIGN',
    '&': 'ADDRESS',
    '<': 'LT',
    '>': 'GT',
    '++': 'SELF_PLUS',
    '--': 'SELF_MINUS',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '>=': 'GET',
    '<=': 'LET',
    '(': 'LL_BRACKET',
    ')': 'RL_BRACKET',
    '{': 'LB_BRACKET',
    '}': 'RB_BRACKET',
    '[': 'LM_BRACKET',
    ']': 'RM_BRACKET',
    ',': 'COMMA',
    '"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON',
    '#': 'SHARP',
}

# 关键字
keywords = [
    ['int', 'float', 'double', 'char', 'void'],
    ['if', 'for', 'while', 'do', 'else'], ['include', 'return'],
]

# 运算符
operators = [
    '=', '&', '<', '>', '++', '--', '+', '-', '*', '/', '>=', '<=', '!='
]

# 分隔符
delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

# c文件名字
# file_name = None

# 文件内容
content = None

class Token(object):
    '''记录分析出来的单词'''

    def __init__(self, type_index, value, line):
        self.type = DETAIL_TOKEN_STYLE[value] if (
            type_index == 0 or type_index == 3 or type_index == 4
        ) else TOKEN_STYLE[type_index]
        self.value = value
        self.line = line

class Lexer(object):
    '''词法分析器'''

    def __init__(self):
        # 用来保存词法分析出来的结果
        self.tokens = []
        self.line = 1

    # 判断是否是空白字符
    def is_blank(self, index):
        if content[index] == '\n':
            self.line +=1
        return (
            content[index] == ' ' or
            content[index] == '\t' or
            content[index] == '\n' or
            content[index] == '\r'
        )

    # 跳过空白字符
    def skip_blank(self, index):
        while index < len(content) and self.is_blank(index):
            index += 1
        return index


    # 判断是否是关键字
    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    # 词法分析主程序
    def main(self):
        i = 0
        while i < len(content):
            i = self.skip_blank(i)
            # 如果是引入头文件，还有一种可能是16进制数，这里先不判断
            if content[i] == '#':
                self.tokens.append(Token(4, content[i], self.line))
                i = self.skip_blank(i + 1)
                # 分析这一引入头文件
                while i < len(content):
                    # 匹配"include"
                    if re.match('include', content[i:]):
                        # self.print_log( '关键字', 'include' )
                        self.tokens.append(Token(0, 'include', self.line))
                        i = self.skip_blank(i + 7)
                    # 匹配"或者<
                    elif content[i] == '"' or content[i] == '<':
                        # self.print_log( '分隔符', content[ i ] )
                        self.tokens.append(Token(4, content[i], self.line))
                       # i = self.skip_blank(i + 1)
                        #print(content[i])
                        close_flag = '"' if content[i] == '"' else '>'
                        i = self.skip_blank(i + 1)
                        #print(content[i])
                        # 找到include的头文件
                        lib = ''
                        while content[i] != close_flag:
                            lib += content[i]
                            i += 1
                        # self.print_log( '标识符', lib )
                        self.tokens.append(Token(1, lib, self.line))
                        # 跳出循环后，很显然找到close_flog
                        # self.print_log( '分隔符', close_flag )
                        self.tokens.append(Token(4, close_flag, self.line))
                        i = self.skip_blank(i + 1)
                        break
                    else:
                        exit()
            # 如果是字母或者是以下划线开头
            elif content[i].isalpha() or content[i] == '_':
                # 找到该字符串
                temp = ''
                while i < len(content) and (
                        content[i].isalpha() or
                        content[i] == '_' or
                        content[i].isdigit()):
                    temp += content[i]
                    i += 1
                # 判断该字符串
                if self.is_keyword(temp):
                    # self.print_log( '关键字', temp )
                    self.tokens.append(Token(0, temp, self.line))
                else:
                    # self.print_log( '标识符', temp )
                    self.tokens.append(Token(1, temp, self.line))
                i = self.skip_blank(i)
            # 如果是数字开头
            elif content[i].isdigit():
                temp = ''
                while i < len(content):
                    if content[i].isdigit() or (
                            content[i] == '.' and content[i + 1].isdigit()):
                        temp += content[i]
                        i += 1
                    elif not content[i].isdigit():
                        if content[i] == '.':
                            # print ('float number error!')
                            exit()
                        else:
                            break
                # self.print_log( '常量' , temp )
                self.tokens.append(Token(2, temp, self.line))
                i = self.skip_blank(i)
            # 如果是分隔符
            elif content[i] in delimiters:
                # self.print_log( '分隔符', content[ i ] )
                self.tokens.append(Token(4, content[i], self.line))
                # 如果是字符串常量
                if content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(content):
                        if content[i] != '\"':
                            temp += content[i]
                            i += 1
                        else:
                            break
                    else:
                        # print ('error:lack of \"')
                        exit()
                    # self.print_log( '常量' , temp )
                    self.tokens.append(Token(5, temp, self.line))
                    # self.print_log( '分隔符' , '\"' )
                    self.tokens.append(Token(4, '\"', self.line))
                i = self.skip_blank(i + 1)
            # 如果是运算符
            elif content[i] in operators:
                # 如果是++或者--
                if (content[i] == '+' or content[i] == '-') and (
                        content[i + 1] == content[i]):
                    # self.print_log( '运算符', content[ i ] * 2 )
                    self.tokens.append(Token(3, content[i] * 2, self.line))
                    i = self.skip_blank(i + 2)
                # 如果是>=或者<=
                elif (content[i] == '>' or content[i] == '<') and content[i + 1] == '=':
                    # self.print_log( '运算符', content[ i ] + '=' )
                    self.tokens.append(Token(3, content[i] + '=', self.line))
                    i = self.skip_blank(i + 2)
                # 其他
                else:
                    # self.print_log( '运算符', content[ i ] )
                    self.tokens.append(Token(3, content[i], self.line))
                    i = self.skip_blank(i + 1)

class Run_Lexer(object):
    def __init__(self, inFile):
        self.inFile = inFile

    def get_code(self):
        self.code = []
        lexer = Lexer()
        lexer.main()
        i = 0
        li = 0
        result = []
        result.append(li)
        result.append(self.inFile)
        while i < len(lexer.tokens):
            if lexer.tokens[i].line != li:
                self.code.append(result)
                while li !=lexer.tokens[i].line:
                    li += 1
                result = []
                result.append(li)
            result.append(lexer.tokens[i].value)
            i += 1
    def runLexer(self):
        sourseFile = open(self.inFile, 'r')
        global content
        content = sourseFile.read()
        # 需要注掉所有print否则全部输出在终端
        self.get_code()
