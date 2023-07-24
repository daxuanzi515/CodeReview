import os
import re
from os.path import split

from clang.cindex import Index, Config, CursorKind, TypeKind, TranslationUnit

clang_path = r'E:\formalFiles\LLVM\bin\libclang.dll'
Config.set_library_file(clang_path)

class FunctionDeclaration:
    def __init__(self, function_name=None, declared_location=None, declared_contents=None, return_types=None,
                 parameter_types=None):
        self.function_name = function_name
        self.declared_location = declared_location
        self.declared_contents = declared_contents
        self.return_types = return_types
        self.parameter_types = parameter_types
        self.kind = 'FUNCTION_DELCARATION'

    def __repr__(self):
        return f"函数名字: {self.function_name}\n函数语句类别: {self.kind}\n函数声明位置: {self.declared_location}\n" \
               f"函数参数类型: {self.parameter_types}\n函数返回值类型: {self.return_types}\n"


class FunctionDefinition:
    def __init__(self, function_name=None, definition_location=None, definition_contents=None):
        self.function_name = function_name
        self.definition_location = definition_location
        self.definition_contents = definition_contents
        self.kind = 'FUNCTION_DEFINITION'

    def __repr__(self):
        return f"函数名字: {self.function_name}\n函数语句类别: {self.kind}\n" \
               f"函数定义位置: {self.definition_location}\n函数定义内容: {self.definition_contents}\n"


class FunctionCallExpress:
    def __init__(self, function_name=None, call_express_location=None, call_express_contents=None):
        self.function_name = function_name
        self.call_express_location = call_express_location
        self.call_express_contents = call_express_contents
        self.kind = 'FUNCTION_CALLEXPRESS'

    def __repr__(self):
        return f"函数名字: {self.function_name}\n函数语句类别: {self.kind}\n" \
               f"函数调用位置: {self.call_express_location}\n函数调用内容: {self.call_express_contents}\n"


