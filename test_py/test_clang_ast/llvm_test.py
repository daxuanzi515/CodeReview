from clang.cindex import Index, TranslationUnit  # 主要API
from clang.cindex import Config  #配置
from clang.cindex import CursorKind  #索引结点的类别
from clang.cindex import TypeKind    #节点的语义类别

libclangPath = r"E:\formalFiles\LLVM\bin\libclang.dll"
#这个路径需要自己先在笔记本上安装
Config.set_library_file(libclangPath)

file_path_ = r"test_headers.cpp"
index = Index.create()

tu = index.parse(file_path_)

AST_root_node = tu.cursor  #cursor根节点

print(AST_root_node)
'''
前序遍历严格来说是一个二叉树才有的概念。这里指的是对于每个节点，先遍历本节点，再遍历子节点的过程。
'''
# node_list = []
# def preorder_travers_AST(cursor):
#     for cur in cursor.get_children():
#         #do something
#         print(cur.spelling)
#         preorder_travers_AST(cur)
#
# preorder_travers_AST(AST_root_node)


def iterAST(cursor):
    for cur in cursor.get_children():
        if cur.kind == CursorKind.FUNCTION_DECL:
            # 处理函数声明节点
            print("Function declaration:", cur.spelling)
            # 获取节点位置
            location = cur.location
            file_path = location.file.name if location.file else "Unknown"
            line = location.line if location.line != 0 else "Unknown"
            column = location.column if location.column != 0 else "Unknown"
            if file_path == file_path_:
                print("Location: File '{}', Line {}, Column {}".format(file_path, line, column))
            # 进一步处理子节点
            for cur_sub in cur.get_children():
                if cur_sub.kind == CursorKind.CALL_EXPR:
                    # 处理函数调用节点
                    print("Function call:", cur_sub.spelling)
                    # 获取节点位置
                    location_sub = cur_sub.location
                    file_path_sub = location_sub.file.name if location_sub.file else "Unknown"
                    line_sub = location_sub.line if location_sub.line != 0 else "Unknown"
                    column_sub = location_sub.column if location_sub.column != 0 else "Unknown"
                    if file_path_sub == file_path_:
                        print("Location: File '{}', Line {}, Column {}".format(file_path_sub, line_sub, column_sub))
        elif cur.kind == CursorKind.VAR_DECL:
            # 处理变量声明节点
            print("Variable declaration:", cur.spelling)
            # 获取节点位置
            location = cur.location
            file_path = location.file.name if location.file else "Unknown"
            line = location.line if location.line != 0 else "Unknown"
            column = location.column if location.column != 0 else "Unknown"
            print("Location: File '{}', Line {}, Column {}".format(file_path, line, column))
        # elif cur.kind == CursorKind.FIELD_DECL:
        #     # 处理字段声明节点
        #     print("Field declaration:", cur.spelling)
        #     # 获取节点位置
        #     location = cur.location
        #     file_path = location.file.name if location.file else "Unknown"
        #     line = location.line if location.line != 0 else "Unknown"
        #     column = location.column if location.column != 0 else "Unknown"
        #     print("Location: File '{}', Line {}, Column {}".format(file_path, line, column))
        # elif cur.kind == CursorKind.TYPEDEF_DECL:
        #     # 处理类型定义节点
        #     print("Typedef declaration:", cur.spelling)
        #     # 获取节点位置
        #     location = cur.location
        #     file_path = location.file.name if location.file else "Unknown"
        #     line = location.line if location.line != 0 else "Unknown"
        #     column = location.column if location.column != 0 else "Unknown"
        #     print("Location: File '{}', Line {}, Column {}".format(file_path, line, column))
        else:
            # 处理其他类型的节点
            print("Other node:", cur.spelling)
            # 获取节点位置
            location = cur.location
            file_path = location.file.name if location.file else "Unknown"
            line = location.line if location.line != 0 else "Unknown"
            column = location.column if location.column != 0 else "Unknown"
            if file_path == file_path_:
                print("Location: File '{}', Line {}, Column {}".format(file_path, line, column))

        # 递归处理子节点
        iterAST(cur)

# 调用 iterAST 函数，传入根节点进行遍历和分析
iterAST(AST_root_node)

#
# # 直接分词结束
# cursor_content = ""
# for token in AST_root_node.get_tokens():
# #针对一个节点，调用get_tokens的方法。
#     print(token.spelling)
# # 这个直接搞完？？？？？一刀秒杀了...

