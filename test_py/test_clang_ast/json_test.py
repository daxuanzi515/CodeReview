import json
from clang.cindex import Index, Config, CursorKind

class AST_Tree_json:
    def __init__(self, absolute_path):
        self.absolute_path = absolute_path
        self.clang_path = r'E:\formalFiles\LLVM\bin\libclang.dll'
        Config.set_library_file(self.clang_path)
        self.AST_Root = Index.create().parse(absolute_path).cursor

    def serialize_node(self, cursor):
        node_dict = {
            "kind": str(cursor.kind),
            "location": [cursor.extent.start.line, cursor.extent.start.column,
                         cursor.extent.end.line, cursor.extent.end.column],
            "children": []
        }

        if cursor.spelling:
            node_dict["spelling"] = cursor.spelling
            print('keywords: ', cursor.spelling)
            print('location: ', cursor.extent.start.line, cursor.extent.start.column,
                                                    cursor.extent.end.line, cursor.extent.end.column)
            operator_text = self.get_operator_words(cursor.extent.start.line,cursor.extent.start.column,
                                                    cursor.extent.end.line, cursor.extent.end.column)
            print('contents: ', operator_text)
            node_dict["contents"] = operator_text
            # node_dict["area_text"] = operator_text

        for child in cursor.get_children():
            child_dict = self.serialize_node(child)
            node_dict["children"].append(child_dict)

        return node_dict

    def get_operator_words(self, s_line,s_index, e_line, e_index):
        with open(self.absolute_path, 'r', encoding='utf-8') as file:
            contents = file.readlines()
        file.close()

        operator_text = ''

        for i in range(s_line - 1, e_line):
            start_index = s_index - 1 if i == s_line - 1 else 0
            end_index = e_index if i == e_line - 1 else len(contents[i])
            operator_text += contents[i][start_index:end_index]

        return operator_text


    def start(self):
        string_res = self.serialize_node(self.AST_Root)
        serialized_json = json.dumps(string_res, indent=4, ensure_ascii=False)
        import time
        local_time = time.localtime()
        date_time = time.strftime("%Y_%m_%d_%H_%M_%S", local_time)
        with open('./log/res_{}.json'.format(date_time),'w', encoding='utf-8') as file:
            file.write(serialized_json)
            file.close()
        # 虽然但是它能识别[]{};+-=，不能获取它们的标识符....而且获取不到值....

        # print(serialized_json)

if __name__ == '__main__':
    # path = r'test_headers.c'
    # ast_obj = AST_Tree_json(path)
    # ast_obj.start()
    # path = '../test_clang_ast/log/test.cpp'
    path = './func.h'
    # path = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\test\init_data\test_data\test_py\test_clang_ast\log\test.cpp'
    f = open(path, 'r', encoding='utf-8')
    data = f.readlines()
    print(data)





