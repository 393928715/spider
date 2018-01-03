# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 13:21:01 2017

@author: Administrator
"""

import pandas as pd

from pyquery import PyQuery as pq

def ipo():
    
    main_url='http://datainfo.hexun.com/newstock/'
    
    main_doc=pq('http://datainfo.hexun.com/newstock/xgcx.aspx?data_type=fld_Net_Pay_Date&page=1&tag=2')
    
    table_doc=main_doc('table[id="newstock"]')('tr')
    
    df_ipo=pd.DataFrame()
    
    n=0
    
    while 1:
    
        text_list=[]
        
        for each in table_doc:
            
            text=pq(each).text()
            
            if len(text)>0:
                
                text_list.append(text.split())
            
        df_ipo=df_ipo.append(pd.DataFrame(text_list[1:]))
        
        for each in main_doc('a[class="a1"]'):
            
            each_doc=pq(each)
            
            if each_doc.text() == '下一页':         
                
                next_url=each_doc.attr.href
                
                break
                
            else:
                next_url=None
        
        if next_url:      
            
            next_url=main_url+next_url
            
            main_doc=pq(next_url)
            
            table_doc=main_doc('table[id="newstock"]')('tr')
            
            n+=1
        
            print n
        
        else:
            break
    
    df_ipo.drop([14,15,16,17],axis=1,inplace=True)
    
    df_ipo.columns=[u'股票代码',u'股票简称',u'申购代码',u'发行总数(万)',u'网上发行(万)',u'申购上限',u'发行价',u'发行市盈率',u'申购日期',u'冻结资金',u'中签率',u'中签号',u'中签公布日',u'上市日期']
    
    df_ipo.to_csv(u'E:/work/宏观数据/IPO.csv',encoding='gbk',index=None)

ipo()
