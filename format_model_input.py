# -*- coding:utf-8 -*-
import csv
import re

"""
0发布时间	        1微博用户	            2用户类型	                3投诉发帖内容	            4评论内容/链接
5涉及国控企业名称	6国控企业法人编号     7污染所在地（尽量精确）	    8污染所在地行政区编号	    9转发量
10评论量	        11点赞量

12政府部门是否回应         13政府部门级别	      14是否是环保部门            15政府部门回应时间	 16政府部门回应时差
17政府部门是否反@	        18政府部门反@帖子内容	  19政府部门是否转发	        20政府部门转发帖子内容（分享心得）
21政府部门是否在投诉帖评论	22政府评论内容	      23政府部门是否发布回应通告	24通告内容

25中央政府是否@政府帐号	26中央政府表述内容	    27上级政府是否@政府帐号	28上级政府表述内容   29下级政府是否@政府帐号	30下级政府表述内容

31对政府部门帐号投诉@的数量(指半年针对某一国控企业问题对某一政府部门@的数量)
32政府部门回应比例(指回应“对政府部门帐号投诉@的数量”的比例)

注：政府部门级别  三类，即省级（直辖市、自治区）；市级（地级市、地区、自治州、盟）；县级（市辖区、县、自治县、县级市、旗、自治旗、林区、特区）

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


def output_data(gov_account_level, enterprise_data, eastern, forest_data, electricity_data, source_data, dict_data,
                writer):
    """
    将数据输出
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
    # 每次外层循环输出一次
    for key, value in dict_data.items():
        # 初始化数据
        s = diff = position = y = x = forward = praise = comment = 0
        forest = industry = year = ''
        count = reply_count = 0.0

        keys = key.split("_")
        enterprise_detail = enterprise_data.get(keys[0], [])
        account_level_info = gov_account_level.get(keys[1], ['unknown', 'unknown']),
        account_level = account_level_info[0][0]
        account_area = account_level_info[0][1]
        if not enterprise_detail or not account_level:
            continue

        first_line = True
        for index in value:
            row = source_data[index]
            if len(row) < 34:
                continue

            reply_count += (1 if row[12] == '1' else 0)  # 政府回应的微博数
            count += 1  # 微博投诉数
            # 首次处理不需要遍历累加的变量 所在地 森林覆盖率 工业发电量 年份
            if first_line:
                first_line = False
                match_obj = re.match(
                    r'.*?((北京)|(天津)|(河北)|(辽宁)|(上海)|(江苏)|(浙江)|(福建)|(山东)|(广东)|'
                    r'(海南)|(山西)|(吉林)|(黑龙江)|(安徽)|(江西)|(河南)|(湖北)|(湖南)|(四川)|(重庆)|'
                    r'(贵州)|(云南)|(西藏)|(陕西)|(甘肃)|(青海)|(宁夏)|(新疆)|(广西)|(内蒙古)).*?',
                    row[7], re.M | re.I)
                if match_obj:
                    province = match_obj.group(1)
                else:
                    continue
                s = (1 if province in eastern else 0)  # 污染所在地区 东部地区为1、中西部地区为0
                forest = forest_data.get(province, 0)  # 森林覆盖率
                industry = electricity_data.get(province, 0)  # 工业发电量
                year = row[0][:4]
            forward += int(row[9])  # 总转发量
            praise += int(row[11])  # 总点赞量
            comment += int(row[10])  # 总评论量
            x += len(row[33].split('_'))  # 微博投诉@的数量
            y += (1 if row[17] == '1' else 0)  # 地方政府回应的数量
            y += (1 if row[19] == '1' else 0)
            y += (1 if row[21] == '1' else 0)
            y += (1 if row[23] == '1' else 0)
            position += (1 if row[25] == '1' else 0)  # 中央/上级政府关注
            position += (1 if row[27] == '1' else 0)
            diff += (float(row[16]) if row[12] == '1' else 0)  # 回应时差
        if count > 0:
            writer.writerow([y, x, round(y / float(x) if x > 0 else 0, 4),  # '地方政府回应数(Y)', '微博投诉@数(X)', '@回应比例',
                             reply_count, count, round(reply_count / count, 4),
                             s, '', '',
                             keys[1], account_level, account_area, keys[0],
                             enterprise_detail[0], enterprise_detail[1], enterprise_detail[2],
                             forward, comment, praise,
                             round(forward / count, 4), round(comment / count, 4), round(praise / count, 4),
                             round(position / count, 4), forest, industry,
                             year, (round(diff / reply_count, 4) if reply_count > 0 else 0)])


