# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 14:45:56 2017

@author: Administrator
"""
from pyquery import PyQuery as pq

import pandas as pd

zc=True

def zjc(zc):
   
    if zc==True:
        main_url='http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/GDZC/GetGDZC?tkn=eastmoney&cfg=gdzc&secucode=&fx=1&sharehdname=&pageSize=50&pageNum=1&sortFields=BDJZ&sortDirec=1&startDate=&endDate='
    else:
        main_url='http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/GDZC/GetGDZC?tkn=eastmoney&cfg=gdzc&secucode=&fx=2&sharehdname=&pageSize=50&pageNum=1&sortFields=BDJZ&sortDirec=1&startDate=&endDate='
      
    main_doc=pq(main_url)
    
    table_doc=main_doc.text()
    
    table=eval(table_doc)['Data'][0]
    
    total_page=table['TotalPage']
    
    for i in range(2,total_page+1):
        
        text_list=map(lambda x:x.split('|'),table['Data'])
        
        if i==2:
        
            df_zc=pd.DataFrame(text_list)
        
        else:
            df_zc=df_zc.append(pd.DataFrame(text_list))
        
        url_part=main_url.split('pageNum=1')
          
        next_url=url_part[0]+'pageNum='+str(i)+url_part[1]
    
        main_doc=pq(next_url)
        
        table_doc=main_doc.text()
        
        table=eval(table_doc)['Data'][0]
        
        print i
        
    df_zc.drop([0,1,3,4,11],axis=1,inplace=True)
    
    df_zc.columns=['code','name','holder','type','chg','chgper_flow','chgper','hold','holdper','hold_flow','holdper_flow','begin','end','announcement']
    
    try:
        df_zc.to_csv(u'E:/work/宏观数据/增持.csv',encoding='gbk',index=None)
    except:
        df_zc.to_csv(u'E:/work/宏观数据/增持.csv',encoding='utf-8',index=None)
    
zjc(zc=False)