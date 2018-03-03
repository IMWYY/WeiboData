# -*- coding:utf-8 -*-

import csv

from data_helper import get_enterprise_data
from data_helper import get_gov_level_data
from data_helper import get_eastern_data
from data_helper import get_province
from data_helper import get_forest_data
from data_helper import get_electricity_data
from data_helper import get_weibo_data
from data_helper import get_gov_reply_data
from data_helper import get_comment_data
from data_helper import time_in_range
from data_helper import get_date_diff
from data_helper import get_pgdp
from data_helper import get_PGDP_data
from data_helper import get_user_data
from data_helper import print_list

"""
'0发布时间', '1微博用户', '2用户类型', '3投诉发帖内容', '4评论内容/链接', 
'5涉及国控企业名称', '6国控企业法人编号','7污染所在地', '8污染所在地行政区编号', '9污染所在地区(东部、中西部)',
'10企业状态', '11登记注册类型', '12企业规模', '13行业类别代码', '14行业类别名称', '15工业总产值当年价格万元', '16年正常生产时间小时', 
'17森林覆盖率', '18工业发电量', '19人均国内生产总值', '20转发量', '21评论量', '22点赞量',

'23政府部门是否回应', '24政府部门', '25政府部门级别','26行政区划','27是否是环保部门', '28政府部门回应时间', '29政府部门回应时差(s)',
'30政府部门是否反@', '31政府部门反@帖子内容', '32政府部门是否转发', '33政府部门转发帖子内容', '34政府部门是否在投诉帖评论',
'35政府评论内容', '36政府部门是否发布回应通告', '37通告内容',

'38中央政府是否@政府帐号', '39中央政府表述内容', '40上级政府是否@政府帐号', '41上级政府表述内容',
'42下级政府是否@政府帐号', '43下级政府表述内容',
"""


