import os
from os.path import split

from docx2pdf import convert

from src.utils.report.generate_report import Generate2Word


class Convert:
    def __init__(self, tpl_file, config_ini, riskdatas, invalid, file_path, md_template):
        self.template_file = tpl_file
        self.config_ini = config_ini
        self.target_img = None
        self.pandoc_path = config_ini['main_project']['project_name'] + config_ini['report']['pandoc_path']
        self.pdf_path = config_ini['main_project']['project_name'] + config_ini['report']['pdf_path']
        self.md_path = config_ini['main_project']['project_name'] + config_ini['report']['markdown_path']
        self.riskdatas = riskdatas
        self.invalid = invalid
        self.md_template = md_template
        self.file_path = file_path
    def generate_report(self):
        demo = Generate2Word(tpl_file=self.template_file, config_ini=self.config_ini, riskdatas=self.riskdatas, invalid=self.invalid, file_path=self.file_path, md_template=self.md_template)
        input_file, self.target_img = demo.generate_reports()
        return input_file

    def convert_to_pdf(self, input_file):
        path, name = split(input_file)
        name = name.replace('.docx', '')
        output_file = self.pdf_path.format(name)
        file = open(output_file, "w")
        file.close()
        convert(input_file, output_file)
        return output_file

    def convert_to_md(self):
        demo = Generate2Word(tpl_file=self.template_file, config_ini=self.config_ini, riskdatas=self.riskdatas,
                             invalid=self.invalid, file_path=self.file_path, md_template=self.md_template)
        input_file, self.target_img = demo.generate_reports()
        os.remove(input_file)
        path, name = split(input_file)
        name = name.replace('.docx', '')
        output_file = self.md_path.format(name)
        a1, a2, a3 = demo.generate_md()
        with open(self.md_template, 'r', encoding='utf-8') as f:
            template = f.read()
            f.close()
        report0 = template.replace('{{table0}}', a1)
        report1 = report0.replace('{{table1}}', a2)
        report2 = report1.replace('{{table2}}', a3)
        import shutil
        target_path = self.md_path
        target_path = target_path.replace('{}.md', '')
        if self.target_img is not None:
            shutil.copy(self.target_img, target_path)
        path, name = split(self.target_img)
        md_report = report2.replace("{{chart}}", name)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
            f.close()
        return output_file