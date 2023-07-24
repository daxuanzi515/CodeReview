import os
from os.path import split


class DefinitionCallExpressCombiner:
    def __init__(self, file_path, keyord=None):
        self.file_path = file_path
        if keyord:
            self.target_word = keyord
        self.headers = []
        self.main_sign = None
        self.definition_contents = []
        self.mix_contents = []
        self.main_length = 0
        self.offset_length = 0

    def find_all_files(self, filepath):
        directory, _ = os.path.split(filepath)
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp'):
                    file_list.append(os.path.abspath(os.path.join(root, file)))
        return file_list

    def has_main_function(self, file_path):
        with open(file_path, "r") as file:
            content = file.read()
            return "int main(" in content

    def getDefinitionCodes(self):
        source_files = self.find_all_files(self.file_path)
        for file_path in source_files:
            with open(file_path, "r") as file:
                content = file.readlines()
                if self.has_main_function(file_path):
                    if self.main_sign is None:
                        self.main_sign = file_path
                    else:
                        print('main function is None.')
                else:
                    self.definition_contents += content

    def Combiner(self):
        self.getDefinitionCodes()
        path, name = split(self.main_sign)
        name = '.' + name
        temp_path = os.path.join(path, name)
        with open(self.main_sign, "r", encoding='utf-8') as main_file:
            main_file_content = main_file.readlines()
            self.main_length = len(main_file_content)

        last_line = self.definition_contents[-1]
        if last_line == '}\n':
            pass
        elif last_line == '}':
            self.definition_contents[-1] = '}\n'
        if main_file_content:
            self.mix_contents = self.definition_contents + main_file_content

        new_data = ["//" + line if line.startswith("#include") else line for line in self.mix_contents]
        with open(temp_path, 'w', encoding='utf-8') as temp_obj:
            temp_obj.writelines(new_data)
        print(new_data)
        self.offset_length = len(new_data) - self.main_length


if __name__ == "__main__":
    filepath = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\test\init_data\test_data\test_py\test_clang_ast\call_location\main.cpp'
    obj = DefinitionCallExpressCombiner(filepath)
    obj.Combiner()
    offset = obj.offset_length
    main_length = obj.main_length
    print(main_length)
    print(offset)
