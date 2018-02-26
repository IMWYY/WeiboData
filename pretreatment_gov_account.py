# -*- coding:utf-8 -*-
import csv

import re


def format_gov_account(input_path, output_path):
    """
    处理所有的政府账号 提取行政区划
    :param input_path: 输入路径
    :param output_path: 输出路径
    """

    titles = ['政府帐号名', '介绍', '级别', '是否环保部门', '行政区划']
    # 回复的数据
    reader = csv.reader(open(input_path, 'r'))
    writer = csv.writer(open(output_path, 'w'))
    writer.writerow(titles)

    for row in reader:
        province = city = county = area = ''
        match_obj = re.match(
            r'.*?((北京)|(天津)|(河北)|(辽宁)|(上海)|(江苏)|(浙江)|(福建)|(山东)|(广东)|'
            r'(海南)|(山西)|(吉林)|(黑龙江)|(安徽)|(江西)|(河南)|(湖北)|(湖南)|(四川)|(重庆)|'
            r'(贵州)|(云南)|(西藏)|(陕西)|(甘肃)|(青海)|(宁夏)|(新疆)|(广西)|(内蒙古)).*?',
            row[1], re.M | re.I)
        if match_obj:
            province = match_obj.group(1)
        pos = row[1].find('市')
        if pos > 1:
            city = row[1][pos - 6:pos]
            print city
        pos = row[1].find('县')
        if pos > 1:
            county = row[1][pos - 6:pos]
            print county
        pos = row[1].find('区')
        if pos > 1:
            area = row[1][pos - 6:pos]
            print area

        addr = province + ('省' if province else '') + city + ('市' if city else '') + county + (
            '县' if county else '') + area + ('区' if area else '')

        writer.writerow([row[0], row[1], row[2], row[3], addr])


# format_gov_account('data/gov_none_accounts.csv', 'data/gov_none_accounts_new.csv')
format_gov_account('data/gov_accounts.csv', 'data/gov_accounts_new.csv')
