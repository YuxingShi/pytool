import tkinter as tk
from tkinter import ttk
import os


class DirectoryBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Directory Browser")

        self.treeview = ttk.Treeview(self.root)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.load_directory("E:\PyCharmProj\pytool")

    def load_directory(self, path, parent=""):
        if not parent:
            # 添加根节点
            root_node = self.treeview.insert("", tk.END, text=path, open=True)
            parent = root_node

        # 遍历目录下的子目录和文件
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)

            if is_dir:
                # 添加子目录节点
                dir_node = self.treeview.insert(parent, tk.END, text=item, open=False)
                self.load_directory(item_path, dir_node)
            else:
                # 添加文件节点
                self.treeview.insert(parent, tk.END, text=item)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    browser = DirectoryBrowser()
    browser.run()
