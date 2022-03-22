# -*- coding:utf-8 -*-

import json
import requests
import logging
import time
from jinja2 import FileSystemLoader, Environment
from enum import Enum

HUGE_HAPPY_DEFAULT = (
    # put your number here
    (('**', '**', '**', '**', '**'), ('**', '**')),
)

DOUBLE_COLOR_DEFAULT = (
    # put your number here
    (('**', '**', '**', '**', '**', '**'), ('**',)),
)

logging.basicConfig(level=logging.INFO,
                    filename='./spider.log',
                    filemode='a',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class lottory_type(Enum):
    HUGE_HAPPY = '大乐透'
    DOUBLE_COLOR = '双色球'

class result:
    def __init__(self, type: lottory_type, id: str, red_ball: tuple, blue_ball: tuple, occur_time: str, pool: int) -> None:
        self.type = type
        self.id = id
        self.red_ball = red_ball
        self.blue_ball = blue_ball
        self.occur_time = occur_time
        self.pool = pool
        self.records = []

    def __str__(self) -> str:
        return f'{self.type } #{self.id} -> ({self.red_ball} - {self.blue_ball}) on {self.occur_time}, pool is {self.pool}'

    def __rper__(self) -> str:
        return self.__str__()

class ball:
    def __init__(self, num: str, color = 'white') -> None:
        self.num = num
        self.color = color

    def __str__(self) -> str:
        return f'{self.num} in {self.color}'

    def __repr__(self) -> str:
        return self.__str__()

class record:
    def __init__(self, result: tuple, bouns: int) -> None:
        self.result = result
        self.bouns = bouns

    def __str__(self) -> str:
        return f'{self.result} -> {self.bouns}'

    def __repr__(self) -> str:
        return self.__str__()

def fetch_huge_happy_result() -> result:
    response = requests.get('https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize=50&isVerify=1&pageNo=1&termLimits=1')
    result_obj = json.loads(response.content)['value']['list'][0]
    result_arr = result_obj['lotteryDrawResult'].split(' ')
    final_result = result(lottory_type.HUGE_HAPPY, result_obj['lotteryDrawNum'], tuple(result_arr[:5]), tuple(result_arr[5:]), result_obj['lotteryDrawTime'], int(float(result_obj['poolBalanceAfterdraw'].replace(',', ''))))
    logging.info(final_result)
    return final_result

def huge_happy_bouns(origin: tuple, result: tuple) -> int:
    red_hit = len(set(origin[0]) & set(result[0]))
    blue_hit = len(set(origin[1]) & set(result[1]))
    if red_hit == 5 and blue_hit == 2:
        return 10,000,000
    if red_hit == 5 and blue_hit == 1:
        return 5,000,000
    if red_hit == 5 and blue_hit == 0:
        return 10,000
    if red_hit == 4 and blue_hit == 2:
        return 3,000
    if red_hit == 4 and blue_hit == 1:
        return 300
    if red_hit == 3 and blue_hit == 2:
        return 200
    if red_hit == 4 and blue_hit == 0:
        return 100
    if (red_hit == 3 and blue_hit == 1) or (red_hit == 2 and blue_hit == 2):
        return 15
    if  (red_hit == 3 and blue_hit == 0) or (red_hit == 1 and blue_hit == 2) or (red_hit == 2 and blue_hit == 1) or (red_hit == 0 and blue_hit == 2):
        return 5
    return 0

def fetch_double_color_result() -> result:
    response = requests.get('http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=1')
    result_obj = json.loads(response.content)['result'][0]
    red_result = result_obj['red'].split(',')
    blue_result = result_obj['blue'].split(',')
    final_result = result(lottory_type.DOUBLE_COLOR, result_obj['code'], tuple(red_result), tuple(blue_result), result_obj['date'][:10], result_obj['poolmoney'])
    logging.info(final_result)
    return final_result

def double_color_bouns(origin: tuple, result: tuple) -> int:
    red_hit = len(set(origin[0]) & set(result[0]))
    blue_hit = len(set(origin[1]) & set(result[1]))
    if red_hit == 6 and blue_hit == 1:
        return 10,000,000
    if red_hit == 6 and blue_hit == 0:
        return 5,000,000
    if red_hit == 5 and blue_hit == 1:
        return 3,000
    if (red_hit == 5 and blue_hit == 0) or (red_hit == 4 and blue_hit == 1):
        return 200
    if (red_hit == 4 and blue_hit == 0) or (red_hit == 3 and blue_hit == 1):
        return 10
    if  (red_hit == 2 and blue_hit == 1) or (red_hit == 1 and blue_hit == 1) or (red_hit == 0 and blue_hit == 1):
        return 5
    return 0

if __name__ == '__main__':
    today = time.strftime('%Y-%m-%d')
    total = 0
    
    huge_happy = fetch_huge_happy_result()
    for row in HUGE_HAPPY_DEFAULT:
        bouns = huge_happy_bouns(row, (huge_happy.red_ball, huge_happy.blue_ball))
        if huge_happy.occur_time == today:
            total += bouns
        ball_list = []
        for red in row[0]:
            if red in huge_happy.red_ball:
                ball_list.append(ball(red, 'red'))
            else:
                ball_list.append(ball(red))
        for blue in row[1]:
            if blue in huge_happy.blue_ball:
                ball_list.append(ball(blue, 'blue'))
            else:
                ball_list.append(ball(blue))
        huge_happy.records.append(record(ball_list, bouns))
    logging.info(huge_happy.records)

    double_color = fetch_double_color_result()
    for row in DOUBLE_COLOR_DEFAULT:
        bouns = double_color_bouns(row, (double_color.red_ball, double_color.blue_ball))
        if double_color.occur_time == today:
            total += bouns
        ball_list = []
        for red in row[0]:
            if red in double_color.red_ball:
                ball_list.append(ball(red, 'red'))
            else:
                ball_list.append(ball(red))
        for blue in row[1]:
            if blue in double_color.blue_ball:
                ball_list.append(ball(blue, 'blue'))
            else:
                ball_list.append(ball(blue))
        double_color.records.append(record(ball_list, bouns))
    logging.info(double_color.records)

    template = Environment(loader=FileSystemLoader('./static/')).get_template('index.html')
    html = template.render(huge_happy = huge_happy, double_color = double_color)

    # TODO    
    # notify yourself with your email or put html on your webiste
    # https://github.com/easychen/pushdeer recommended
