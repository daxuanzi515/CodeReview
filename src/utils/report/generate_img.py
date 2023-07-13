import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

from pylab import mpl
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
class PieChartGenerator:
    def __init__(self, riskdatas, invaliddatas, config_ini):
        self.riskdatas = riskdatas
        self.invaliddatas = invaliddatas
        self.config_ini = config_ini

    def data_processing(self):
        rank_counts = {}
        for data in self.riskdatas:
            rank = data["rank"]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        for data in self.invaliddatas:
            rank = data["rank"]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        self.labels = list(rank_counts.keys())
        self.sizes = list(rank_counts.values())

    def generate_image(self):
        self.data_processing()
        cmap = get_cmap('tab20c')
        colors = [cmap(i) for i in range(len(self.labels))]

        explode = [0.1] * len(self.labels)
        plt.pie(self.sizes, explode=explode, labels=self.labels, autopct="%3.1f%%", startangle=60, colors=colors)
        plt.title('Risk Level Distribution')
        # 保存饼状图为图像文件
        import time
        nowtime = time.localtime()
        nowtime_ = time.strftime("%Y_%m_%d_%H_%M_%S", nowtime)
        img_path = self.config_ini['main_project']['project_name'] + self.config_ini['report']['img_path'].format(nowtime_, 'image')  # 指定保存路径和文件名
        plt.savefig(img_path)  # 保存饼状图为图像文件
        return img_path

# datas = [
#             {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
#             {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "Low"},
#             {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
#             {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "Medium"},
#             {"func": "Risk Function 1", "path": "Path 1", "lines": 10, "remedy": "Solution 1", "rank": "High"},
#         ]
# demo=PieChartGenerator(datas=datas)
# demo.generate_image()




