# -*- coding:utf-8 -*-

import copy
import csv
import datetime


def time_in_range(x, y):
    """
    :param x: 回复的时间
    :param y: 原微博发布的时间
    :return:  回复时间是否再原微博发布的时间后的两月以内
    """
    d1 = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(y, '%Y-%m-%d %H:%M:%S')
    return 0 <= (d1 - d2).days <= 60


def correspond_reply(weibo_at, gov_reply, output):
    """
    匹配微博和政府的回应
    :param output: 输出的文件
    :param weibo_at:  weibo_at的文件路径
    :param gov_reply: gov_reply的文件路径
    """
    weibo_at_data = []
    gov_reply_data = []
    weibo_at_reader = csv.reader(open(weibo_at, 'r'))
    gov_reply_reader = csv.reader(open(gov_reply, 'r'))
    for row in weibo_at_reader:
        weibo_at_data.append(row)
    for row in gov_reply_reader:
        gov_reply_data.append(row)

    gov_reply_data.sort(key=lambda x: x[5])
    weibo_at_data.sort(key=lambda x: x[5])

    out = open(output, 'w')
    writer = csv.writer(out)
    titles = ['政府是否回应', '发博账号', '内容', '点赞量', '评论量', '转发量', '发布时间', '评论链接', '涉及企业', '是否转发',
              '转发自', '转发内容', '@的账号', '@的政府账号数量',
              '政府回复的类型(0反@1转发2评论3)', '政府回复的账号', '回复内容', '点赞量', '评论量', '转发量', '发布时间', '评论链接', '涉及企业', '是否转发',
              '转发自', '转发内容', '@的账号']
    writer.writerow(titles)

    no_reply = False
    count = 0

    for weibo in weibo_at_data:
        # 如果微博发布时间比最晚的回复时间还要晚 直接退出
        # print '1：' + weibo[5]
        # print '2：' + gov_reply_data[len(gov_reply_data)-1][5]
        weibo.insert(0, 0)  # 利用第一个标示位 表示需要筛选回复
        if not no_reply and weibo[6] > gov_reply_data[len(gov_reply_data) - 1][5]:
            no_reply = True
        has_reply = False
        if no_reply:
            temp = copy.deepcopy(weibo[:12])
            # 合并@
            temp.append(''.join(weibo[12:len(weibo) - 1]))
            temp.append(weibo[len(weibo) - 1])
            writer.writerow(temp)
            print 'no reply and more'
        else:
            for reply in gov_reply_data:
                # 在回复的时间范围内 且 原微博@到该回复账号 且 涉及企业相同
                if time_in_range(reply[5], weibo[6]) and ('@' + reply[0]) in weibo[12:len(weibo) - 1] \
                        and weibo[8] == reply[7]:
                    print (reply[8] + ' ' + reply[9] + weibo[9] + ' ' + weibo[1] + ' ' + weibo[10])
                    # 反@
                    if ('@' + weibo[1]) in reply[11:]:
                        temp = copy.deepcopy(weibo[:12])
                        temp[0] = 1
                        # 合并@
                        temp.append(''.join(weibo[12:len(weibo) - 1]))
                        temp.append(weibo[len(weibo) - 1])
                        temp.append(0)
                        temp.extend(reply[:11])
                        temp.append(''.join(reply[11:]))
                        writer.writerow(temp)
                        count += 1
                        print count
                        has_reply = True
                    # 微博转发
                    elif reply[8] == 1 and (reply[9] == weibo[1] or (weibo[9] == 1 and reply[9] == weibo[10])):
                        temp = copy.deepcopy(weibo[:12])
                        temp[0] = 1
                        # 合并@列表
                        temp.append(''.join(weibo[12:len(weibo) - 1]))
                        temp.append(weibo[len(weibo) - 1])
                        temp.append(1)
                        temp.extend(reply[:11])
                        temp.append(''.join(reply[11:]))
                        writer.writerow(temp)
                        count += 1
                        print count
                        has_reply = True
            if not has_reply:
                temp = copy.deepcopy(weibo[:12])
                # 合并@
                temp.append(''.join(weibo[12:len(weibo) - 1]))
                temp.append(weibo[len(weibo) - 1])
                writer.writerow(temp)
                print 'weibo has no reply '
    print count


def test():
    temp = []
    tt = [0, 2, 3]
    temp.append(tt)
    tt = [4, 5, 6]
    print temp

# correspond_reply('data/weiboAt.csv', 'data/govReply.csv', 'data/at_and_reply.csv')
# correspond_reply('data/weiboAt2015.csv', 'data/govReply2015.csv', 'data/at_and_reply2015.csv')
# correspond_reply('data/weiboAt2016.csv', 'data/govReply2016.csv', 'data/at_and_reply2016.csv')
# correspond_reply('data/weiboAt2017.csv', 'data/govReply2017.csv', 'data/at_and_reply2017.csv')
# test()
