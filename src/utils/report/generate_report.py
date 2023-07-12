import os
import datetime
from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm
from src.utils.report.generate_img import PieChartGenerator

# 根据模板生成一个报告内容
class Generate2Word:
    def __init__(self,tpl_file, config_ini):
        self.now1=str(datetime.date.today() - datetime.timedelta(days=0)).replace("-", "").replace(" ", "")
        self.nnow = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.now = self.now1[4:6] + '.' + self.now1[6:]  # 现在时间
        self.tpl_file = tpl_file
        self.config_ini = config_ini
        self.report_file = (config_ini['main_project']['project_name']+config_ini['report']['word_path']).format(self.nnow)

    def DP(self):
        # 数据处理
        datas = [
            {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
            {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "Low"},
            {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
            {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "Medium"},
            {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
        ]
        img = PieChartGenerator(datas, self.config_ini)
        folder_path = img.generate_image()
        return datas, folder_path

    def generate_reports(self):
        # 生成报告
        tpl = DocxTemplate(self.tpl_file)
        result1, result2 = self.DP()

        insert_image1 = InlineImage(tpl, result2, width=Mm(140))

        datas=result1
        context = {'data': self.now,
                   'leak_num': len(datas),
                   'file_path': os.path.realpath(__file__),
                   "code_type": "C",
                   'datas': datas,
                    "chart":insert_image1}  # 待替换对象

        # 渲染模板
        tpl.render(context)
        tpl.save(self.report_file)

        return self.report_file, result2



