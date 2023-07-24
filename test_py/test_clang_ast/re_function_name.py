
# def extract_function_name(input_string):
#     import re
#     pattern = r'\b(\w+)\s*\('
#     match = re.search(pattern, input_string)
#     if match:
#         return match.group(1)
#     words = re.findall(r'\b\w+\b', input_string)  # 提取字符串中的单词列表
#     for word in words:
#         if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):  # 判断单词是否符合函数名的命名规则
#             return word  # 返回第一个符合要求的单词作为函数名
#     return None
#
# if __name__ == '__main__':
#     # 示例用法
#     inputs = [
#         "add",                # 输入函数名
#         "add(1,2)",           # 输入不完整的函数调用表达式
#         "a = add(1,2);",      # 输入完整的赋值语句
#         "= add(1,2);",        # 输入不完整的赋值语句
#         " add(1,2) ",         # 输入带空格的内容
#         "asd",                 # 输入可能的函数名
#         "Q_12(1,1", # 不完整的带下划线的函数调用表达式
#         "int res = sum(100)", # 完整的赋值语句
#         "int res = sum(100) + sub(200);", # 联合函数赋值语句 默认第一个...
#         "res += add(1, 2)",
#     ]
#
#     for input_str in inputs:
#         function_name = extract_function_name(input_str)
#         print(function_name)

# import re
#
# pattern = r'#include\s*["<]\s*test\.h\s*[">]'
# text = '''
# #include "test.h"
# #include "example.hpp"
# #include <iostream>
# #include <vector>
# '''
#
# matches = re.findall(pattern, text)
# for match in matches:
#     print(match)
import re
pattern = r'.*\n'
test = [
    'a\n',
    '}\n',
    ';\n',
    '\n',
    'int su;\n',
]
for i in test:
    matches = re.findall(pattern, i)
    if matches:
        print(i)