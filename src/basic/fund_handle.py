# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from basic.utils import notice
import matplotlib.pyplot as plt
from basic.config import *
# 中文设置
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False


def request(url, param=None):
    r = requests.get(url=url, params=param)
    r.raise_for_status()
    return r.text


def fund_information(code, sdate, edate, begin):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    param = {
        'type': 'lsjz',
        'code': code,
        'page': 1,
        'sdate': sdate,
        'edate': edate,
        'per': 20
    }
    begin = pd.to_datetime(begin, format='%Y/%m/%d')
    ret = request(url, param)
    soup = BeautifulSoup(ret, 'html.parser')

    pages = re.search('pages:([0-9]+),', ret).group(1)
    pages = int(pages)
    if pages <= 0:
        notice('no response')
        return None, None

    headers = []
    for head in soup.find_all('th'):
        headers.append(head.contents[0])

    data = []
    for page in range(1, pages + 1):
        param['page'] = page
        html = request(url, param)
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


def fund_list():
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    res = request(url)
    fund_ls = re.search('var r = (.*?);', res).group(1)
    fund_ls = np.array(eval(fund_ls))
    fund_dict = {}
    fund_dict['code'] = fund_ls[:,0]
    fund_dict['ch_name'] = fund_ls[:, 2]
    fund_dict['code'] = fund_dict['code'].astype(str)
    df = pd.DataFrame(fund_dict, index=fund_ls[:,0])
    return df


Main_Control = fund_list()


def get_fund_name(code):
    code = str(code)
    return Main_Control.loc[code,].loc['ch_name']


def get_ma(n, df):
    if df.shape[0] < n:
        return None

    date_time = []
    ma = []

    sum_val = 0
    pre = 0
    for i in range(0, df.shape[0]):
        sum_val += df.iloc[i,].loc[SUM_VAL_FIELD]
        if i >= n:
            sum_val -= df.iloc[pre,].loc[SUM_VAL_FIELD]
            pre += 1
        if i >= n - 1:
            date_time.append(df.iloc[i,].loc[DATE_FIELD])
            ma.append(sum_val / n)
    n_df = pd.DataFrame()
    n_df[DATE_FIELD] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df[SUM_VAL_FIELD] = ma

    return n_df



def get_dif(ma12, ma26):
    # MA12和MA26时间对齐
    if ma12.shape[0] != ma26.shape[0]:
        min_date = ma26.iloc[0,].loc[DATE_FIELD]
        ma12 = ma12[ma12[DATE_FIELD] >= min_date]

    dif = []
    date_time = []

    for i in range(ma12.shape[0]):
        date_time.append(ma12.iloc[i,].loc[DATE_FIELD])
        dif.append(ma12.iloc[i,].loc[SUM_VAL_FIELD] - ma26.iloc[i,].loc[SUM_VAL_FIELD])

    n_df = pd.DataFrame()
    n_df[DATE_FIELD] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df[SUM_VAL_FIELD] = dif
    return n_df


def get_dea(dif):
    n = 9
    return get_ma(n, dif)


def get_macd_bar(dif, dea):
    # 时间对齐
    if dif.shape[0] != dea.shape[0]:
        min_date = dea.iloc[0,].loc[DATE_FIELD]
        dif = dif[dif[DATE_FIELD] >= min_date]

    bar = []
    date_time = []

    for i in range(dif.shape[0]):
        date_time.append(dif.iloc[i,].loc[DATE_FIELD])
        bar.append((dif.iloc[i,].loc[SUM_VAL_FIELD] - dea.iloc[i,].loc[SUM_VAL_FIELD]) * 2)

    n_df = pd.DataFrame()
    n_df[DATE_FIELD] = pd.to_datetime(date_time, format='%Y/%m/%d')
    n_df[SUM_VAL_FIELD] = bar
    return n_df


fund_list()


