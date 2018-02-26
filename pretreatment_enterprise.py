# -*- coding:utf-8 -*-
"""
处理企业数据 合并去重
"""
import csv


def format_enterprise():
    """
    将企业名称干扰的关键字去除 如有限公司等
    :return:
    """
    # 打开文件
    reader = csv.reader(open('data/enterprise_old.csv', 'r'))
    # 关键字文件
    keyword = open('data/enterprise.csv', 'w')
    writer = csv.writer(keyword)

    count = 0
    for line in reader:
        name = line[0]
        if not name:
            continue
        try:
            if name.index("有限公司") > 0:
                line[0] = name[0:name.index("有限公司")]
                writer.writerow(line)
                count += 1
        except ValueError:
            try:
                if name.index("有限责任公司") > 0:
                    line[0] = name[0:name.index("有限责任公司")]
                    writer.writerow(line)
                    count += 1
            except ValueError:
                try:
                    if name.index("污水处理厂") > 0:
                        writer.writerow(line)
                except ValueError:
                    writer.writerow(line)
                    count += 1
    print count


def format_enterprise_characteristics(output_path):
    """
    将企业特征信息和企业信息整合到一起 信息包括：
    企业名称,地点,行政编号,年份,污染类型,法人编号,
    企业状态,登记注册类型,企业规模,行业类别代码,行业类别名称,工业总产值当年价格万元,年正常生产时间小时
    """
    # 打开文件
    enterprise_reader = csv.reader(open('data/enterprise.csv', 'r'))
    characteristics_reader = csv.reader(open('data/enterprise_characteristics.csv', 'r'))

    writer = csv.writer(open(output_path, 'w'))

    characteristics_data = {}
    characteristics_data8 = {}
    characteristics_data7 = {}
    for row in characteristics_reader:
        if not row[3]:
            continue
        code = row[3].replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        if code and len(code) >= 9:
            characteristics_data[code[:9]] = row
        if code and len(code) >= 8:
            characteristics_data8[code[:8]] = row
        if code and len(code) >= 7:
            characteristics_data7[code[:7]] = row

    count = 0
    all_count = 0
    for row in enterprise_reader:
        all_count += 1
        key = row[5][:9] if len(row[5]) > 9 else row[5]
        characteristics = characteristics_data.get(key)
        if not characteristics:
            characteristics = characteristics_data8.get(key)
        if not characteristics:
            characteristics = characteristics_data7.get(key)
        if not characteristics:
            print key
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], '', '', '', '', '', '', ''])
            count += 1
        else:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], characteristics[5], characteristics[6],
                             characteristics[7], characteristics[8], characteristics[9],
                             characteristics[10], characteristics[11]])
    print count
    print all_count


def format_PGDP():
    reader = csv.reader(open('data/PGDP.csv', 'r'))
    writer = csv.writer(open('data/PGDP_new.csv', 'w'))
    for row in reader:
        if row[1]:
            row[1] = row[1].replace('省', '').replace('市', '')
        writer.writerow(row)

        # reader = csv.reader(open('data/enterprise_characteristics.csv', 'r'))
        # count = 0
        # for row in reader:
        #     if row[10] and row[2] == '2014':
        #         count += 1
        #         print row[2]
        # print count


# format_enterprise_characteristics('data/enterprise_new.csv')
format_PGDP()
