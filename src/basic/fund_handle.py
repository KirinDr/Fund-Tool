# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 中文设置
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False


def request(code, sdate, edate, page):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    param = {
                'type': 'lsjz',
                'code': code,
                'page': page,
                'sdate': sdate,
                'edate': edate,
                'per': 20
            }
    r = requests.get(url=url, params=param)
    r.raise_for_status()
    return r.text


def fund_information(code, sdate, edate):
    ret = request(code, sdate, edate, 1)
    soup = BeautifulSoup(ret, 'html.parser')

    pages = re.search('pages:([0-9]+),', ret).group(1)
    pages = int(pages)
    if pages <= 0:
        return None

    headers = []
    for head in soup.find_all('th'):
        headers.append(head.contents[0])

    data = []
    for page in range(1, pages + 1):
        html = request(code, sdate, edate, page)
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all('tbody')[0].find_all('tr'):
            row_data = []
            for td in tag.find_all('td'):
                if td.contents:
                    row_data.append(td.contents[0])
                else:
                    row_data.append(np.nan)
            data.append(row_data)

    df = pd.DataFrame()
    data = np.array(data)
    for h in range(len(headers)):
        df[headers[h]] = data[:, h]

    df['净值日期'] = pd.to_datetime(df['净值日期'], format='%Y/%m/%d')
    df['单位净值'] = df['单位净值'].astype(float)
    df['累计净值'] = df['累计净值'].astype(float)
    df['日增长率'] = df['日增长率'].str.strip('%').astype(float)
    df = df.set_index('净值日期', drop=False)
    df.sort_index()

    return df
