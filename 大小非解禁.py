# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 15:20:57 2017

@author: Administrator
"""
import pandas as pd

from pyquery import PyQuery as pq

def dxf():
    
    main_url='http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=FD&sty=BST&st=3&sr=true&fd=2017&stat=1&js=LoadDataResult([(x)])'
    
    main_url_split=main_url.split('stat=1')
    
    text_list=[]
    
    main_doc=pq(main_url)
    
    for i in range(1,13):
    
        text=main_doc.text()
        
        text=text[text.find('[')+2:text.find('"]')]
        
        text=text.split('","')
        
        text=map(lambda x:x.split(','),text)
        
        text_list.extend(text)
        
        next_url=main_url_split[0]+'stat='+str(i+1)+main_url_split[1]
        
        main_doc=pq(next_url)
        
        print i
    
    df_dxf=pd.DataFrame(text_list)
    
    df_dxf.drop([0,9,10,11,12],axis=1,inplace=True)
    
    df_dxf.columns=[u'代码',u'名称',u'相关',u'解除限售日',u'占股本总比例%',u'数量(万股)',u'收盘价(元)',u'市值(亿元)']
    
    df_dxf.sort_values(u'解除限售日',ascending=False,inplace=True)
    
    df_dxf.to_csv(u'E:/work/宏观数据/大小非解禁.csv',encoding='gbk',index=None)