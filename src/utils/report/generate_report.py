import os
import datetime
from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm
from src.utils.report.generate_img import PieChartGenerator

# 根据模板生成一个报告内容
class Generate2Word:
    def __init__(self, tpl_file, config_ini, riskdatas, invalid, file_path, md_template):
        self.now1 = str(datetime.date.today() - datetime.timedelta(days=0)).replace("-", "").replace(" ", "")
        self.nnow = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.now = self.now1[4:6] + '.' + self.now1[6:]  # 现在时间
        self.tpl_file = tpl_file
        self.config_ini = config_ini
        self.riskdatas = riskdatas
        self.invalid = invalid
        self.file_path = file_path
        self.md_template = md_template
        self.report_file = (config_ini['main_project']['project_name']+config_ini['report']['word_path']).format(self.nnow)

    def DP(self):
        # 数据处理
        img = PieChartGenerator(riskdatas=self.riskdatas, invaliddatas=self.invalid, config_ini=self.config_ini)
        # img = PieChartGenerator(datas, self.config_ini)
        folder_path = img.generate_image()
        return folder_path

    def generate_reports(self):
        # 生成报告
        tpl = DocxTemplate(self.tpl_file)
        result3 = self.DP()
        self.code_type = self.file_path.split('.')[-1]
        self.insert_image1 = InlineImage(tpl, result3, width=Mm(140))
        len1 = len(self.riskdatas)
        len2 = len(self.invalid)
        self.length = len1 + len2
        context = {'data': self.nnow,
                   'leak_num': self.length,
                   'file_path': self.file_path,
                   "code_type": self.code_type,
                   'riskdatas': self.riskdatas,
                   'invalid': self.invalid,
                    "chart":self.insert_image1}  # 待替换对象

        # 渲染模板
        tpl.render(context)
        tpl.save(self.report_file)
        return self.report_file, result3

    def generate_md(self):
        table0_data = '| 检测时间 | 文件路径 | 缺陷数 | 语言类型 |\n'
        table0_data += '| :------: | :----: | :------: | :------: |\n'
        table0_data += f'| {self.nnow} | {self.file_path} | {self.length} | {self.code_type} |\n'

        table1_data = '| 文件路径 | 行数 | 名称 | 风险水平 | 解决方式 |\n'
        table1_data += '| :----: | :------: | :------: | :------: | :------: |\n'
        for item in self.riskdatas:
            table1_data += f'| {self.file_path} | {self.length} | {item["func"]} | {item["rank"]} | {item["remedy"]} |\n'

        table2_data = '| 文件路径 | 行数 | 名称 |\n'
        table2_data += '| :----: | :------: | :------: |\n'
        for item in self.invalid:
            table2_data += f'| {self.file_path} | {self.length} | {item["func"]} |\n'

        return table0_data, table1_data, table2_data
        # with open(self.md_template, 'r', encoding='utf-8') as f:
        #     template = f.read()
        #     f.close()
        #
        # report0 = template.replace('{{table0}}', table0_data)
        # report1 = report0.replace('{{table1}}', table1_data)
        # report2 = report1.replace(' {{table2}}', table2_data)
        # img_path = self.DP()
        # md_report = report2.replace("{{chart}}", img_path)
