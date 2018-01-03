# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 14:50:07 2017

@author: Administrator
"""

import tushare as ts

import pandas as pd

s1=ts.get_k_data('000001',start='1999-12-30',index=True,ktype='w')

s1['last_close']=s1['close'].shift()

s1['chgper']=s1['close']/s1['last_close']-1
#
#s1['zf']=(s1['high']-s1['low'])/s1['last_close']
#
#s1=s1.loc[:,['date','chgper','zf']]
#
#s1.dropna(inplace=True)
#
#s1.to_excel(u'E:/工作/000001_2.xlsx',index=None)

s2=s1[s1['chgper']<=-0.0780]

high_date=s1[s1['chgper']<=-0.0780].date

for date in high_date:
    
    the_index=s1[s1.date==date].index
    
   # print int(the_index)
    try:
        one_month_chgper=s1.loc[the_index+4,'close'].iat[0]/s1.loc[the_index,'close'].iat[0]-1
    except:
        one_month_chgper='miss'
    
    try:
        two_month_chgper=s1.loc[the_index+8,'close'].iat[0]/s1.loc[the_index,'close'].iat[0]-1
    except:
        two_month_chgper='miss'
    
    s2.loc[the_index,'one_month_chgper']=one_month_chgper
    
    s2.loc[the_index,'two_month_chgper']=two_month_chgper
    
    