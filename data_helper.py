# -*- coding:utf-8 -*-
import csv
import json

import datetime

import re


def print_list(data):
    print json.dumps(data, ensure_ascii=False)


def get_pgdp(data, year, enterprise_province, gov_location):
    """
    根据地点获取人均gdp数据 如果有精确到市的数据 选择市的 如果没有选择省的
    :param data: 字典数据 key-地点 value-[2014, 2015, 216]
    :param year: 年份
    :param enterprise_province: 企业的省份
    :param gov_location: 政府的地点
    """
    pos_1 = gov_location.find('省')
    pos_2 = gov_location.find('市')
    result = city = ''
    if pos_1 > 1 and pos_2 > 4:
        city = gov_location[pos_1 + 1:pos_2]
    elif pos_1 < 0 and pos_2 > 1:
        city = gov_location[:pos_2]

    # 如果有精确到市的数据 选择市的 如果没有选择省的
    if city:
        result = data.get(city)
    if not result:
        result = data.get(enterprise_province)

    if not result:
        return ''
    return result[0 if year == '2014' else (1 if year == '2015' else (2 if year == '2016' else 0))]


def get_province(location):
    """
    根据地点找出省份
    """
    match_obj = re.match(
        r'.*?((北京)|(天津)|(河北)|(辽宁)|(上海)|(江苏)|(浙江)|(福建)|(山东)|(广东)|'
        r'(海南)|(山西)|(吉林)|(黑龙江)|(安徽)|(江西)|(河南)|(湖北)|(湖南)|(四川)|(重庆)|'
        r'(贵州)|(云南)|(西藏)|(陕西)|(甘肃)|(青海)|(宁夏)|(新疆)|(广西)|(内蒙古)).*?',
        location, re.M | re.I)
    if match_obj:
        return match_obj.group(1)
    else:
        return ''


def get_eastern_data():
    """
    获取东部省份信息
    """
    return ['北京', '天津', '河北', '辽宁', '上海', '江苏', '浙江', '福建', '山东', '广东', '海南']
    # western = ['山西', '吉林', '黑龙江', '安徽', '江西', '河南', '湖北', '湖南',
    #            '四川', '重庆', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '广西', '内蒙古']


def get_forest_data():
    """
    获取森林覆盖率的数据
    """
    return {'北京': 35.84, '天津': 9.87, '河北': 23.41, '山西': 18.03, '内蒙古': 21.03, '辽宁': 38.24,
            '吉林': 40.38, '黑龙江': 43.16, '上海': 10.74, '江苏': 15.8, '浙江': 59.07, '安徽': 27.53,
            '福建': 65.95, '江西': 60.01, '山东': 16.73, '河南': 21.5, '湖北': 38.4,
            '湖南': 47.77, '广东': 51.26, '广西': 56.51, '海南': 55.38, '重庆': 38.43, '四川': 35.22,
            '贵州': 37.09, '云南': 50.03, '西藏': 11.98, '陕西': 41.42, '甘肃': 11.28,
            '青海': 5.63, '宁夏': 11.89, '新疆': 4.24}


def get_electricity_data():
    """
    获取工业发电量的数据
    """
    return {'北京': 434.39, '天津': 617.55, '河北': 2630.59, '山西': 2535.08, '内蒙古': 3949.81, '辽宁': 1778.76,
            '吉林': 760.26, '黑龙江': 900.41, '上海': 807.29, '江苏': 4709.37, '浙江': 3197.66, '安徽': 2252.69,
            '福建': 2007.43, '江西': 1085.35, '山东': 5329.27, '河南': 2652.66, '湖北': 2479.02,
            '湖南': 1385.09, '广东': 4263.66, '广西': 1346.51, '海南': 287.73, '重庆': 701.19, '四川': 3273.85,
            '贵州': 1903.99, '云南': 2692.54, '西藏': 54.48, '陕西': 1757.41, '甘肃': 1214.33,
            '青海': 552.96, '宁夏': 1144.38, '新疆': 2719.13}


def time_in_range(x, y):
    """
    :param x: 回复的时间
    :param y: 原微博发布的时间
    :return:  回复时间是否再原微博发布的时间后的两月以内
    """
    d1 = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(y, '%Y-%m-%d %H:%M:%S')
    return 0 <= (d1 - d2).days <= 60


def get_date_diff(date1, date2):
    """
    计算两个日期的时间差 精确到秒
    """
    d1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    return (d1 - d2).total_seconds()


def get_gov_level_data(gov_account_path):
    """
    获取政府账号级别 和 行政区划的数据
    """
    gov_account_data = {}
    gov_account_reader = csv.reader(open(gov_account_path, 'r'))
    for row in gov_account_reader:
        if '省' in row[2]:
            gov_account_data[row[0]] = ['省', row[4]]
        elif '市' in row[2]:
            gov_account_data[row[0]] = ['市', row[4]]
        else:
            gov_account_data[row[0]] = ['县', row[4]]
    return gov_account_data


def get_PGDP_data(PGDP_path):
    """
    获取人均gdp数据 key-地点 value-[2014, 2015, 216]
    """
    data = {}
    reader = csv.reader(open(PGDP_path, 'r'))
    for row in reader:
        data[row[1]] = [row[4], row[3], row[2]]
    return data


def get_enterprise_data(enterprise_path):
    """
    获取企业数据 包括
    0企业名称,1地点,2行政编号,3年份,4污染类型,5法人编号,
    6企业状态,7登记注册类型,8企业规模,9行业类别代码,10行业类别名称,11工业总产值当年价格万元,12年正常生产时间小时
    """
    enterprise_data = {}
    enterprise_reader = csv.reader(open(enterprise_path, 'r'))
    for row in enterprise_reader:
        enterprise_data[row[0]] = row
    return enterprise_data


def get_weibo_data(weibo_at_path):
    """
    获取微博@的数据
    """
    weibo_at_data = []
    weibo_at_reader = csv.reader(open(weibo_at_path, 'r'))
    for row in weibo_at_reader:
        weibo_at_data.append(row)
    weibo_at_data.sort(key=lambda x: x[5])  # 按时间升序排序
    return weibo_at_data


def get_gov_reply_data(gov_reply_path):
    """
    获取政府回应的数据
    """
    gov_reply_data = []
    gov_reply_reader = csv.reader(open(gov_reply_path, 'r'))
    for row in gov_reply_reader:
        gov_reply_data.append(row)
    gov_reply_data.sort(key=lambda x: x[5])  # 按时间升序排序
    return gov_reply_data


def get_comment_data(comment_path):
    """
    获取评论的数据 用微博账号和发帖时间做key 形成键值对
    """
    comment_data = {}
    csv_reader = csv.reader(open(comment_path, 'r'))
    for row in csv_reader:
        comment_data[row[0].strip() + row[5]] = row
    return comment_data
