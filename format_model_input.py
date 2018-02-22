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
5* Forward     转发量
6* Comment     评论量
7* Praise      点赞量
8* Position    中央/上级政府关注  (@地方政府微博帐号表征为1，若无@则表征为0)
9* Forest      森林覆盖率
10*Industry    工业发电量
11*year         年份
"""


def format_model_input(input_path, output_path):
    """
    根据数据需求格式模型输入
    :return:
    """
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

    titles = ['地方政府回应', '微博投诉', '污染所在地区', '人均国内生产总值', '企业特征', '转发量', '评论量',
              '点赞量', '中央/上级政府关注', '森林覆盖率', '工业发电量']

    out = open(output_path, 'w')
    writer = csv.writer(out)
    writer.writerow(titles)

    first_row = True
    csv_reader = csv.reader(open(input_path, 'r'))
    for row in csv_reader:
        # 跳过标题栏
        if first_row:
            first_row = False
            continue
        if row and len(row) == 26:
            calculated_data = [0 for x in xrange(11)]
            valid = True

            province = ''
            match_obj = re.match(
                r'.*?((北京)|(天津)|(河北)|(辽宁)|(上海)|(江苏)|(浙江)|(福建)|(山东)|(广东)|'
                r'(海南)|(山西)|(吉林)|(黑龙江)|(安徽)|(江西)|(河南)|(湖北)|(湖南)|(四川)|(重庆)|'
                r'(贵州)|(云南)|(西藏)|(陕西)|(甘肃)|(青海)|(宁夏)|(新疆)|(广西)|(内蒙古)).*?',
                row[6], re.M | re.I)
            if match_obj:
                province = match_obj.group(1)
            else:
                valid = False

            # 地方政府回应 (是否回应/回应的比例)
            if valid and (row[12] or row[14] == 1 or row[16] == 1 or row[18] == 1 or [20] == 1):
                calculated_data[0] = 1

            # 微博投诉(有无@/@的数量)
            calculated_data[1] = row[10]

            # 污染所在地区(东部地区为1、中西部地区为0)
            if valid and province and province in eastern:
                calculated_data[2] = 1
            elif valid and province and province in western:
                calculated_data[2] = 0
            else:
                valid = False

            # 转发量
            calculated_data[5] = row[7]

            # 评论量
            calculated_data[6] = row[8]

            # 点赞量
            calculated_data[7] = row[9]

            # 中央/上级政府关注  (@地方政府微博帐号表征为1，若无@则表征为0)
            calculated_data[8] = row[22]

            # 森林覆盖率
            if valid and province and province in forest_data.keys():
                calculated_data[9] = forest_data[row[6]]
            else:
                valid = False

            # 工业发电量
            if valid and province and province in electricity_data.keys():
                calculated_data[10] = electricity_data[row[6]]
            else:
                valid = False

            # 时间
            if row[0] and valid:
                calculated_data[10] = row[0]  # todo 年份

            if valid:
                writer.writerow(calculated_data)
