# -*- coding:utf-8 -*-
import csv

import copy

"""
将微博评论的数据处理成每个微博及其评论一行的形式
评论只保存有关的评论 及回复的账号是政府账号的评论
如果微博没有评论将直接剔除
"""


def format_reply(input_path, gov_account_data, data):
    """
    筛选回复内容 保留原微博和有关的评论
    :param gov_account_data: 政府账号的数据
    :param input_path: 输入路径
    :param data: 输出的数据列表
    """
    # 回复的数据
    reply_reader = csv.reader(open(input_path, 'r'))

    temp = []
    has_comment = False
    for row in reply_reader:
        if row[0] and row[0] != '' and row[1] != '' and len(row) >= 3:
            if len(row[2]) < 10:  # 原微博数据 将上一个微博数据保存 并重新初始化新微博数据
                if temp and has_comment:
                    data.append(temp)
                    has_comment = False
                temp = copy.deepcopy(row[:11])
                # 合并@列表
                temp.append(''.join(row[11:]))
            if len(row[2]) > 10 and row[0] in gov_account_data:  # 将有关的评论数据追加在后面的列
                has_comment = True
                temp.append(row[0])  # 评论账号
                temp.append(row[2])  # 评论时间
                temp.append(row[1])  # 评论内容


def process_reply(output_path):
    """
    筛选回复内容 保留原微博和有关的评论
    :param output_path: 输出路径
    """
    # 政府账号的数据
    gov_account_data = []
    gov_account_reader = csv.reader(open('data/gov_accounts.csv', 'r'))
    for row in gov_account_reader:
        gov_account_data.append(row[0])

    # 回复的数据
    reply_data = []
    format_reply('data/weiboComment2014.csv', gov_account_data, reply_data)
    format_reply('data/weiboComment2015.csv', gov_account_data, reply_data)
    format_reply('data/weiboComment2016.csv', gov_account_data, reply_data)
    format_reply('data/weiboComment2017.csv', gov_account_data, reply_data)

    print len(reply_data)

    out = open(output_path, 'w')
    writer = csv.writer(out)
    for data in reply_data:
        writer.writerow(data)


process_reply('data/weiboComment_format.csv')
