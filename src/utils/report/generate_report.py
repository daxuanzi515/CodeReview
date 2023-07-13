import os
import datetime
from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm
from src.utils.report.generate_img import PieChartGenerator

# 根据模板生成一个报告内容
class Generate2Word:
    def __init__(self, tpl_file, config_ini, riskdatas, invalid, file_path):
        self.now1 = str(datetime.date.today() - datetime.timedelta(days=0)).replace("-", "").replace(" ", "")
        self.nnow = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.now = self.now1[4:6] + '.' + self.now1[6:]  # 现在时间
        self.tpl_file = tpl_file
        self.config_ini = config_ini
        self.riskdatas = riskdatas
        self.invalid = invalid
        self.file_path = file_path
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
        code_type = self.file_path.split('.')[-1]
        insert_image1 = InlineImage(tpl, result3, width=Mm(140))
        len1 = len(self.riskdatas)
        len2 = len(self.invalid)
        length = len1 + len2
        context = {'data': self.nnow,
                   'leak_num': length,
                   'file_path': self.file_path,
                   "code_type": code_type,
                   'riskdatas': self.riskdatas,
                   'invalid': self.invalid,
                    "chart":insert_image1}  # 待替换对象

        # 渲染模板
        tpl.render(context)
        tpl.save(self.report_file)

        return self.report_file, result3



