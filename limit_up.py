# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 15:23:08 2017

@author: Administrator
"""
from sqlalchemy import create_engine 

import pandas as pd

import tushare as ts

import numpy as np

def limit_up(df):
    
    if df.hq_close.count()>20:
    
        df['chgper']=(df['hq_close']/df['hq_close'].shift()-1)*100
        
        df['last_chgper']=df['chgper'].shift()
        
        df=df[df.chgper+df.last_chgper>19.8]
        
        #df=df[df.hq_open != df.hq_close]

        return df

def limit_up_sum(df):
    
    df['lb']=df.hq_close.count()    

    return df['lb'].iat[0]

def plot(df_stock):
    
        import xlsxwriter
        
        wbk=xlsxwriter.Workbook(u'E:\\work\\报表\\连板跟踪\\连板个股数.xlsx')
    
        pic_sheet=wbk.add_worksheet('pic')
        
        data_sheet=wbk.add_worksheet('data')
    
        data_len=len(df_stock)
        
        data_sheet.write_row(0,0,[u'日期',u'连板数'])
    
        for i in xrange(len(df_stock)):
            
            data_sheet.write_row(i+1,0,df_stock.iloc[i])
        
        lb_chart=wbk.add_chart({'type':'line'})
        
        lb_chart.add_series({
         'name':u'连板数',
         'categories':['data', 1, 0, 1+data_len, 0],
         'values':['data', 1, 1, 1+data_len,1],
         'line':{'width': 1.5},#FF6666
         })       
         
        lb_chart.set_x_axis({'label_position': 'low',})    
                            
        lb_chart.set_y_axis({'major_gridlines':False,})      
         
        lb_chart.set_title({'none':True})
        
        lb_chart.set_size({'width':800,'height':400})
        
        lbzs_chart=wbk.add_chart({'type':'line'})
        
        lbzs_chart.add_series({
         'name':u'连板增速',
         'categories':['data', 1, 0, 1+data_len, 0],
         'values':['data', 1, 2, 1+data_len,2],
         'line':{'color':'#FF6666','width': 1.5},
         })       
         
        lbzs_chart.set_title({'none':True})
        
        lbzs_chart.set_size({'width':800,'height':400})
        
        lbzs_chart.set_y_axis({
                           #'interval_unit': 5 ,
                           'major_gridlines':False,
                           })                                
        
        pic_sheet.insert_chart(0,0,lb_chart)
        
        pic_sheet.insert_chart(21,0,lbzs_chart)
        
        wbk.close()

if __name__ == '__main__':

    engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
    
    df_stock=pd.read_sql('select hq_code,hq_date,hq_close,hq_open from hstockquotationday as hiq where hiq.index > "2017-06-01" ',con=engine)#and hiq.index< "2017-10-01"
    
    df_stock=df_stock.groupby('hq_code').apply(limit_up)
    
    df_stock=df_stock.groupby('hq_date').apply(limit_up_sum)
    
    df_stock=df_stock.to_frame('lb')

    df_sz=ts.get_k_data('000001',index=True)
     
    df_sz['date']=pd.to_datetime(df_sz['date'])
     
    df_sz.set_index('date',inplace=True)
    
    df_stock=df_stock.reindex(df_sz.index)
    
    df_stock.fillna(0,inplace=True)
 
    df_stock['lb_zs']=df_stock['lb']/df_stock['lb'].shift()-1
     
    df_stock.reset_index(inplace=True)
    
    df_stock['date']=df_stock['date'].astype(str)
    
    df_stock=df_stock.replace(np.inf, 2)
    
    df_stock.dropna(inplace=True)
    
    plot(df_stock)
