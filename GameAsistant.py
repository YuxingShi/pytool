# coding:utf-8
import time
import win32gui
import win32con
import win32api
from PIL import ImageGrab


class GameAssist(object):

    def __init__(self, wd_name):
        """初始化"""

        # 取得窗口句柄
        self.hwnd = win32gui.FindWindow(0, wd_name)
        if not self.hwnd:
            print("窗口找不到，请确认窗口句柄名称：【%s】" % wd_name)
            exit()
        # 窗口显示最前面
        # win32gui.SetForegroundWindow(self.hwnd)
        # 获取窗口位置,左上角，右下角
        # left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        self.scree_left_and_right_point = win32gui.GetWindowRect(self.hwnd)
        print(self.scree_left_and_right_point)

    def set_mouse_at_window_center(self):
        left, top, right, bottom = self.scree_left_and_right_point
        window_center = (left + right)//2, (top + bottom)//2
        win32api.SetCursorPos(window_center)

    def click(self, times=100000):
        for i in range(times):
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def screenshot(self):
        """屏幕截图"""

        # 1、用grab函数截图，参数为左上角和右下角左标
        # image = ImageGrab.grab((417, 257, 885, 569))
        print(win32gui.IsWindowEnabled(self.hwnd))
        image = ImageGrab.grab(self.scree_left_and_right_point)
        with open('./test.jpg', 'wb') as fp:
            image.save(fp)
        # # 2、分切小图
        # # exit()
        # image_list = {}
        # offset = self.im_width  # 39
        #
        # # 8行12列
        # for x in range(8):
        #     image_list[x] = {}
        #     for y in range(12):
        #         # print("show",x, y)
        #         # exit()
        #         top = x * offset
        #         left = y * offset
        #         right = (y + 1) * offset
        #         bottom = (x + 1) * offset
        #         # 用crop函数切割成小图标，参数为图标的左上角和右下角左边
        #         im = image.crop((left, top, right, bottom))
        #         # 将切割好的图标存入对应的位置
        #         image_list[x][y] = im
        # return image_list


if __name__ == "__main__":
    # wd name 为连连看窗口的名称，必须写完整
    window_name = u'咸鱼之王'
    demo = GameAssist(window_name)
    demo.set_mouse_at_window_center()
    demo.click()
    # time.sleep(1)
    # demo.screenshot()




