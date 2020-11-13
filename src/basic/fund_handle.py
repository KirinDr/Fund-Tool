# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from basic.notice_util import notice
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


def fund_information(code, sdate, edate, begin):
    begin = pd.to_datetime(begin, format='%Y/%m/%d')
    ret = request(code, sdate, edate, 1)
    soup = BeautifulSoup(ret, 'html.parser')

    pages = re.search('pages:([0-9]+),', ret).group(1)
    pages = int(pages)
    if pages <= 0:
        notice('no response')
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
    df.sort_index(ascending=True, inplace=True)

    return df, df[df['净值日期'] >= begin]


def get_ma(n, df):
    if df.shape[0] < n:
        return None

    date_time = []
    ma = []

    sum_val = 0
    pre = 0
    for i in range(n - 1):
        sum_val += df.iloc[i,].loc['单位净值']
    for i in range(n, df.shape[0]):
        sum_val += df.iloc[i,].loc['单位净值']
        if i > n:
            sum_val -= df.iloc[pre,].loc['单位净值']
            pre += 1
        date_time.append(df.iloc[i,].loc['净值日期'])
        ma.append(sum_val / n)
    n_df = pd.DataFrame()
    n_df['净值日期'] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df['单位净值'] = ma

    return n_df



def get_dif(ma12, ma26):
    # MA12和MA26时间对齐
    if ma12.shape[0] != ma26.shape[0]:
        min_date = ma26.iloc[0,].loc['净值日期']
        ma12 = ma12[ma12['净值日期'] >= min_date]

    dif = []
    date_time = []

    for i in range(ma12.shape[0]):
        date_time.append(ma12.iloc[i,].loc['净值日期'])
        dif.append(ma12.iloc[i,].loc['单位净值'] - ma26.iloc[i,].loc['单位净值'])

    n_df = pd.DataFrame()
    n_df['净值日期'] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df['单位净值'] = dif
    return n_df


def get_dea(dif):
    n = 9
    return get_ma(n, dif)


def get_macd_bar(dif, dea):
    # 时间对齐
    if dif.shape[0] != dea.shape[0]:
        min_date = dea.iloc[0,].loc['净值日期']
        dif = dif[dif['净值日期'] >= min_date]

    bar = []
    date_time = []

    for i in range(dif.shape[0]):
        date_time.append(dif.iloc[i,].loc['净值日期'])
        bar.append((dif.iloc[i,].loc['单位净值'] - dea.iloc[i,].loc['单位净值']) * 2)

    n_df = pd.DataFrame()
    n_df['净值日期'] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df['单位净值'] = bar
    return n_df



