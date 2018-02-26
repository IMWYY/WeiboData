# -*- coding:utf-8 -*-

import csv
from data_helper import get_gov_level_data
from data_helper import get_weibo_data
from data_helper import get_gov_reply_data
from data_helper import get_comment_data
from data_helper import print_list
from data_helper import time_in_range
from data_helper import get_date_diff
from data_helper import get_enterprise_data

"""
0发布时间	        1微博用户	            2用户类型	                3投诉发帖内容	            4评论内容/链接
5涉及国控企业名称	6国控企业法人编号     7污染所在地（尽量精确）	    8污染所在地行政区编号	    9转发量
10评论量	        11点赞量

12政府部门是否回应         13政府部门级别	      14是否是环保部门            15政府部门回应时间	 16政府部门回应时差
17政府部门是否反@	        18政府部门反@帖子内容	  19政府部门是否转发	        20政府部门转发帖子内容（分享心得）
21政府部门是否在投诉帖评论	22政府评论内容	      23政府部门是否发布回应通告	24通告内容

25中央政府是否@政府帐号	26中央政府表述内容	    27上级政府是否@政府帐号	28上级政府表述内容   29下级政府是否@政府帐号	30下级政府表述内容

31@的政府账号
32政府回应次数 
33对政府部门帐号投诉@的数量(指半年针对某一国控企业问题对某一政府部门@的数量)
34政府部门回应比例(指回应“对政府部门帐号投诉@的数量”的比例)

注：政府部门级别  三类，即省级（直辖市、自治区）；市级（地级市、地区、自治州、盟）；县级（市辖区、县、自治县、县级市、旗、自治旗、林区、特区）
"""


