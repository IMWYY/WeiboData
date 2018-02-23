# -*- coding:utf-8 -*-
"""
处理企业数据 合并去重
"""
import csv


def format_enterprise():
    # 打开文件
    reader = csv.reader(open('data/enterprise.csv', 'r'))
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


format_enterprise()