def create_nested_folders():
    import os
    # 绝对路径
    base_folder = './'

    # 嵌套文件夹列表
    nested_folders = [
        'data/exe',
        'data/reports/pdf',
        'data/reports/md',
        'data/reports/img',
        'data/reports/docx',
        'data/rules',
        'data/tags',
        'data/logs',
    ]

    for folder in nested_folders:
        folder_path = os.path.join(base_folder, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


if __name__ == '__main__':
    # 调用函数进行操作
    create_nested_folders()
