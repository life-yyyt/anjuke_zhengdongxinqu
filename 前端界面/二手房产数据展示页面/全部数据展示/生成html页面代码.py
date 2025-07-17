import pandas as pd

# 加载数据
df = pd.read_csv('anjuke_data_cleaned.csv')

# 将 DataFrame 转换为 HTML 表格，并设置一些基本格式
html_table = df.to_html(
    index=False,  # 不显示索引列
    justify='left',  # 内容左对齐
    border=1,  # 添加表格边框
    col_space=20  # 列间距
)

# 定义 HTML 文件路径
html_path = '爬取数据展示页面.html'

# 生成完整的 HTML 内容，添加内联样式以美化表格和页面
html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>房产数据展示</title>
    <style>
        /* 设置页面背景色，字体和布局 */
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }}

        /* 标题样式 */
        h1 {{
            color: #007bff;
            text-align: center;
            padding-bottom: 20px;
        }}

        /* 表格样式 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            background-color: white;
        }}

        /* 表头样式 */
        th {{
            background-color: #007bff;
            color: white;
            padding: 10px;
            text-align: left;
        }}

        /* 表格单元格样式 */
        td {{
            padding: 8px;
            text-align: left;
            border-top: 1px solid #ddd;
        }}

        /* 奇偶行背景颜色交替 */
        tr:nth-child(odd) {{
            background-color: #f9f9f9;
        }}

        tr:nth-child(even) {{
            background-color: #ffffff;
        }}

        /* 表格边框 */
        table, th, td {{
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <h1>房产数据表格</h1>
    {html_table}
</body>
</html>
"""

# 将 HTML 内容写入文件
with open(html_path, 'w', encoding='utf-8') as file:
    file.write(html_content)