def format_list_input(output_path):
    """
    将数据处理为需求列表的数据
    :param output_path: 输出的文件
    """
    titles = ['发布时间', '微博用户', '用户类型', '投诉发帖内容', '评论内容/链接',
              '涉及国控企业名称', '国控企业法人编号', '污染所在地', '污染所在地行政区编号', '污染所在地区(东部、中西部)',
              '企业状态', '登记注册类型', '企业规模', '行业类别名称', '行业类别代码', '工业总产值当年价格万元', '年正常生产时间小时',
              '森林覆盖率', '工业发电量', '人均国内生产总值', '转发量', '评论量', '点赞量',
              '政府部门是否回应', '政府部门', '政府部门级别', '行政区划', '是否是环保部门', '政府部门回应时间', '政府部门回应时差(s)',
              '政府部门是否反@', '政府部门反@帖子内容', '政府部门是否转发', '政府部门转发帖子内容', '政府部门是否在投诉帖评论',
              '政府评论内容', '政府部门是否发布回应通告', '通告内容',
              '中央政府是否@政府帐号', '中央政府表述内容', '上级政府是否@政府帐号', '上级政府表述内容',
              '下级政府是否@政府帐号', '下级政府表述内容']

    out = open(output_path, 'w')
    writer = csv.writer(out)
    writer.writerow(titles)

    # 微博@的数据
    weibo_at_data = get_weibo_data('data/weiboAt.csv')
    # 政府回应的数据
    gov_reply_data = get_gov_reply_data('data/govReply_filtered.csv')
    # 获取评论的数据
    comment_data = get_comment_data('data/weiboComment_format.csv')
    # 政府账号级别 和 行政区划的数据
    gov_account_level = get_gov_level_data('data/gov_accounts.csv')
    # 0企业名称,1地点,2行政编号,3年份,4污染类型,5法人编号,
    # 6企业状态,7登记注册类型,8企业规模,9行业类别代码,10行业类别名称,11工业总产值当年价格万元,12年正常生产时间小时
    enterprise_data = get_enterprise_data('data/enterprise.csv')
    # 森林覆盖率
    forest_data = get_forest_data()
    # 工业发电量
    electricity_data = get_electricity_data()
    # 人均国内生产总值
    pgdp_data = get_PGDP_data('data/PGDP.csv')
    # 东部省份
    eastern = get_eastern_data()

    count = 0

    for weibo in weibo_at_data:
        print_list(weibo)
        # 如果是政府@政府的微博不统计
        if not weibo or gov_account_level.get(weibo[1]):
            print '--------no gov_account_level'
            continue

        # 处理@的政府账号 每个政府@一条数据
        at_list = list(set(weibo[11:len(weibo) - 1]))
        for at in at_list:
            if len(at) < 2 or not at.startswith('@') or not gov_account_level.get(at[1:]):
                continue
            government = at[1:]  # @的政府账号
            account_level_detail = gov_account_level.get(government, ['unknown', 'unknown'])
            gov_level = account_level_detail[0]
            gov_location = account_level_detail[1]

            line = ['' for i in xrange(44)]
            line[0] = weibo[5]  # 发布时间
            line[1] = weibo[0]  # 微博用户
            # todo 用户类型
            line[3] = weibo[1]  # 投诉发帖内容
            line[4] = weibo[6]  # 评论内容/链接
            line[5] = weibo[7]  # 涉及国控企业名称

            enterprise_detail = enterprise_data.get(weibo[7], [])
            if enterprise_detail:
                province = get_province(enterprise_detail[1])

                line[6] = enterprise_detail[5]  # 国控企业法人编号
                line[7] = enterprise_detail[1]  # 污染所在地
                line[8] = enterprise_detail[2]  # 污染所在地行政区编号
                line[9] = 1 if province in eastern else 0  # 东西部
                line[10] = enterprise_detail[6]  # 企业状态
                line[11] = enterprise_detail[7]  # 登记注册类型
                line[12] = enterprise_detail[8]  # 企业规模
                line[13] = enterprise_detail[9]  # 行业类别代码
                line[14] = enterprise_detail[10]  # 行业类别名称
                line[15] = enterprise_detail[11]  # 工业总产值当年价格万元
                line[16] = enterprise_detail[12]  # 年正常生产时间小时

                line[17] = forest_data.get(province, 0)  # 森林覆盖率
                line[18] = electricity_data.get(province, 0)  # 工业发电量
                line[19] = get_pgdp(pgdp_data, weibo[5][:4], province, gov_location)  # 人均国内生产总值
            else:
                print '--------no enterprise_detail'
                continue
            line[20] = weibo[4]  # 转发量
            line[21] = weibo[3]  # 评论量
            line[22] = weibo[2]  # 点赞量
            line[24] = government  # 政府部门
            line[25] = gov_level  # 政府部门的级别
            line[26] = gov_location  # 政府部门行政区划
            line[27] = 1  # 是否是环保部门 目前默认是环保部门

            line[23] = line[30] = line[32] = line[34] = line[36] = 0  # 初始化政府回应为否

            # 评论数据 12评论账号 13评论时间 14评论内容
            comment_detail = comment_data.get(weibo[0].strip() + weibo[5])
            if comment_detail and len(comment_detail) > 14:
                index = 12
                while index < len(comment_detail):
                    if comment_detail[index] == government:
                        line[23] = 1  # 政府部门是否回应
                        line[28] = comment_detail[13]  # 政府部门回应时间
                        line[29] = abs(get_date_diff(comment_detail[13], weibo[5]))  # 政府部门回应时差
                        line[34] = 1  # 是否评论
                        line[35] = comment_detail[14]  # 评论内容
                        break
                    index += 3

            # 反@ 发布通告（没有@的回应）转发
            for reply in gov_reply_data:
                # 在回复的时间范围内 且 发布回复的账号是该@的政府 且 涉及企业相同
                if time_in_range(reply[5], weibo[5]) and reply[0] == government and weibo[7] == reply[7]:
                    line[23] = 1  # 政府部门是否回应

                    # 回应时间取最临近的
                    if line[29] and line[28]:
                        if get_date_diff(reply[5], weibo[5]) < line[29]:
                            line[28] = reply[5]  # 政府部门回应时间
                            line[29] = get_date_diff(reply[5], weibo[5])  # 政府部门回应时差
                    else:
                        line[28] = reply[5]  # 政府部门回应时间
                        line[29] = get_date_diff(reply[5], weibo[5])  # 政府部门回应时差

                    # 反@
                    if ('@' + weibo[0]) in reply[11:]:
                        line[30] = 1  # 17政府部门是否反@
                        line[31] = reply[1]  # 18政府部门反@帖子内容
                        count += 1
                        print '反@' + str(count)
                    # 发布通告（没有@的回应）
                    else:
                        line[36] = 1
                        line[37] = reply[1]  # 24通告内容
                        count += 1
                        print '发布通告' + str(count)

                    # 转发 (回复是转发 且 (转发自原博主或转发自原博主转发自的博主))
                    if reply[8] == 1 and (reply[9] == weibo[0] or (weibo[8] == 1 and reply[9] == weibo[9])):
                        line[32] = 1
                        line[33] = reply[10]
                        count += 1
                        print '转发' + str(count)

                    # 初始化中央政府回应为否
                    line[38] = line[40] = line[42] = 0

                    # 中央政府回应
                    if reply[0] == '环保部发布':
                        line[38] = 1
                        line[39] = reply[1]

                    # 上级回应下级
                    if gov_account_level.get(reply[0], ['无', ''])[0] == '省':
                        for account in reply[11:]:
                            if len(account) > 1 and (gov_account_level.get(account[1:], ['无', ''])[0] == '市'
                                                     or gov_account_level.get(account[1:], ['无', ''])[0] == '县'):
                                line[40] = 1
                                line[41] = reply[1]
                    elif gov_account_level.get(reply[0], ['无', ''])[0] == '市':
                        for account in reply[11:]:
                            if len(account) > 1 and gov_account_level.get(account[1:], ['无', ''])[0] == '县':
                                line[40] = 1
                                line[41] = reply[1]
                    elif reply[0] == '环保部发布':
                        for account in reply[11:]:
                            if len(account) > 1 and gov_account_level.get(account[1:], ['无', ''])[0] != '无':
                                line[40] = 1
                                line[41] = reply[1]

                    # 下级回应上级
                    if gov_account_level.get(reply[0], ['无', ''])[0] == '县':
                        for account in reply[11:]:
                            if len(account) > 1 and (gov_account_level.get(account[1:], ['无', ''])[0] == '市'
                                                     or gov_account_level.get(account[1:], ['无', ''])[0] == '省'
                                                     or account == '@环保部发布'):
                                line[42] = 1
                                line[43] = reply[1]
                    elif gov_account_level.get(reply[0], ['无', ''])[0] == '市':
                        for account in reply[11:]:
                            if len(account) > 1 and (gov_account_level.get(account[1:], ['无', ''])[0] == '省'
                                                     or account == '@环保部发布'):
                                line[42] = 1
                                line[43] = reply[1]
                    elif gov_account_level.get(reply[0], ['无', ''])[0] == '省':
                        for account in reply[11:]:
                            if account == '@环保部发布':
                                line[42] = 1
                                line[43] = reply[1]
            writer.writerow(line)
            print_list(line)
    print 'all' + str(count)


