# coding:utf-8
# Created on 2019年2月26日
# @author: Shiyx
import time
import calendar
import requests
import openpyxl
from lxml import etree

_DEBUG_ = False
person_id_dict = {'2678': '施宇星',
                  '2562': '梁霞',
                  '3140': '王小梅',
                  '3283': '朱晓凤',
                  '3116': '蒋丽婷',
                  '3139': '陈小英',
                  '2955': '游芬',
                  '1342': '马晓元',
                  '3282': '张捷',
                  '3279': '许嘉俊'}


class ITM(object):
    response = None
    base_url = ''
    header = {
        'Accept': 'application/x-ms-application, image/jpeg, application/xaml+xml, '
                  'image/gif, image/pjpeg, application/x-ms-xbap, application/x-shockwave-flash, */*',
        'Accept-Language': 'zh-CN',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727'
                      '; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)',
        'Accept-Encoding': 'gzip, deflate'
    }
    _user_info_dict = {}
    _task_info_dict = {}
    _event_task_dict = {}
    month_date_begin = ''
    month_date_end = ''

    def __init__(self, base_url='http://10.168.6.51:7001/', https=False):
        self.session = requests.Session()
        self.session.verify = https
        self.session.headers.update(self.header)
        self.base_url = base_url
        self._init_data()

    def _init_data(self):
        # 本月第一天日期及第二天日期
        year, month = time.localtime()[0: 2]
        month_first_day, month_last_day = 1, calendar.monthrange(year, month)[1]
        self.month_date_begin = '{}-{}-{}'.format(year, month, month_first_day)
        self.month_date_end = '{}-{}-{}'.format(year, month, month_last_day)
        
    def update_headers(self, headers):
        self.session.headers.update(headers)
                
    def get(self, url, headers=None):
        if headers:
            self.updateHeaders(headers)
        try:
            self.response = self.session.get(url)
            if self.response.status_code == 200:
                return 0
            else:
                return -1
        except requests.exceptions.ConnectionError:
            return -1
        
    def post(self, url, headers=None, data=None):
        if headers:
            self.updateHeaders(headers)
        try:
            self.response = self.session.post(url, data)
            if self.response.status_code == 200:
                if _DEBUG_:
                    print('response:', self.response.text)
                return 0
            else:
                return -1
        except requests.exceptions.ConnectionError:
            return -1

    def login(self, user_code='test', password='888888'):
        url = '%sj_security_check' % self.base_url
        data = '<UserInfo forceLogin="-1" autoLogin="0" loginType="0" isAllowUnSys="false">' \
               '<j_username>%s</j_username><j_password>%s</j_password></UserInfo>' % (user_code, password)
        if self.post(url, data=data) == 0:
            root = etree.fromstring(self.response.text.encode('GBK'))
            try:
                if root.xpath('.//check_result')[0].text == 'true':
                    url = '%sservlet/util?OperType=6' % self.base_url  # 获取用户初始信息
                    if self.post(url) == 0:
                        self._user_info_dict.clear()
                        root = etree.fromstring(self.response.text.encode('GBK'))
                        self._user_info_dict['staff_name'] = root.xpath('.//staff_name')[0].text
                        self._user_info_dict['user_name'] = root.xpath('.//user_name')[0].text
                        self._user_info_dict['pswd'] = root.xpath('.//pswd')[0].text
                    return 0
                else:
                    return -1
            except Exception:
                return -1
        else:
            return -1

    # 获取任务单总数
    def get_task_count(self):
        url = '%sservlet/result.do?method=getPageResultXml&getType=FORCE' % self.base_url
        data = '<root><result id="957100001" key="957100001" ref="sqlResult" hasField="0" filedsearch="">' \
               '<param name="FLOW_MOD" type="STRING" isMultiple="0BF"></param>' \
               '<param name="SERIAL" type="STRING" isMultiple="0BF"></param>' \
               '<param name="TITLE" type="STRING" isMultiple="0BF"></param>' \
               '<param name="BEGIN_DATE" type="STRING" isMultiple="0BF"></param>' \
               '<param name="END_DATE" type="STRING" isMultiple="0BF"></param>' \
               '<param name="ORG_ID" type="STRING" isMultiple="0BF"></param>' \
               '<param name="start" type="STRING" isMultiple="0BF">0</param>' \
               '<param name="limit" type="STRING" isMultiple="0BF">30</param>' \
               '</result></root>'
        if self.post(url, data=data) == 0:
            root = etree.fromstring(self.response.content)
            tasks_count = root.xpath('.//totalCount')[0].text
            tasks_row = root.xpath('.//rowSet')
            self._task_info_dict.clear()  # 流程id列表初始化
            for row in tasks_row:
                flow_id = row.xpath('./C_3')[0].text  # 流程id
                patch_publish_time = row.xpath('./C_13')[0].text  # 补丁预排发布时间
                arrived_time = row.xpath('./C_11')[0].text  # 环节创建时间
                self._task_info_dict[flow_id] = [patch_publish_time, arrived_time]  # 流程id为C_3
            if _DEBUG_:
                print('self._task_info_dict', self._task_info_dict)
            return tasks_count
        else:
            return -1

    # 根据流程id获取任务单信息
    def get_task_information(self):
        tasks_info_dict = {}
        for flow_id in self._task_info_dict.keys():
            task_info = self._task_info_dict.get(flow_id)
            if _DEBUG_:
                print('task_info', task_info)
            url = '%sservlet/CooCommonServlet?tag=4&CLASS_NAME=CooTfEventSql' \
                  '&CLASS_FIELD=GET_ALL_MAIN_FLOW_INFO_IN_PATCH&FLOW_ID=' % self.base_url + flow_id
            if self.post(url) == 0:
                root = etree.fromstring(self.response.content)
                title = root.xpath('.//TITLE')[0].text
            url = '%sservlet/result.do?method=getPageResultXml&getType=FORCE' % self.base_url
            data = '<root><result id="570001" key="570001" ref="sqlResult" hasField="0" filedsearch="">' \
                   '<param name="FLOW_ID" type="STRING" isMultiple="0BF">%s</param>' \
                   '<param name="start" type="STRING" isMultiple="0BF">0</param>' \
                   '<param name="limit" type="STRING" isMultiple="0BF">10</param></result></root>' % flow_id
            if self.post(url, data=data) == 0:
                root = etree.fromstring(self.response.content)
                row_set = root.xpath('.//rowSet')[0]  # 只取第一行的值
                svn_url = row_set.xpath('./C_2')[0].text
                task_info.append(svn_url)
            tasks_info_dict[title] = task_info
        return tasks_info_dict

    # 获取指定时间段的事件单信息
    def get_event_itm(self, date_start, date_end):
        url = '%sservlet/result.do?method=getPageResultXml&getType=FORCE' % self.base_url
        data = '<root><result id="4500029" key="4500029" ref="sqlResult" hasField="0" filedsearch="">' \
               '<param name="now_tch" type="STRING" isMultiple="0BT"></param>' \
               '<param name="event_priority" type="STRING" isMultiple="0BF"></param>' \
               '<param name="EVENT_TYPE" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_created_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_created_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_expect_finish_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="PRODUCT_PCK" type="STRING" isMultiple="0BT"></param>' \
               '<param name="submit_org_id" type="STRING" isMultiple="0BF"></param>' \
               '<param name="event_title" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_submit_date" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="m_submit_date" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="s_patch_plan_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_patch_plan_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_expect_finish_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="event_serial" type="STRING" isMultiple="0BF"></param>' \
               '<param name="start" type="STRING" isMultiple="0BF">0</param>' \
               '<param name="limit" type="STRING" isMultiple="0BF">20</param>' \
               '</result></root>' % (date_start, date_end)
        if self.post(url, data=data) == 0:
            root = etree.fromstring(self.response.content)
            tasks_count = root.xpath('.//totalCount')[0].text
            row_sets = root.xpath('.//rowSet')
            sheet = []
            title = ['事件单号', '事件主题', '事件原因', '发起工程点', '事件归类', '创建日期', '当前环节',
                     '当前环节负责人', '当前环节开始时间', '事件处理协作单', '期望完成日期', '事件类型', '原因一级分类',
                     '原因二级分类', '是否BUG', '归属产品包', '要求完成时间', '是否超时', '研发响应时长',
                     '研发耗费时长（小时）', '是否出补丁', '提出人']
            sheet.append(title)
            for row in row_sets:
                event_no = row.xpath('./C_3')[0].text  # 事件单号
                event_theme = row.xpath('./C_4')[0].text  # 事件主题
                # event_cause = ''  # 事件原因
                start_point = row.xpath('./C_5')[0].text  # 发起工程点
                event_classification = ''  # 事件归类
                create_time = row.xpath('./C_7')[0].text  # 创建日期
                current_step = row.xpath('./C_8')[0].text  # 当前环节
                current_step_person = row.xpath('./C_9')[0].text  # 当前环节负责人
                current_step_time = row.xpath('./C_12')[0].text  # 当前环节开始时间
                event_process_task = row.xpath('./C_13')[0].text  # 事件处理协作单
                hope_complete_time = row.xpath('./C_14')[0].text  # 期望完成日期
                event_type = row.xpath('./C_15')[0].text  # 事件类型
                cause_level1 = row.xpath('./C_17')[0].text  # 原因一级分类
                event_cause = cause_level2 = row.xpath('./C_18')[0].text  # 原因二级分类 # 如果存在【原因二级分类】则【事件原因直接取该值】
                bug_justify = row.xpath('./C_19')[0].text  # 是否BUG
                package_belong = row.xpath('./C_20')[0].text  # 归属产品包
                demand_end_time = row.xpath('./C_21')[0].text  # 要求完成时间
                time_out_justify = row.xpath('./C_22')[0].text  # 是否超时
                develop_react_time = row.xpath('./C_26')[0].text  # 研发响应时长
                develop_time = row.xpath('./C_28')[0].text  # 研发耗费时长（小时）
                patch_published = row.xpath('./C_25')[0].text  # 是否出补丁
                advice = row.xpath('./C_27')[0].text  # 提出人
                sheet.append([event_no, event_theme, event_cause, start_point, event_classification, create_time,
                              current_step, current_step_person, current_step_time, event_process_task,
                              hope_complete_time, event_type, cause_level1, cause_level2, bug_justify, package_belong,
                              demand_end_time, time_out_justify, develop_react_time, develop_time, patch_published,
                              advice])
            if _DEBUG_:
                print('sheet', sheet)
            self.write_to_xlsx(sheet)

    # 需求单明细查询
    def requirement_detail_query(self):
        result_dict = {}
        url = '%sservlet/result.do?method=getPageResultXml&getType=FORCE' % self.base_url
        data = '<root><result id="4500028" key="4500028" ref="sqlResult" hasField="0" filedsearch="">' \
               '<param name="PRODUCT_PKG" type="STRING" isMultiple="0BT"></param>' \
               '<param name="m_pre_dev_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="request_title" type="STRING" isMultiple="0BF"></param>' \
               '<param name="PROJECT_SITE_ID" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_submit_time" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_submit_time" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_hope_solve_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_hope_solve_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="urgency_degree" type="STRING" isMultiple="0BF"></param>' \
               '<param name="important_degree" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_patch_plan_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_patch_plan_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="now_tch" type="STRING" isMultiple="0BT"></param>' \
               '<param name="m_created_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="s_created_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="request_type" type="STRING" isMultiple="0BF"></param>' \
               '<param name="bbusiness_dimensionality_id" type="STRING" isMultiple="0BF"></param>' \
               '<param name="request_serial" type="STRING" isMultiple="0BF"></param>' \
               '<param name="m_pre_patch_publish_date" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="s_pre_patch_publish_date" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="s_pre_dev_end_date" type="STRING" isMultiple="0BF"></param>' \
               '<param name="IMPLEMENT_PLAN" type="STRING" isMultiple="0BF"></param>' \
               '<param name="start" type="STRING" isMultiple="0BF">0</param>' \
               '<param name="limit" type="STRING" isMultiple="0BF">200</param>' \
               '</result></root>' % (self.month_date_end, self.month_date_begin)
        if self.post(url, data=data) == 0:
            root = etree.fromstring(self.response.content)
            tasks_count = root.xpath('.//totalCount')[0].text
            row_sets = root.xpath('.//rowSet')
            for row in row_sets:
                requirement_no = row.xpath('./C_7')[0].text  # 需求单号
                requirement_title = row.xpath('./C_8')[0].text  # 需求标题
                patch_no = row.xpath('./C_12')[0].text  # 发布补丁号
                plan_pub_time = row.xpath('./C_17')[0].text  # 规划补丁发布时间
                actual_pub_time = row.xpath('./C_22')[0].text  # 实际补丁发布时间
                result_dict[requirement_no] = [requirement_title, patch_no, plan_pub_time, actual_pub_time]
            print(tasks_count, result_dict)

    # 需求单进程查询
    def requirement_schedule_query(self, pub_person_id):
        result_dict = {}
        url = '%sservlet/result.do?method=getPageResultXml&getType=FORCE' % self.base_url
        data = '<root><result id="900001001" key="900001001" ref="sqlResult" hasField="0" filedsearch="">' \
               '<param name="pretreatment_staff" type="STRING" isMultiple="0BF"></param>' \
               '<param name="DEV_E_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="DEV_ORG" type="STRING" isMultiple="0BT"></param>' \
               '<param name="V_TITLE" type="STRING" isMultiple="0BF"></param>' \
               '<param name="V_NO" type="STRING" isMultiple="0BF"></param>' \
               '<param name="B_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="E_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="V_STATUS" type="STRING" isMultiple="0BT"></param>' \
               '<param name="V_BATCH" type="STRING" isMultiple="0BF"></param>' \
               '<param name="PUB_B_TIME" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="PUB_E_TIME" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="R_PUB_B_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="R_PUB_E_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="PUB_P" type="STRING" isMultiple="0BF">%s</param>' \
               '<param name="R_DEV_B_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="R_DEV_E_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="REQ_P" type="STRING" isMultiple="0BF"></param>' \
               '<param name="DEV_B_TIME" type="STRING" isMultiple="0BF"></param>' \
               '<param name="DEV_P" type="STRING" isMultiple="0BF"></param>' \
               '<param name="start" type="STRING" isMultiple="0BF">0</param>' \
               '<param name="limit" type="STRING" isMultiple="0BF">50</param>' \
               '<param name="sort" type="STRING" isMultiple="0BF">DEV_ORG_NAME</param>' \
               '<param name="dir" type="STRING" isMultiple="0BF">ASC</param>' \
               '</result></root>' % (self.month_date_begin, self.month_date_end, pub_person_id)
        if self.post(url, data=data) == 0:
            root = etree.fromstring(self.response.content)
            tasks_count = root.xpath('.//totalCount')[0].text
            row_sets = root.xpath('.//rowSet')
            sheet = []
            for row in row_sets:
                requirement_no = row.xpath('./C_2')[0].text  # 需求单号
                requirement_title = row.xpath('./C_3')[0].text  # 需求标题
                patch_no = row.xpath('./C_12')[0].text  # 发布补丁号
                plan_pub_time = row.xpath('./C_17')[0].text  # 规划补丁发布时间
                actual_pub_time = row.xpath('./C_22')[0].text  # 实际补丁发布时间
                tester = row.xpath('./C_23')[0].text  # 测试人员
                sheet.append([requirement_no, requirement_title, patch_no, plan_pub_time, actual_pub_time, tester])
            return sheet

    # 需求单进程统计
    def requirement_schedule_statistic(self):
        sheet = []
        title = ['需求单号', '需求标题', '发布补丁号', '规划补丁发布时间', '实际补丁发布时间', '测试人员']
        sheet.append(title)
        for staff_id in person_id_dict.keys():
            sheet.extend(self.requirement_schedule_query(staff_id))
        self.write_to_xlsx(sheet, 'staff_performamce.xlsx', sheet_name='{}-{}'.format(self.month_date_begin, self.month_date_end))

    @staticmethod
    def write_to_xlsx(src_list, work_book_name='test.xlsx', sheet_name='sheet'):
        wb = openpyxl.workbook.Workbook()
        ws = wb.create_sheet(sheet_name)
        for row in src_list:
            ws.append(row)
        wb.save(work_book_name)


if __name__ == '__main__':
    rs = ITM()
    rs.login('shiyuxing', '888888')
    #rs.get_task_count()
    rs.get_event_itm('2020-07-31', '2020-08-06')
    # rs.requirement_schedule_statistic()
    # rs.requirement_detail_query()