def get_gov_level_data(gov_account_path):
    """
    获取政府账号级别的数据
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


def get_enterprise_data(enterprise_path):
    """
    获取企业数据 包括法人编号 所在地 所在地行政编号
    """
    enterprise_data = {}
    enterprise_reader = csv.reader(open(enterprise_path, 'r'))
    for row in enterprise_reader:
        enterprise_data[row[0]] = [row[5], row[1], row[2]]
    return enterprise_data


def format_model_input(input_path, output_path):
    """
    根据数据需求格式模型输入
    :return:
    """

    titles = ['地方政府回应数(Y)', '微博投诉@数(X)', '@回应比例',
              '地方政府回应的投诉发帖数', '投诉发帖数', '投诉回应比例',
              '污染所在地区(S)', '人均国内生产总值(PGDP)', '企业特征(Enterprise)',
              '政府部门', '政府部门级别', '行政区划', '企业名称', '法人编号', '污染所在地', '行政编号',
              '总转发量(Forward_all)', '总评论量(Comment_all)', '总点赞量(Praise_all)',
              '平均转发量(Forward)', '平均评论量(Comment)', '平均点赞量(Praise)',
              '中央/上级政府关注(Position)', '森林覆盖率(Forest)', '工业发电量(Industry)',
              '年份(year)', '平均回应时间/秒(Diff)']

    eastern = ['北京', '天津', '河北', '辽宁', '上海', '江苏', '浙江', '福建', '山东', '广东', '海南']
    western = ['山西', '吉林', '黑龙江', '安徽', '江西', '河南', '湖北', '湖南',
               '四川', '重庆', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '广西', '内蒙古']

    forest_data = {'北京': 35.84, '天津': 9.87, '河北': 23.41, '山西': 18.03, '内蒙古': 21.03, '辽宁': 38.24,
                   '吉林': 40.38, '黑龙江': 43.16, '上海': 10.74, '江苏': 15.8, '浙江': 59.07, '安徽': 27.53,
                   '福建': 65.95, '江西': 60.01, '山东': 16.73, '河南': 21.5, '湖北': 38.4,
                   '湖南': 47.77, '广东': 51.26, '广西': 56.51, '海南': 55.38, '重庆': 38.43, '四川': 35.22,
                   '贵州': 37.09, '云南': 50.03, '西藏': 11.98, '陕西': 41.42, '甘肃': 11.28,
                   '青海': 5.63, '宁夏': 11.89, '新疆': 4.24}

    electricity_data = {'北京': 434.39, '天津': 617.55, '河北': 2630.59, '山西': 2535.08, '内蒙古': 3949.81, '辽宁': 1778.76,
                        '吉林': 760.26, '黑龙江': 900.41, '上海': 807.29, '江苏': 4709.37, '浙江': 3197.66, '安徽': 2252.69,
                        '福建': 2007.43, '江西': 1085.35, '山东': 5329.27, '河南': 2652.66, '湖北': 2479.02,
                        '湖南': 1385.09, '广东': 4263.66, '广西': 1346.51, '海南': 287.73, '重庆': 701.19, '四川': 3273.85,
                        '贵州': 1903.99, '云南': 2692.54, '西藏': 54.48, '陕西': 1757.41, '甘肃': 1214.33,
                        '青海': 552.96, '宁夏': 1144.38, '新疆': 2719.13}

    gov_account_level = get_gov_level_data('data/gov_accounts.csv')
    enterprise_data = get_enterprise_data('data/enterprise.csv')

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
        # 检查是否在这个时间区间 每个时间区间会输出一次
        if get_date_span(row[0]) != current_date_span:
            # print 'current_date_span' + str(current_date_span)
            # print 'next_date_span' + str(get_date_span(row[0]))
            current_date_span = get_date_span(row[0])
            output_data(gov_account_level, enterprise_data, eastern, forest_data, electricity_data, required_data,
                        span_data, writer)
            span_data = {}
        # 检查所有@的政府账号和时间涉及的企业 作为key
        # print 'row[31]' + row[31]
        for at in row[31].split('_'):
            if not at:  # 剔除没有@那315个政府账号的帖子
                print '--------' + row[31]
                continue
            key = row[5] + '_' + at
            # print 'key' + key
            if span_data.get(key, []):
                span_data.get(key).append(i)
            else:
                span_data[key] = [i]


# print get_date_span('2016-09-09 23:55:33')
format_model_input('data/required_data.csv', 'data/model_input.csv')
