# -*- coding:utf-8 -*-
import csv
from data_helper import get_gov_level_data
from data_helper import get_PGDP_data
from data_helper import get_enterprise_data
from data_helper import get_province
from data_helper import get_forest_data
from data_helper import get_electricity_data
from data_helper import get_eastern_data
from data_helper import get_pgdp

"""
0* Y           地方政府回应      (是否回应/回应的比例)
1* X           微博投诉          （有无@/@的数量)
2* S           污染所在地区      (东部地区为1、中西部地区为0)
3  PGDP        人均国内生产总值
4  Enterprise  企业特征
5* Forward_all     总转发量
6* Comment_all     总评论量
7* Praise_all      总点赞量
8* Forward     平均转发量
9* Comment     平均评论量
10* Praise      平均点赞量
11* Position    中央/上级政府关注  (@地方政府微博帐号表征为1，若无@则表征为0)
12* Forest      森林覆盖率
13*Industry    工业发电量
14*year        年份
15*Diff        平均回应时间

'地方政府回应数(Y)', '微博投诉@数(X)', '@回应比例',
'地方政府回应的投诉发帖数', '投诉发帖数', '投诉回应比例',
'污染所在地区(S)', '人均国内生产总值(PGDP)',
'企业状态', '登记注册类型', '企业规模', '行业类别代码', '行业类别名称', '工业总产值当年价格万元', '年正常生产时间小时',
'政府部门', '政府部门级别', '行政区划', '企业名称', '法人编号', '污染所在地', '行政编号',
'总转发量(Forward_all)', '总评论量(Comment_all)', '总点赞量(Praise_all)',
'平均转发量(Forward)', '平均评论量(Comment)', '平均点赞量(Praise)',
'中央/上级政府关注(Position)', '森林覆盖率(Forest)', '工业发电量(Industry)',
'年份(year)', '平均回应时间/秒(Diff)'
"""


def get_date_span(date):
    """
    获取时间所在区间 半年一段 0 1 2 3 4 5分别表示14-16三年
    :return: 0 1 2 3 4 5分别表示14-16三年
    """
    if '2014-01-01 00:00:00' <= date < '2014-07-01 00:00:00':
        return 0
    elif '2014-07-01 00:00:00' <= date < '2015-01-01 00:00:00':
        return 1
    elif '2015-01-01 00:00:00' <= date < '2015-07-01 00:00:00':
        return 2
    elif '2015-07-01 00:00:00' <= date < '2016-01-01 00:00:00':
        return 3
    elif '2016-01-01 00:00:00' <= date < '2016-07-01 00:00:00':
        return 4
    elif '2016-07-01 00:00:00' <= date < '2017-03-01 00:00:00':
        return 5
    else:
        return -1


def output_data(PGDP_data, gov_account_level, enterprise_data, eastern, forest_data, electricity_data, source_data,
                dict_data, writer):
    """
    将数据输出
    :param PGDP_data: 人均gdp的数据
    :param gov_account_level: 政府部门级别的数据
    :param enterprise_data: 企业数据 包括法人编号 所在地 所在地行政编号
    :param eastern: 污染所在地区 东部数据
    :param forest_data: 森林覆盖率数据
    :param electricity_data: 工业发电量数据
    :param source_data: 全部的数据 列表形式
    :param dict_data: 字典 key是 企业和政府部门组合 value是row的列表
    :param writer: 输出流
    """
    if len(dict_data) == 0:
        return
    print len(dict_data)
    # 每次外层循环输出一次 key是 企业_政府账号 value是微博帖子数组下标的列表
    for key, value in dict_data.items():
        # 初始化数据
        pgdp = s = diff = position = y = x = forward = praise = comment = 0
        forest = industry = year = ''
        weibo_count = reply_count = 0.0

        keys = key.split("__")
        # 政府的数据
        government = keys[1]
        account_level_detail = gov_account_level.get(government, ['unknown', 'unknown'])
        gov_level = account_level_detail[0]
        gov_location = account_level_detail[1]
        if gov_level == 'unknown':
            print government + "--------" + key

        # 企业的数据
        enterprise = keys[0]
        enterprise_detail = enterprise_data.get(enterprise, [])  # 法人编号 所在地 所在地行政编号
        if not enterprise_detail:
            continue
        # 0企业名称,1地点,2行政编号,3年份,4污染类型,5法人编号, 6企业状态,7登记注册类型,8企业规模,
        # 9行业类别代码,10行业类别名称,11工业总产值当年价格万元,12年正常生产时间小时
        enterprise_legal = enterprise_detail[5]
        enterprise_location = enterprise_detail[1]
        enterprise_area_code = enterprise_detail[2]
        enterprise_status = enterprise_detail[6]
        enterprise_type = enterprise_detail[7]
        enterprise_scale = enterprise_detail[8]
        enterprise_industry = enterprise_detail[9]
        enterprise_industry_code = enterprise_detail[10]
        enterprise_output = enterprise_detail[11]
        enterprise_hours = enterprise_detail[12]

        first_line = True
        for index in value:
            row = source_data[index]
            if len(row) < 34:
                continue

            reply_count += (1 if row[12] == '1' else 0)  # 政府回应的微博数
            weibo_count += 1  # 微博投诉数

            # 首次处理不需要遍历累加的变量 所在地 森林覆盖率 工业发电量 年份
            if first_line:
                first_line = False
                province = get_province(enterprise_location)
                if not province:
                    continue
                s = (1 if province in eastern else 0)  # 污染所在地区 东部地区为1、中西部地区为0
                forest = forest_data.get(province, 0)  # 森林覆盖率
                industry = electricity_data.get(province, 0)  # 工业发电量
                year = row[0][:4]  # 年份
                pgdp = get_pgdp(PGDP_data, year, province, gov_location)

            forward += int(row[9])  # 总转发量
            praise += int(row[11])  # 总点赞量
            comment += int(row[10])  # 总评论量
            # x += len(row[31].split('_'))  # 微博投诉@的数量
            x += (len(row[31].split('__')) if row[31] else 0)  # 微博投诉@的数量
            y += (1 if row[17] == '1' else 0)  # 地方政府回应的数量
            y += (1 if row[19] == '1' else 0)
            y += (1 if row[21] == '1' else 0)
            y += (1 if row[23] == '1' else 0)
            position += (1 if row[25] == '1' else 0)  # 中央/上级政府关注
            position += (1 if row[27] == '1' else 0)
            diff += (float(row[16]) if row[12] == '1' else 0)  # 回应时差
        if weibo_count > 0:
            writer.writerow([y, x, round(y / float(x) if x > 0 else 0, 4),  # '地方政府回应数(Y)', '微博投诉@数(X)', '@回应比例',
                             reply_count, weibo_count, round(reply_count / weibo_count, 4),
                             s, pgdp, enterprise_status, enterprise_type, enterprise_scale, enterprise_industry,
                             enterprise_industry_code, enterprise_output, enterprise_hours,
                             government, gov_level, gov_location, enterprise,
                             enterprise_legal, enterprise_location, enterprise_area_code,
                             forward, comment, praise,
                             round(forward / weibo_count, 4), round(comment / weibo_count, 4),
                             round(praise / weibo_count, 4),
                             round(position / weibo_count, 4), forest, industry,
                             year, (round(diff / reply_count, 4) if reply_count > 0 else 0)])


