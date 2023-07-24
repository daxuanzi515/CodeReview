import os


def get_all_c_cpp_files(folder_path):
    c_cpp_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".c") or filename.endswith(".cpp"):
            c_cpp_files.append(filename)
    return c_cpp_files


def extract_functions_from_content(content):
    functions = []
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("int ") or line.strip().startswith("void ") or line.strip().startswith("bool "):
            function_name = line.split("(")[0].split()[-1]
            functions.append((function_name, i))
    return functions


def has_main_function(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        return "int main(" in content


def extract_headers_from_content(content):
    headers = set()
    lines = content.split("\n")
    for line in lines:
        if line.startswith("#include"):
            headers.add(line)
    return headers


def calculate_lines(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        l = file.readlines()
    return len(l)


def main():
    folder_path = "."  # 当前文件夹
    main_file_path = None

    all_headers = set()
    other_files = []

    for filename in get_all_c_cpp_files(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as file:
            content = file.read()
            if has_main_function(file_path):
                if main_file_path is None:
                    main_file_path = file_path
                else:
                    print(
                        f"Warning: Multiple files with main function found. Keeping main function in {main_file_path}.")
            else:
                # headers = extract_headers_from_content(content)
                # all_headers.update(headers)
                other_files.append(content)

    if main_file_path is None:
        print("Error: No file with main function found.")
        return

    # combined_headers = "\n".join(all_headers)
    #
    # # 注释掉所有头文件
    # for header in all_headers:
    #     combined_headers = combined_headers.replace(header, f"// {header}")

    others_len = 0
    main_len = 0
    # 将其他文件的内容合并到一个临时文件中
    with open("temp_combined_output.cpp", "w") as temp_output_file:
        for content in other_files:
            temp_output_file.write(content)
        temp_output_file.write('\n')

        with open(main_file_path, "r") as main_file:
            main_file_content = main_file.readlines()
            main_len = len(main_file_content)
            temp_output_file.writelines(main_file_content)

    f = open('temp_combined_output.cpp','r', encoding='utf=8')
    l = f.readlines()
    others_len = len(l)
    new_data = ["//" + line if line.startswith("#include") else line for line in l]

    # for i in l:
    #     if i.startswith("#include"):
    #         data = "//" + i
    #         new_data.append(data)
    #     else:
    #         new_data.append(i)
    print(main_len)
    print(others_len)
    print(others_len - main_len)
    offset = others_len - main_len
    # 行数 - offset ----> start_line - offset , end_line - offset
    f = open('temp_combined_output.cpp','w', encoding='utf=8')
    f.writelines(new_data)


if __name__ == "__main__":
    main()