class FunctionDump:
    def __init__(self, source_path):
        self.index = Index.create()
        self.translation_unit = self.index.parse(source_path) #options=TranslationUnit.PARSE_SKIP_PREAMBLE)
        self.root_cursor = self.translation_unit.cursor
        self.function_declaration_list = []
        self.function_definition_list = []
        self.function_callexpress_list = []
        self.source_path = source_path

    # 启动函数
    def analyseLauncher(self):
        self.analyseRunner(self.root_cursor)

    # 实施函数
    def analyseRunner(self, cursor):
        if cursor.kind == CursorKind.FUNCTION_DECL or cursor.kind == CursorKind.CXX_METHOD:
            if not cursor.is_definition():
                name = cursor.spelling
                location = (
                    cursor.extent.start.line, cursor.extent.start.column, cursor.extent.end.line, cursor.extent.end.column)
                parameter_types = self.get_parameter_types(cursor)
                return_type = self.get_return_type(cursor)
                function_declaration = FunctionDeclaration(function_name=name, declared_location=location,
                                                           declared_contents=self.get_node_contents(cursor),
                                                           return_types=return_type,
                                                           parameter_types=parameter_types)
                self.function_declaration_list.append(function_declaration)

            definition_cursor = cursor.get_definition()
            if definition_cursor:
                definition_location = (definition_cursor.extent.start.line, definition_cursor.extent.start.column,
                                       definition_cursor.extent.end.line, definition_cursor.extent.end.column)
                definition_contents = self.get_node_contents(definition_cursor)

                function_definition = FunctionDefinition(function_name=definition_cursor.spelling,
                                                         definition_location=definition_location,
                                                         definition_contents=definition_contents)
                self.function_definition_list.append(function_definition)
                # 这句放里面还是外面？？？？
            self.check_function_calls(self.root_cursor, cursor.spelling)# 这句


        for child in cursor.get_children():
            self.analyseRunner(child)

    def check_function_calls(self, cursor, function_name):
        if cursor.kind == CursorKind.CALL_EXPR and cursor.spelling == function_name:
            call_location = (
                cursor.extent.start.line,
                cursor.extent.start.column,
                cursor.extent.end.line,
                cursor.extent.end.column,
            )
            call_contents = self.get_node_contents(cursor)  # 获取函数调用语句的内容
            function_callexpress = FunctionCallExpress(function_name=function_name, call_express_location=call_location,
                                                       call_express_contents=call_contents)
            self.function_callexpress_list.append(function_callexpress)

        for child in cursor.get_children():
            self.check_function_calls(child, function_name)

    # 参数类型过滤
    def get_parameter_types(self, cursor):
        parameter_types = []
        for arg in cursor.get_arguments():
            arg_type = arg.type.spelling
            parameter_types.append(arg_type)
        if not parameter_types:
            return ["void"]  # 返回 "void" 字符串表示无参函数
        return parameter_types

    # 返回值过滤
    def get_return_type(self, cursor):
        result_type = cursor.type
        if cursor.spelling == "main":
            return "int"
        elif result_type.kind == TypeKind.FUNCTIONPROTO:  # 除了void以外的类型
            return_type = result_type.get_result().spelling
            return return_type
        elif result_type.kind == TypeKind.FUNCTIONNOPROTO:  # void
            return_type = result_type.get_result().spelling
            return return_type
        return None

    # 返回节点内容
    def get_node_contents(self, cursor):
        with open(self.source_path, 'r', encoding='utf-8') as file:
            contents = file.readlines()
        start_line = cursor.extent.start.line - 1
        start_column = cursor.extent.start.column - 1
        end_line = cursor.extent.end.line - 1
        end_column = cursor.extent.end.column - 1
        # print(start_line, start_column, end_line, end_column)

        cursor_contents = ""
        for line in range(start_line, end_line + 1):
            if line == start_line:
                cursor_contents += contents[line][start_column:]
            elif line == end_line:
                cursor_contents += contents[line][:end_column + 1]
            else:
                cursor_contents += contents[line]
        return cursor_contents

    # 查找调用函数


    def show_function_details(self):
        ### 函数声明
        print('~~函数声明~~')
        for item in self.function_declaration_list:
            print(item)
        print('~~函数定义~~')
        for item in self.function_definition_list:
            print(item)
        print('~~函数调用~~')
        for item in self.function_callexpress_list:
            print(item)


