from clang.cindex import Index, CursorKind, Config, TypeKind


class FunctionInfo:
    def __init__(self, name, kind, location, parameter_types=None, return_type=None, definition_location=None, definition_contents=None, call_locations=None, call_contents=None):
        self.name = name
        self.kind = kind
        self.location = location
        self.parameter_types = parameter_types or []
        self.return_type = return_type
        self.definition_location = definition_location
        self.definition_contents = definition_contents
        self.call_locations = call_locations or []
        self.call_contents = call_contents or []

    def add_parameter_type(self, parameter_type):
        self.parameter_types.append(parameter_type)

    def add_call_location(self, call_location):
        self.call_locations.append(call_location)

    def add_call_content(self, call_contents):
        self.call_contents.append(call_contents)

    def __repr__(self):
        return f"Function: {self.name}\nKind: {self.kind}\nLocation: {self.location}\nParameter Types: {self.parameter_types}\nReturn Type: {self.return_type}\nDefinition Location: {self.definition_location}\nDefinition Contents: {self.definition_contents}\nCall Locations: {self.call_locations}\nCall Contents: {self.call_contents}\n"

class FunctionAnalyzer:
    def __init__(self, source_path):
        self.clang_path = r'E:\formalFiles\LLVM\bin\libclang.dll'
        Config.set_library_file(self.clang_path)
        self.index = Index.create()
        self.translation_unit = self.index.parse(source_path)
        self.root_cursor = self.translation_unit.cursor
        self.function_info_list = []

    def analyze(self):
        self._analyze_cursor(self.root_cursor)

    def _analyze_cursor(self, cursor):
        if cursor.kind == CursorKind.FUNCTION_DECL:
            name = cursor.spelling
            kind = "Function Declaration"
            location = (cursor.extent.start.line, cursor.extent.start.column, cursor.extent.end.line, cursor.extent.end.column)
            parameter_types = self._get_parameter_types(cursor)
            return_type = self._get_return_type(cursor)

            function_info = FunctionInfo(name, kind, location, parameter_types, return_type)
            self.function_info_list.append(function_info)

            definition_cursor = cursor.get_definition()
            if definition_cursor:
                definition_location = (definition_cursor.extent.start.line, definition_cursor.extent.start.column, definition_cursor.extent.end.line, definition_cursor.extent.end.column)
                definition_contents = self._get_cursor_contents(definition_cursor)
                function_info.definition_location = definition_location
                function_info.definition_contents = definition_contents

            self._check_function_calls(self.root_cursor, name)

        for child in cursor.get_children():
            self._analyze_cursor(child)

    def _get_parameter_types(self, cursor):
        parameter_types = []
        for arg in cursor.get_arguments():
            arg_type = arg.type.spelling
            parameter_types.append(arg_type)
        if not parameter_types:
            return ["void"]  # 返回 "void" 字符串表示无参函数
        return parameter_types

    def _get_return_type(self, cursor):
        result_type = cursor.type
        if cursor.spelling == "main":
            return "int"
        elif result_type.kind == TypeKind.FUNCTIONPROTO:# 除了void以外的类型
            return_type = result_type.get_result().spelling
            return return_type
        elif result_type.kind == TypeKind.FUNCTIONNOPROTO:# void
            return_type = result_type.get_result().spelling
            return return_type
        return None

    def _get_cursor_contents(self, cursor):
        with open(cursor.location.file.name, 'r', encoding='utf-8') as file:
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

    def _check_function_calls(self, cursor, function_name):
        for child in cursor.get_children():
            self._check_function_calls(child, function_name)

        if cursor.kind == CursorKind.CALL_EXPR and cursor.spelling == function_name:
            call_location = (
                cursor.extent.start.line,
                cursor.extent.start.column,
                cursor.extent.end.line,
                cursor.extent.end.column,
            )
            call_contents = self._get_call_contents(cursor)  # 获取函数调用语句的内容
            function_info = self._find_function_info(function_name)
            if function_info:
                function_info.add_call_location(call_location)
                function_info.add_call_content(call_contents)

    def _get_call_contents(self, cursor):
        with open(cursor.extent.start.file.name, 'r', encoding='utf-8') as file:
            contents = file.readlines()
        start_line = cursor.extent.start.line - 1
        start_column = cursor.extent.start.column - 1
        end_line = cursor.extent.end.line - 1
        end_column = cursor.extent.end.column - 1

        call_contents = ""
        for line in range(start_line, end_line + 1):
            if line == start_line:
                call_contents += contents[line][start_column:]
            elif line == end_line:
                call_contents += contents[line][:end_column + 1]
            else:
                call_contents += contents[line]

        return call_contents

    def _find_function_info(self, function_name):
        for function_info in self.function_info_list:
            if function_info.name == function_name:
                return function_info
        return None

    def print_function_info(self):
        for function_info in self.function_info_list:
            print(function_info)

if __name__ == "__main__":
    source_path = "test_headers.cpp"

    analyzer = FunctionAnalyzer(source_path)
    analyzer.analyze()
    analyzer.print_function_info()
