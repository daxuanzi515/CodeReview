import os
import re
from os.path import split


class Combine:
    def __init__(self, filepath):
        self.absolute_path = filepath

    def getSourceFiles(self):
        directory, _ = os.path.split(self.absolute_path)
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp'):
                    file_list.append(os.path.abspath(os.path.join(root, file)))
        return file_list

    def getHeaders(self, filename):
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

    def getContents(self, headers, source):
        # 按照
        # include<stdio.h>
        # include"test.h"
        pass

