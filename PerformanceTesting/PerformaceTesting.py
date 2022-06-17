# coding:utf-8
import time

import matplotlib
import matplotlib.pyplot as plt

font = {'family': 'MicroSoft YaHei',
        'weight': 'normal',
        'size': 10}
matplotlib.rc("font", **font)
base_time = 1655454892
time_list = time.mktime(1655454892)
# 图片生成代码
fig = plt.figure(figsize=(20, 10))  # figsize=(10, 5)  建立画布
ax1 = fig.add_subplot(2, 2, 1)
fig.subplots_adjust(wspace=0)  # 设置子图间的间距，为子图宽度的40%
