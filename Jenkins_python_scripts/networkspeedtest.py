#!/usr/bin/env python
# -*- coding=utf-8 -*-
import speedtest as spt
from pprint import pprint

spd = spt.Speedtest()
pprint(spd.get_servers())
print('测试开始，请稍等...')
download = int(spd.download())
upload = int(spd.upload())
print(f'当前下载速度为：{str(download)} bit/s')
print(f'当前上传速度为：{str(upload)} bit/s')
print('测试已完成！')