def add_extra_info(output_path):
    """
    在model_list_input添加用户信息('微博用户', '是否认证') 和 '是否上市'
    :param output_path:
    :return:
    """
    user_data = get_user_data('data/all_user.csv')
    reader = csv.reader(open('data/model_input_list.csv', 'r'))

    titles = ['发布时间', '微博用户', '是否认证', '认证类型(机构/个人)', '投诉发帖内容', '评论内容/链接',
              '涉及国控企业名称', '国控企业法人编号', '污染所在地', '污染所在地行政区编号', '污染所在地区(东部、中西部)',
              '企业状态', '是否上市', '登记注册类型', '企业规模', '行业类别名称', '行业类别代码', '工业总产值当年价格万元', '年正常生产时间小时',
              '森林覆盖率', '工业发电量', '人均国内生产总值', '转发量', '评论量', '点赞量',
              '政府部门是否回应', '政府部门', '政府部门级别', '行政区划', '是否是环保部门', '政府部门回应时间', '政府部门回应时差(s)',
              '政府部门是否反@', '政府部门反@帖子内容', '政府部门是否转发', '政府部门转发帖子内容', '政府部门是否在投诉帖评论',
              '政府评论内容', '政府部门是否发布回应通告', '通告内容',
              '中央政府是否@政府帐号', '中央政府表述内容', '上级政府是否@政府帐号', '上级政府表述内容',
              '下级政府是否@政府帐号', '下级政府表述内容']
    writer = csv.writer(open(output_path, 'w'))

    market_reader = csv.reader(open('data/market_enterprise_new.csv', 'r'))
    market_enterprise = []
    for row in market_reader:
        market_enterprise.append(row[2])

    count = 0
    no_data_list = []
    first_row = True
    for row in reader:
        if first_row:
            first_row = False
            writer.writerow(titles)
            continue

        market = 1 if row[5] in market_enterprise else 0
        info = user_data.get(row[1])

        if not info:
            print '----' + row[1]
            count += 1
            row[2] = '否'
            no_data_list.append(row[1])
            row.insert(3, '')
            row.insert(12, market)
        else:
            row[2] = info[0]
            row.insert(3, info[1])
            row.insert(12, market)
        writer.writerow(row)
    print count
    print len(set(no_data_list))


# format_list_input('data/model_input_list.csv')
add_extra_info('data/model_input_list_new.csv')