def format_model_input(input_path, output_path):
    """
    根据数据需求格式模型输入
    :return:
    """

    titles = ['地方政府回应数(Y)', '微博投诉@数(X)', '@回应比例',
              '地方政府回应的投诉发帖数', '投诉发帖数', '投诉回应比例',
              '污染所在地区(S)', '人均国内生产总值(PGDP)',
              '企业状态', '登记注册类型', '企业规模', '行业类别代码', '行业类别名称', '工业总产值当年价格万元', '年正常生产时间小时',
              '政府部门', '政府部门级别', '行政区划', '企业名称', '法人编号', '污染所在地', '行政编号',
              '总转发量(Forward_all)', '总评论量(Comment_all)', '总点赞量(Praise_all)',
              '平均转发量(Forward)', '平均评论量(Comment)', '平均点赞量(Praise)',
              '中央/上级政府关注(Position)', '森林覆盖率(Forest)', '工业发电量(Industry)',
              '年份(year)', '平均回应时间/秒(Diff)']

    eastern = get_eastern_data()
    forest_data = get_forest_data()
    electricity_data = get_electricity_data()
    gov_account_level = get_gov_level_data('data/gov_accounts.csv')
    enterprise_data = get_enterprise_data('data/enterprise.csv')
    PGDP_data = get_PGDP_data('data/PGDP.csv')

    out = open(output_path, 'w')
    writer = csv.writer(out)
    writer.writerow(titles)

    # 将csv文件中的数据装入list
    required_data = []
    first_row = True
    reader = csv.reader(open(input_path, 'r'))
    for r in reader:
        # 跳过标题栏
        if first_row:
            first_row = False
            continue
        required_data.append(r)
    required_data.sort(key=lambda x: x[0])  # 按时间升序排序

    current_date_span = 0
    span_data = {}  # 满足条件的数据 key是 企业和政府部门组合 value是row的列表
    for i in xrange(len(required_data)):
        row = required_data[i]

        # 删除政府部门@政府部门的帖子
        if gov_account_level.get(row[1]):
            print '-----'
            continue

        # 检查是否在这个时间区间 每个时间区间会输出一次
        if get_date_span(row[0]) != current_date_span:
            current_date_span = get_date_span(row[0])
            output_data(PGDP_data, gov_account_level, enterprise_data, eastern, forest_data, electricity_data,
                        required_data, span_data, writer)
            span_data = {}
        # 检查所有@的政府账号和时间涉及的企业 作为key
        if not row[31]:  # 剔除没有@那315个政府账号的帖子
            continue
        for at in row[31].split('__'):
            if not at:
                continue
            key = row[5].replace('_', '') + '__' + at
            if span_data.get(key, []):
                span_data.get(key).append(i)
            else:
                span_data[key] = [i]


# print get_date_span('2016-09-09 23:55:33')
format_model_input('data/required_data.csv', 'data/model_input_statistical.csv')
