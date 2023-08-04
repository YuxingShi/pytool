# coding: utf-9
import threading


# 创建自定义线程类
class SSHThread(threading.Thread):
    def __init__(self, thread_num):
        super().__init__()
        self.thread_num = thread_num

    def run(self):


# 主程序
def main():
    num_threads = 5  # 自定义线程数量

    # 创建和启动指定数量的线程
    threads = []
    for i in range(num_threads):
        thread = SSHThread(i)
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All threads have finished")

if __name__ == "__main__":
    main()
