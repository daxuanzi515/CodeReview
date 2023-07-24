class Test_AST:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.cmd = 'clang'

    def isCpp(self):
        import re
        cpp_pattern = '.*\.cpp$'
        c_pattern = '.*\.c$'
        h_pattern = '.*\.h$'
        if re.match(cpp_pattern, self.name) is not None:
            print('.cpp')
            self.cmd = 'clang++'
        elif re.match(c_pattern, self.name) is not None:
            print('.c')
        elif re.match(h_pattern, self.name) is not None:
            print('.h')

    def packet(self):
        import subprocess
        self.isCpp()
        ast_parameter = '-ast-dump'
        syntax_only = '-fsyntax-only'
        common_header_ignore = '-nostdinc'
        find_str = 'findstr'
        find_item = 'FunctionDecl'
        """
        TypedefDecl：表示类型定义（typedef）的声明。它将一个已有类型定义为一个新的类型别名。
        EnumDecl：表示枚举类型的声明。它包含枚举类型的名称、枚举常量等信息。
        EnumConstantDecl：表示枚举常量的声明。它包含枚举常量的名称和值等信息。
        RecordDecl ： 结构体声明语句
        FieldDecl：表示结构体或联合体的成员变量的声明。它包含成员变量的名称、类型等信息。
        UnionDecl：表示联合体的声明。它包含联合体的名称、成员变量等信息。
        ArraySubscriptExpr：表示数组下标表达式。它包含数组变量和下标表达式等信息。
        UnaryOperator：表示一元操作符表达式，如取地址（&）、解引用（*）、取反（-）等。
        BinaryOperator：表示二元操作符表达式，如加法（+）、减法（-）、乘法（*）等。
        IfStmt：表示条件语句（if语句）。它包含条件表达式、if语句块、else语句块等信息。
        ForStmt：表示循环语句（for循环）。它包含循环变量、循环条件、循环体等信息。
        WhileStmt：表示循环语句（while循环）。它包含循环条件、循环体等信息。
        ################################################
        TranslationUnitDecl：表示整个翻译单元（源代码文件）。
        FunctionDecl：表示函数声明。
        DeclStmt ：函数定义
        CallExpr ：表示函数调用表达式。它包含被调用的函数、实参列表等信息。
        VarDecl：表示变量声明。
        ParmVarDecl：表示函数参数声明。
        NamespaceDecl：表示命名空间的声明。
        UnaryOperator 一元操作
        CompoundStmt 代表大括号，函数实现、struct、enum、for的body等一般用此包起来。
        ReturnStmt 返回语句
        IntegerLiteral 整型
        """

        output = ""
        args = [self.cmd, '-Xclang', ast_parameter, syntax_only, common_header_ignore, self.path + '/' + self.name,]
                # '|', find_str, find_item]

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        while True:
            line = process.stdout.readline()
            if not line:
                break
            output += line.decode('gbk')  # 将回显内容添加到字符串中
        process.wait()

        return output


def run(absolute_path):
    from os.path import split
    import time
    path, name = split(absolute_path)
    test_obj = Test_AST(path, name)
    result = test_obj.packet()
    local_time = time.localtime()
    date_time = time.strftime("%Y_%m_%d_%H_%M_%S", local_time)
    with open('./log/res_{}.txt'.format(date_time), 'w', encoding='utf-8') as file:
        file.write(result)
        file.close()
    print('end!')

if __name__ == '__main__':
    path = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\test\init_data\test_data\test_py\test_clang_ast\test_no_headers.c'
    run(path)
