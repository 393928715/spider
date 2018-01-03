# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 09:15:49 2017

@author: Administrator
"""

from pyquery import PyQuery as pq

import pandas as pd

main_doc=pq('http://data.eastmoney.com/cjsj/yzgptjnew.html')

table_doc=main_doc('tr[class=""]')

text_list=[]

for each in table_doc:
    
    text=pq(each).text().split()
    
    text_list.append(text)

df_new_investor=pd.DataFrame(text_list,columns=['date','new_thwk','new_peak','final_thwk','final_peak','hold_thwk','hold_peak','trade_thwk','trade_peak','per_thwk','per_peak'])

df_new_investor.to_csv(u'E:\\work\\宏观数据\\新增投资者.csv',index=None)
