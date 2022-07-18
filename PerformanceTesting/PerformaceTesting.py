# coding:utf-8
import time
import random
import csv


def get_date_range(start_date='2022-05-24', days=30):
    date_list = []
    temp_time = time.mktime(time.strptime(start_date, '%Y-%m-%d'))
    day_seconds = 24 * 60 * 60
    date_list.append(start_date)
    for _ in range(days - 1):
        temp_time += day_seconds
        date_list.append(time.strftime('%Y-%m-%d', time.localtime(temp_time)))
    return date_list


def generate_performance_data(save_file_name):
    date_list = get_date_range()
    head_row = ['日期', '用户态CPU利用率', '系统态CPU利用率', '日期', '内存利用率', '日期', '磁盘使用率']
    use_list = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 0.5, 0.1, 0.1, 0.1, 0.1]
    disk_use_list = [0, 0, 0, 0, 0, 0, 0, 0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0, 0, 0, 0, 0]
    with open(save_file_name, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(head_row)
        disk_use = 5
        for date in date_list:
            user_cpu = 9
            sys_cpu = 2
            mem_use = 20
            for i in range(24):
                new_user_cpu = user_cpu + use_list[i] * random.random() * 20
                new_sys_cpu = sys_cpu + use_list[i] * random.random() * 3
                new_mem_use = mem_use + use_list[i] * random.random() * 18
                disk_use += disk_use_list[i] * random.random()
                date_h = '{} {}'.format(date, str(i))
                data_row = [date_h, new_user_cpu, new_sys_cpu, date_h, new_mem_use, date_h, disk_use]
                writer.writerow(data_row)


if __name__ == '__main__':
    for i in range(16, 17):
        generate_performance_data('{}.csv'.format(i))
