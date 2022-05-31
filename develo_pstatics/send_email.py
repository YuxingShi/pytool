# coding:utf-8
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.application import MIMEApplication
from typing import List


class EmailSender(object):
    server = None
    from_addr = ''
    passwd = ''

    def __init__(self, smtp_server='smtp.hztech.cn', smtp_port=465, from_addr='shiyuxing@hztech.cn',
                 passwd='YNOsn3csv'):
        self.from_addr = from_addr
        self.passwd = passwd
        self.server = smtplib.SMTP(smtp_server, smtp_port)
        self.server.set_debuglevel(1)
        self.server.starttls()  # 主要是当前连接支持server并不支持[AUTH_CRAM_MD5, AUTH_PLAIN, AUTH_LOGIN]中的任何一种认证方式，导致程序运行出现问题。
        # 邮件设置
        self.msg = MIMEMultipart()

    def set_email_subject(self, subject_text: str):
        """
        邮件主题
        :param subject_text: 主题文本
        :return:
        """
        self.msg['Subject'] = subject_text

    def set_email_body(self, body_text: str):
        """
        设置邮件正文
        :param body_text: 正文内容
        :return:
        """
        # 添加邮件正文:
        self.msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    def set_email_attach(self, file_path: str):
        """
        添加邮件附件
        :param file_path: 附件路径
        :return:
        """
        # 添加附件
        # 注意这里的文件路径是斜杠
        path, file_name = os.path.split(file_path)
        part = MIMEApplication(open(file_path, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=file_name)
        self.msg.attach(part)

    def send_email(self, receiver: List, acc: List):
        """
        邮件发送
        :param receiver:  收件人列表
        :param acc: 抄送人列表
        :return:
        """
        self.msg['to'] = ','.join(receiver)
        self.msg['Cc'] = ','.join(acc)
        self.msg['from'] = self.from_addr
        # 登陆邮箱
        self.server.login(self.from_addr, self.passwd)
        # 发送邮件
        self.server.sendmail(self.from_addr, receiver + acc, self.msg.as_string())
        # 断开服务器链接
        self.server.quit()
