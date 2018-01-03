# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:03:47 2017

@author: Administrator
"""

import pandas as pd

from pyquery import PyQuery as pq

def ggt():

    main_url='http://data.10jqka.com.cn/hgt/ggtb/board/getGgtPage/page/1/ajax/1/'
    
    main_url_split=main_url.split('page/1')
    
    main_doc=pq(main_url)
    
    table_doc=main_doc('tr')
    
    n=1
    
    text_list=[]
    
    while main_doc:
         
        for each in table_doc:
            
            text=pq(each).text().split()
            
            text_len=len(text)
            
            if text_len<15:
                
                if text_len>10:
                                       
                    text[6]=text[6]+' '+text[7]
                    
                    text.pop(7)               
    
                text_list.append(text)
                    
        print n
                    
        n+=1
        
        next_url=main_url_split[0]+'page/'+str(n)+main_url_split[1]
        
        try:
            main_doc=pq(next_url)
        except:
            main_doc=None
        
        if main_doc:
            table_doc=main_doc('tr')
    
    df_ggt=pd.DataFrame(text_list)
    
    df_ggt.columns=[u'日期',u'流入(港元)',u'余额(港元)',u'成交净买额(港元)',u'买入(港元)',u'卖出(港元)',u'领涨股',u'领涨股涨跌幅',u'恒生指数',u'涨跌幅']
    
    df_ggt.to_csv(u'E:/work/宏观数据/港股通.csv',encoding='gbk',index=None)
