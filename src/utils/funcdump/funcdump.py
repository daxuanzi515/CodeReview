import os
import re
from os.path import split

from clang.cindex import Config, Index, CursorKind, TypeKind
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
        self.translation_unit = self.index.parse(source_path)
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


# 头文件和源文件的封装类
class HeaderInfo:
    def __init__(self, ):
        pass




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
        name = '.' + name
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
    # 遍历所有同类型文件
    def find_all_files(self, filepath):
        directory, _ = os.path.split(filepath)
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp'):
                    file_list.append(os.path.abspath(os.path.join(root, file)))
        return file_list

    # 1.2 启动项
    def headers_runner(self, init_filename):
        source_path = self.virtualTempFile(init_filename)
        headers_path = self.find_dependencies(source_path)
        path, name = split(source_path)

        headers_objs = []
        for item in headers_path:
            header_path = path + '/' + item
            source_path = self.virtualTempFile(header_path)
            headers_analyzer = FunctionDump(source_path)
            headers_analyzer.analyseLauncher()
            # headers_analyzer.show_function_details()
            headers_objs.append((init_filename, header_path, headers_analyzer))
            os.remove(source_path)

        return headers_objs

    def exclude_headers_runner(self, init_filename):
        source_path = self.virtualTempFile(init_filename)
        analyzer = FunctionDump(source_path)
        analyzer.analyseLauncher()
        analyzer.show_function_details()
        os.remove(source_path)
        return analyzer

    def source_runner(self, init_filename):
        filelist = self.find_all_files(init_filename)
        source_info_list = []

        for file in filelist:
            headers_objs = []
            # 源文件
            source_path = self.virtualTempFile(file)
            headers_path = self.find_dependencies(source_path)
            path, name = split(source_path)
            for header in headers_path:
                header_path = path + '/' + header
                source_path_ = self.virtualTempFile(header_path)
                headers_analyzer = FunctionDump(source_path_)
                headers_analyzer.analyseLauncher()
                # headers_analyzer.show_function_details()
                headers_objs.append((file, header_path, headers_analyzer))
                os.remove(source_path_)

            analyzer = FunctionDump(source_path)
            analyzer.analyseLauncher()
            os.remove(source_path)
            # analyzer.show_function_details()

            per_source_info = SourceInfo(filepath=file, source_obj=analyzer, headers_obj_list=headers_objs)
            source_info_list.append(per_source_info)
        return source_info_list

    def newHumanJudger(self):
        init_data = self.source_runner(self.file_path)
        keyword = self.target_function_name

        for data in init_data:
            # 文件名
            filename = data.filepath
            path, name = split(filename)
            # 声明
            function_declaration_list = data.source_obj.function_declaration_list
            # 定义
            function_definition_list = data.source_obj.function_definition_list
            # 调用
            function_callexpress_list = data.source_obj.function_callexpress_list
            # 头文件
            headers_obj_list = data.headers_obj_list
            print('位于源文件: ', name)
            print('---声明---')
            for per_obj in function_declaration_list:
                if keyword == per_obj.function_name and per_obj.declared_contents:
                    print(per_obj.declared_contents)
                    print(per_obj.declared_location)
                    break
            print('---定义---')
            for per_obj in function_definition_list:
                if keyword == per_obj.function_name and per_obj.definition_contents:
                    print(per_obj.definition_contents)
                    print(per_obj.definition_location)
                    break
            print('---调用---')
            for per_obj in function_callexpress_list:
                if keyword == per_obj.function_name and per_obj.call_express_contents:
                    print(per_obj.call_express_contents)
                    print(per_obj.call_express_location)
                    break

            # 头文件遍历
            for per_obj in headers_obj_list:
                filepath, header_path, item = per_obj
                path, name = split(filepath)
                path, name_ = split(header_path)
                print(f'~~~被{name}调用的{name_}~~~')
                print('---声明---')
                # 声明
                for i in item.function_declaration_list:
                    if i.function_name == keyword and i.declared_contents:
                        print(i.declared_contents)
                        print(i.declared_location)
                        break
                print('---定义---')
                for i in item.function_definition_list:
                    if i.function_name == keyword and i.definition_contents:
                        print(i.definition_contents)
                        print(i.definition_location)
                        break

class SourceInfo:
    def __init__(self, filepath, source_obj=None, headers_obj_list=None):
        self.filepath = filepath
        self.source_obj = source_obj
        self.headers_obj_list = headers_obj_list

# 为了解决跳转到其他.c/.cpp文件的bug
if __name__ == "__main__":
    path = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\test\init_data\test_data\test_py\test_clang_ast\call_location\temp_combined_output.cpp'
    obj = FunctionPreprocessor(path, 'add')
    obj.exclude_headers_runner(path)