def format_data(output_path):
    """
    将数据处理为需求列表的数据
    :param output_path: 输出的文件
    """
    # 微博@的数据
    weibo_at_data = get_weibo_data('data/weiboAt.csv')
    # 政府回应的数据
    gov_reply_data = get_gov_reply_data('data/govReply_filtered.csv')
    # 获取评论的数据
    comment_data = get_comment_data('data/weiboComment_format.csv')
    # 政府账号级别 和 行政区划的数据
    gov_account_level_data = get_gov_level_data('data/gov_accounts.csv')
    # 企业数据 包括法人编号 所在地 所在地行政编号
    enterprise_data = get_enterprise_data('data/enterprise.csv')

    titles = ['发布时间', '微博用户', '用户类型', '投诉发帖内容', '评论内容/链接', '涉及国控企业名称', '国控企业法人编号',
              '污染所在地', '污染所在地行政区编号', '转发量', '评论量', '点赞量',
              '政府部门是否回应', '政府部门级别', '是否是环保部门', '政府部门回应时间', '政府部门回应时差(s)',
              '政府部门是否反', '政府部门反@帖子内容', '政府部门是否转发', '政府部门转发帖子内容', '政府部门是否在投诉帖评论',
              '政府评论内容', '政府部门是否发布回应通告', '通告内容',
              '中央政府是否@政府帐号', '中央政府表述内容', '上级政府是否@政府帐号', '上级政府表述内容',
              '下级政府是否@政府帐号', '下级政府表述内容',
              '@的政府账号', '政府回应次数(包括转发反@评论通告)', '对政府部门帐号投诉@的数量', '政府部门回应比例']
    out = open(output_path, 'w')
    writer = csv.writer(out)
    writer.writerow(titles)

    count = 0

    for weibo in weibo_at_data:
        print_list(weibo)
        if not weibo:
            continue

        line = ['' for i in xrange(35)]
        line[0] = weibo[5]  # 发布时间
        line[1] = weibo[0]  # 微博用户
        line[3] = weibo[1]  # 投诉发帖内容
        line[4] = weibo[6]  # 评论内容/链接
        line[5] = weibo[7]  # 涉及国控企业名称

        enterprise_detail = enterprise_data.get(weibo[7], [])
        if enterprise_detail:
            line[6] = enterprise_detail[5]  # 国控企业法人编号
            line[7] = enterprise_detail[1]  # 污染所在地
            line[8] = enterprise_detail[2]  # 污染所在地行政区编号
        else:
            line[6] = 'unknown'  # 国控企业法人编号
            line[7] = 'unknown'  # 污染所在地
            line[8] = 'unknown'  # 污染所在地行政区编号

        line[9] = weibo[4]  # 转发量
        line[10] = weibo[3]  # 评论量
        line[11] = weibo[2]  # 点赞量

        line[12] = line[17] = line[19] = line[21] = line[23] = 0  # 初始化政府回应为否

        # 处理@的政府账号 用_分割
        at_accounts = []
        first_line = True
        at_list = list(set(weibo[11:len(weibo) - 1]))
        for at in at_list:
            if len(at) > 1 and gov_account_level_data.get(at[1:]):
                if first_line:
                    first_line = False
                    at_accounts.append(at[1:])
                else:
                    at_accounts.append('__' + at[1:])
        line[31] = ''.join(at_accounts)

        # 评论数据 12评论账号 13评论时间 14评论内容
        comment_detail = comment_data.get(weibo[0].strip() + weibo[5], [])
        if comment_detail and len(comment_detail) > 14:
            line[21] = 1  # 是否评论
            line[22] = comment_detail[14]  # 评论内容
            line[12] = 1  # 12政府部门是否回应
            line[13] = gov_account_level_data.get(comment_detail[12], ['无', ''])[0]  # 政府部门的级别
            line[14] = 1  # 14是否是环保部门 目前默认是环保部门
            line[15] = comment_detail[13]  # 15政府部门回应时间
            line[16] = abs(get_date_diff(comment_detail[13], weibo[5]))  # 16政府部门回应时差

        # 反@ 发布通告（没有@的回应）转发
        for reply in gov_reply_data:
            # 在回复的时间范围内 且 原微博@到该回复账号 且 涉及企业相同
            if time_in_range(reply[5], weibo[5]) and ('@' + reply[0]) in weibo[11:len(weibo) - 1] \
                    and weibo[7] == reply[7]:

                line[12] = 1  # 12政府部门是否回应
                line[13] = gov_account_level_data.get(reply[0], ['无', ''])[0]  # 政府部门的级别
                line[14] = 1  # 14是否是环保部门 目前默认是环保部门

                # 回应时间取最临近的
                if line[15] and line[16]:
                    if get_date_diff(reply[5], weibo[5]) < line[16]:
                        line[15] = reply[5]  # 15政府部门回应时间
                        line[16] = get_date_diff(reply[5], weibo[5])  # 16政府部门回应时差
                else:
                    line[15] = reply[5]  # 15政府部门回应时间
                    line[16] = get_date_diff(reply[5], weibo[5])  # 16政府部门回应时差

                # 反@
                if ('@' + weibo[0]) in reply[11:]:
                    line[17] = 1  # 17政府部门是否反@
                    line[18] = reply[1]  # 18政府部门反@帖子内容
                    count += 1
                    print '反@' + str(count)
                # 发布通告（没有@的回应）
                else:
                    line[23] = 1
                    line[24] = reply[1]  # 24通告内容
                    count += 1
                    print '发布通告' + str(count)

                # 转发 (回复是转发 且 (转发自原博主或转发自原博主转发自的博主))
                if reply[8] == 1 and (reply[9] == weibo[0] or (weibo[8] == 1 and reply[9] == weibo[9])):
                    line[19] = 1
                    line[20] = reply[10]
                    count += 1
                    print '转发' + str(count)

                # 初始化中央政府回应为否
                line[25] = line[27] = line[29] = 0

                # 中央政府回应
                if reply[0] == '环保部发布':
                    line[25] = 1
                    line[26] = reply[1]

                # 上级回应下级
                if gov_account_level_data.get(reply[0], ['无', ''])[0] == '省':
                    for account in reply[11:]:
                        if len(account) > 1 and (gov_account_level_data.get(account[1:], ['无', ''])[0] == '市'
                                                 or gov_account_level_data.get(account[1:], ['无', ''])[0] == '县'):
                            line[27] = 1
                            line[28] = reply[1]
                elif gov_account_level_data.get(reply[0], ['无', ''])[0] == '市':
                    for account in reply[11:]:
                        if len(account) > 1 and gov_account_level_data.get(account[1:], ['无', ''])[0] == '县':
                            line[27] = 1
                            line[28] = reply[1]
                elif reply[0] == '环保部发布':
                    for account in reply[11:]:
                        if len(account) > 1 and gov_account_level_data.get(account[1:], ['无', ''])[0] != '无':
                            line[27] = 1
                            line[28] = reply[1]

                # 下级回应上级
                if gov_account_level_data.get(reply[0], ['无', ''])[0] == '县':
                    for account in reply[11:]:
                        if len(account) > 1 and (gov_account_level_data.get(account[1:], ['无', ''])[0] == '市'
                                                 or gov_account_level_data.get(account[1:], ['无', ''])[0] == '省'
                                                 or account == '@环保部发布'):
                            line[29] = 1
                            line[30] = reply[1]
                elif gov_account_level_data.get(reply[0], ['无', ''])[0] == '市':
                    for account in reply[11:]:
                        if len(account) > 1 and (gov_account_level_data.get(account[1:], ['无', ''])[0] == '省'
                                                 or account == '@环保部发布'):
                            line[29] = 1
                            line[30] = reply[1]
                elif gov_account_level_data.get(reply[0], ['无', ''])[0] == '省':
                    for account in reply[11:]:
                        if account == '@环保部发布':
                            line[29] = 1
                            line[30] = reply[1]
        reply_count = 0
        reply_count += (1 if line[17] == 1 else 0)
        reply_count += (1 if line[19] == 1 else 0)
        reply_count += (1 if line[21] == 1 else 0)
        reply_count += (1 if line[23] == 1 else 0)
        line[32] = reply_count
        writer.writerow(line)
        print_list(line)
    print 'all' + str(count)


format_data('data/required_data.csv')
