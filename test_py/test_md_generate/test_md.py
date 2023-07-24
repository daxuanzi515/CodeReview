data = [
    {'检测时间': '2023-07-15', '缺陷数': '10'},
    {'检测时间': '2023-07-16', '缺陷数': '8'},
    {'检测时间': '2023-07-17', '缺陷数': '12'}
]

# 构建表格数据
table_data = '| 检测时间 | 缺陷数 |\n'
table_data += '| :------: | :----: |\n'
for item in data:
    table_data += f'| {item["检测时间"]} | {item["缺陷数"]} |\n'

# 读取Markdown模板文件
with open('mytemplate.md', 'r', encoding='utf-8') as f:
    template = f.read()

# 替换占位符
report = template.replace('{{table0}}', table_data)

# 保存生成的报告
with open('myreport.md', 'w', encoding='utf-8') as f:
    f.write(report)
