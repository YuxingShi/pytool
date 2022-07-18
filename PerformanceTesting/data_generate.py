# coding:utf-8
import random


def withG(num):
    return '{}G'.format(num)


def disk_storage():
    host = '10.168.6.150'
    temp = round(random.random() * 300, 1)
    document = round(random.random() * 200, 1)
    temp1 = round(random.random() * 100, 1)
    jimureport = round(random.random() * 100, 1)
    group1 = round(random.random() * 100, 1)
    sapply = round(random.random() * 400, 1)
    undefined = round(random.random() * 100, 1)
    total = round(temp + document + temp1 + jimureport + group1 + sapply + undefined, 1)
    template = """
    [root@{} gdcrtmis]# du -cah -d 1
    {:<6}     ./temp
    {:<6}     ./document
    {:<6}     ./temp1
    {:<6}     ./jimureport
    {:<6}     ./group1
    {:<6}     ./sapply
    {:<6}     ./undefined
    {:<6}     .
    {:<6}     总用量""".format(host, withG(temp), withG(document), withG(temp1), withG(jimureport), withG(group1),
                             withG(sapply), withG(undefined), withG(total), withG(total))
    print(template)


if __name__ == "__main__":
    disk_storage()
