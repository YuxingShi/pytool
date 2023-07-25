import os

def generate_file_list(directory):
    """生成目录下的文件列表"""
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def generate_html(file_list):
    """根据文件列表生成 HTML"""
    html = "<html><body><ul>"
    for file in file_list:
        filename = os.path.basename(file)
        html += f"<li><a href='{file}' download='{filename}'>{filename}</a></li>"
    html += "</ul></body></html>"
    return html


DIRECTORY = "F:\\mp3"  # 指定要生成文件列表的目录


file_list = generate_file_list(DIRECTORY)
html_content = generate_html(file_list)

with open("index.html", "w", encoding="GBK") as file:
    file.write(html_content)