# 封装预处理器 找到源文件未出现的函数声明....在头文件里进行查找...
class FunctionPreprocessor:
    def __init__(self, file_path, keyword=None):
        self.file_path = file_path
        self.target_function_name = keyword
        self.headers_list = None
        self.exclude_headers_list = None

    # 产生除去头文件的临时文件XXX_.c/.cpp
    def virtualTempFile(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.readlines()
        temp_contents = []
        # 注释头文件....
        for item in contents:
            if item.startswith('#include'):
                item = '//' + item  # 在头文件行之前添加注释符号
            temp_contents.append(item)
        path, name = split(filename)
        name = name.replace(".", "_.")
        new_filename = os.path.join(path, name)
        with open(new_filename, 'w', encoding='utf-8') as file:
            file.writelines(temp_contents)
        return new_filename

    # 获取源文件的所有头文件列表
    def find_dependencies(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.readlines()
        headers = []
        pattern = r'#include\s*["]\s*(\w+\.h)\s*["]'
        for item in contents:
            match = re.search(pattern, item)
            if match:
                dependency = match.group(1)
                headers.append(dependency)
        return headers

    # 1.2 启动项
    def headers_runner(self, init_filename):
        source_path = self.virtualTempFile(init_filename)
        headers_path = self.find_dependencies(source_path)
        headers_objs = []
        for item in headers_path:
            headers_analyzer = FunctionDump(item)
            headers_analyzer.analyseLauncher()
            # headers_analyzer.show_function_details()
            headers_objs.append((item, headers_analyzer))

        return headers_objs

    def exclude_headers_runner(self, init_filename):
        source_path = self.virtualTempFile(init_filename)
        analyzer = FunctionDump(source_path)
        analyzer.analyseLauncher()
        # analyzer.show_function_details()
        os.remove(source_path)
        return analyzer

    def analyseHeaderDECL_DEFI(self, init_filename, keyword):
        print('--------------头文件-----------------')
        headers_tuple = self.headers_runner(init_filename)  # 可能是函数的声明和定义

        print('--------------除了头文件----------------')
        exclude_headers_objs = self.exclude_headers_runner(init_filename)  # 可能是函数的定义和调用

        # 模拟查找
        # flag = False # 在头文件里
        # flag = True # 在当前的文件里
        # target_function_name 选中要查找的函数名字

        target_function_name = keyword
        declared_flag = True
        defined_flag = True
        # 获得源文件的函数声明列表 函数定义列表
        declared_function_names = [item.function_name for item in exclude_headers_objs.function_declaration_list]
        defined_function_names = [item.function_name for item in exclude_headers_objs.function_definition_list]

        if target_function_name not in declared_function_names:
            declared_flag = False
        if target_function_name not in defined_function_names:
            defined_flag = False

        path, name = split(init_filename)
        # 这里是只检测头文件的函数声明、定义的
        if not declared_flag:
            for item in headers_tuple:
                header_path, header_obj = item
                for declared_obj in header_obj.function_declaration_list:
                    if declared_obj.function_name == target_function_name and declared_obj.declared_contents is not None:
                        print(f'~~~这里是{header_path}头文件的{target_function_name}函数声明~~~')
                        print(declared_obj.declared_contents)
                        print(declared_obj.declared_location)
        # 这里加上源文件的
        elif declared_flag:
            for item in exclude_headers_objs.function_declaration_list:
                if item.function_name == target_function_name and item.declared_contents is not None:
                    print(f'~~~这里是{name}源文件的函数{target_function_name}声明~~~')
                    print(item.declared_contents)
                    print(item.declared_location)

        if not defined_flag:
            for item in headers_tuple:
                header_path, header_obj = item
                for defined_obj in header_obj.function_definition_list:
                    if defined_obj.function_name == target_function_name and defined_obj.definition_contents is not None:
                        print(f'~~~这里是{header_path}头文件的{target_function_name}函数定义~~~')
                        print(defined_obj.definition_contents)
                        print(defined_obj.definition_location)
        elif defined_flag:
            for item in exclude_headers_objs.function_definition_list:
                if item.function_name == target_function_name and item.definition_contents is not None:
                    print(f'~~~这里是{name}源文件的函数{target_function_name}定义~~~')
                    print(item.definition_contents)
                    print(item.definition_location)

        print(f'~~~这里是{name}源文件的函数{target_function_name}调用~~~')
        for item in exclude_headers_objs.function_callexpress_list:
            if item.function_name == target_function_name and item.call_express_contents is not None:
                print(item.call_express_contents)
                print(item.call_express_location)






def VirtualTempFile(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        contents = file.readlines()
    temp_contents = []
    # 注释头文件....
    for item in contents:
        if item.startswith('#include'):
            item = '//' + item # 在头文件行之前添加注释符号
        temp_contents.append(item)
    path, name = split(filename)
    name = name.replace(".", "_.")
    new_filename = os.path.join(path, name)
    with open(new_filename, 'w', encoding='utf-8') as file:
        file.writelines(temp_contents)
    return new_filename


def headers_runner(init_filename):
    source_path = VirtualTempFile(init_filename)
    headers_path = find_dependencies(source_path)
    headers_objs = []
    for item in headers_path:
        headers_analyzer = FunctionDump(item)
        headers_analyzer.analyseLauncher()
        headers_analyzer.show_function_details()
        headers_objs.append((item, headers_analyzer))

    return headers_objs



def exclude_headers_runner(init_filename):
    source_path = VirtualTempFile(init_filename)
    analyzer = FunctionDump(source_path)
    analyzer.analyseLauncher()
    analyzer.show_function_details()
    os.remove(source_path)
    return analyzer


def find_dependencies(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        contents = file.readlines()
    headers = []
    pattern = r'#include\s*["]\s*(\w+\.h)\s*["]'
    for item in contents:
        match = re.search(pattern, item)
        if match:
            dependency = match.group(1)
            headers.append(dependency)
    return headers

def before(init_filename):
    print('--------------头文件-----------------')
    # headers_tuple = headers_runner(init_filename) # 可能是函数的声明和定义

    list_ = SelectAllfiles(init_filename)
    print('--------------除了头文件----------------')
    exclude_headers_objs = []
    headers_objs = []
    if len(list_) > 1:
        for i in range(len(list_)):
            temp_obj = exclude_headers_runner(list_[i])
            exclude_headers_objs.append(temp_obj)
            headers_tuple = headers_runner(list_[i])
            headers_objs.append(headers_tuple)
    else:
        headers_objs = headers_runner(init_filename)
        exclude_headers_objs = exclude_headers_runner(init_filename) # 可能是函数的定义和调用

    if exclude_headers_objs != [] and headers_objs != []:
        return headers_objs, exclude_headers_objs
    return headers_objs, exclude_headers_objs

def judge_type(inputobj):
    pass

def run_all(init_filename, keyword):
    pass

def run_single(init_filename,keyword):
    # 模拟查找
    # flag = False # 在头文件里
    # flag = True # 在当前的文件里
    # target_function_name 选中要查找的函数名字
    headers_objs, exclude_headers_objs = before(init_filename=init_filename)
    target_function_name = keyword
    declared_flag = True
    defined_flag = True
    # 获得源文件的函数声明列表 函数定义列表
    declared_function_names = [item.function_name for item in exclude_headers_objs.function_declaration_list]
    defined_function_names = [item.function_name for item in exclude_headers_objs.function_definition_list]

    if target_function_name not in declared_function_names:
        declared_flag = False
    if target_function_name not in defined_function_names:
        defined_flag = False

    path, name = split(init_filename)
    # 这里是只检测头文件的函数声明、定义的
    if not declared_flag:
        for item in headers_objs:
            header_path, header_obj = item
            for declared_obj in header_obj.function_declaration_list:
                if declared_obj.function_name == target_function_name and declared_obj.declared_contents is not None:
                    print(f'~~~这里是{header_path}头文件的{target_function_name}函数声明~~~')
                    print(declared_obj.declared_contents)
                    print(declared_obj.declared_location)
    # 这里加上源文件的
    elif declared_flag:
        for item in exclude_headers_objs.function_declaration_list:
            if item.function_name == target_function_name and item.declared_contents is not None:
                print(f'~~~这里是{name}源文件的函数{target_function_name}声明~~~')
                print(item.declared_contents)
                print(item.declared_location)

    if not defined_flag:
        for item in headers_objs:
            header_path, header_obj = item
            for defined_obj in header_obj.function_definition_list:
                if defined_obj.function_name == target_function_name and defined_obj.definition_contents is not None:
                    print(f'~~~这里是{header_path}头文件的{target_function_name}函数定义~~~')
                    print(defined_obj.definition_contents)
                    print(defined_obj.definition_location)
    elif defined_flag:
        for item in exclude_headers_objs.function_definition_list:
            if item.function_name == target_function_name and item.definition_contents is not None:
                print(f'~~~这里是{name}源文件的函数{target_function_name}定义~~~')
                print(item.definition_contents)
                print(item.definition_location)

    print(f'~~~这里是{name}源文件的函数{target_function_name}调用~~~')
    for item in exclude_headers_objs.function_callexpress_list:
        if item.function_name == target_function_name and item.call_express_contents is not None:
            print(item.call_express_contents)
            print(item.call_express_location)


def SelectAllfiles(filepath):
    directory, _ = os.path.split(filepath)
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.c') or file.endswith('.cpp'):
                file_list.append(os.path.abspath(os.path.join(root, file)))
    return file_list

if __name__ == "__main__":
    path = 'radio.cpp' # 把实现写在.h里就不能实现查找调用 好典
    keyword = 'func'
    run_single(path, keyword)