#coding:utf-8
import wmi

c = wmi.WMI()


def yingpan():
    # # 硬盘序列号
    cc = ""
    for physical_disk in c.Win32_DiskDrive():
        # print(physical_disk.SerialNumber)
        cc += physical_disk.SerialNumber
    return cc


def cpuid():
    # CPU序列号
    cc = ""
    for cpu in c.Win32_Processor():
        # print(cpu.ProcessorId.strip())
        cc += cpu.ProcessorId.strip()
    return cc


def zhubanid():
    # 主板序列号
    cc = ""
    for board_id in c.Win32_BaseBoard():
        # print(board_id.SerialNumber)
        cc += board_id.SerialNumber
    return cc


def macid():
    # mac地址
    cc = ""
    for mac in c.Win32_NetworkAdapter():
        # print(mac.MACAddress)
        cc += str(mac.MACAddress)
    return cc


def biosid():
    # bios序列号
    cc = ""
    for bios_id in c.Win32_BIOS():
        # print(bios_id.SerialNumber.strip())
        cc += bios_id.SerialNumber.strip()
    return cc


if __name__ == '__main__':
    yid = yingpan()
    cid = cpuid()
    zid = zhubanid()
    mid = macid()
    bid = biosid()
    zong = yid+cid+zid+mid+bid
    print(zong)
