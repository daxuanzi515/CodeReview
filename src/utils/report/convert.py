import os
from os.path import split

from docx2pdf import convert
import subprocess
from src.utils.report.generate_report import Generate2Word
class Convert:
    def __init__(self, tpl_file, config_ini):
        self.template_file = tpl_file
        self.config_ini = config_ini
        self.target_img = None
        self.pandoc_path = config_ini['main_project']['project_name'] + config_ini['report']['pandoc_path']
        self.pdf_path = config_ini['main_project']['project_name'] + config_ini['report']['pdf_path']
        self.md_path = config_ini['main_project']['project_name'] + config_ini['report']['markdown_path']
    def generate_report(self):
        demo = Generate2Word(tpl_file=self.template_file, config_ini=self.config_ini)
        input_file, self.target_img = demo.generate_reports()
        return input_file
    def convert_to_pdf(self, input_file):
        path, name = split(input_file)
        name = name.replace('.docx','')
        output_file = self.pdf_path.format(name)
        file = open(output_file, "w")
        file.close()
        convert(input_file, output_file)
        return output_file
    def convert_to_md(self, input_file):
        path, name = split(input_file)
        name = name.replace('.docx','')
        output_file = self.md_path.format(name)
        # 复制图片到md的文件夹 保证图片路径在md文件夹下 即md文件和图片在一起
        import shutil
        target_path = self.md_path
        target_path = target_path.replace('{}.md', '')
        if self.target_img is not None:
            shutil.copy(self.target_img, target_path)
        subprocess.run([self.pandoc_path, input_file, "-o", output_file])
        return output_file
