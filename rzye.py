# -*- coding: utf-8 -*-
"""
Created on Fri Nov 03 15:54:25 2017

@author: Administrator
"""
import xlsxwriter

from pyquery import PyQuery as pq

import pandas as pd

class Rzye:
    
    def __init__(self):
        
        self.data_dir=u'E:\\work\\宏观数据\\rzye_index.csv'
        
        self.form_dir=u'E:\\work\\宏观数据\\rzye_index.csv'
    
    def get_rzye(self):
    
        main_url='http://data.cfi.cn/'
        
        first_url='http://data.cfi.cn/cfidata.aspx?sortfd=&sortway=&curpage=1&fr=content&ndk=A0A1934A1939A4569A5232&xztj=&mystock='
        
        page_url=first_url
        
        table_doc=pq(page_url)("table[class='table_data']")('tr')
        
        n=0
        
        text=table_doc.text()
        
        df_rz=pd.DataFrame()
        
        while table_doc:
        
            text_list=[]
            
            for each in table_doc:
                
                text=pq(each).text().split()
                
                text_list.append(text)
                    
            df=pd.DataFrame(text_list[1:],columns=text_list[0])
            
            df_rz=df_rz.append(df)
            
            #得到下一页链接
            try:
                next_url=main_url+pq(page_url)('a[style="font-size:11pt"]').attr.href
            except TypeError:
                next_url=None
                
            if next_url and (next_url != first_url):
                
                page_url=next_url
            
            else:
                
                page_url=None
            
            table_doc=pq(page_url)("table[class='table_data']")('tr')
            
            n+=1
            
            print n
        
        df_rz.sort_values(u'截止日',inplace=True)
        
        df_rz.to_csv(self.data_dir,encoding='gbk',index=None)
        
        return df
    
    def plot_rzye(self):
        
        df_rzye=pd.read_csv(self.form_dir,encoding='gbk')
        
        #截取2017年以后数据
        df_rzye=df_rzye[df_rzye[u'截止日']>='2017-01-01']
        
        df_rzye[u'上证涨跌%']=df_rzye[u'上证指数']/df_rzye[u'上证指数'].iat[0]-1
        
        df_rzye[u'深成涨跌%']=df_rzye[u'深成指数']/df_rzye[u'深成指数'].iat[0]-1
        
        df_rzye[u'中小板涨跌%']=df_rzye[u'中小板指数']/df_rzye[u'中小板指数'].iat[0]-1
        
        df_rzye[u'创业板指数']=df_rzye[u'创业板指数'].astype(float)
        
        df_rzye[u'创业板涨跌%']=df_rzye[u'创业板指数']/df_rzye[u'创业板指数'].iat[0]-1
        
        df_rzye.rename(columns={u'上证涨跌%':u'上证净值',u'深成涨跌%':u'深成净值',u'中小板涨跌%':u'中小板净值',u'创业板涨跌%':u'创业板净值'},inplace=True)
        
        header=list(df_rzye.columns)
        
        shye_col=header.index(u'上海融资额(亿)')
        
        szye_col=header.index(u'深圳融资额(亿)')
        
        szjz_col=header.index(u'上证净值')
        
        scjz_col=header.index(u'深成净值')
        
        cybjz_col=header.index(u'创业板净值')
        
        zxbjz_col=header.index(u'中小板净值')
        
        lrye_col=header.index(u'两融总额')
        
        date_col=header.index(u'截止日')
        
        wbk=xlsxwriter.Workbook(u'E:\\work\\报表\\融资余额\\rzye_index.xlsx')
        
        pic_sheet=wbk.add_worksheet('pic')
        
        data_sheet=wbk.add_worksheet('data')
        
        #写入画图数据
        data_sheet.write_row(0,0,df_rzye.columns)
        
        data_len=len(df_rzye)
        
        for i in xrange(data_len):
            
            data_sheet.write_row(i+1,0,df_rzye.iloc[i])
            
            
        #两融总额图
        lrye_chart=wbk.add_chart({'type':'line'})
        
        lrye_chart.add_series({
            'name':['data', 0, lrye_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,lrye_col, 1+data_len,lrye_col],
            })   
            
        lrye_chart.set_size({'width':1000,'height':400})
        
        
        #上海融资额图
        sh_chart=wbk.add_chart({'type':'line'})
        
        sh_chart.add_series({
            'name':['data', 0, shye_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,shye_col, 1+data_len,shye_col],
            })       
        
        sh_chart.add_series({
            'name':['data', 0, szjz_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,szjz_col, 1+data_len,szjz_col],
            'y2_axis': True,            
            })    
        
        sh_chart.set_size({'width':1000,'height':400})
        
        
        #深圳融资额与深成图
        sz_chart1=wbk.add_chart({'type':'line'})
        
        sz_chart1.add_series({
            'name':['data', 0, szye_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,szye_col, 1+data_len,szye_col],
            })       
        
        sz_chart1.add_series({
            'name':['data', 0, scjz_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,scjz_col, 1+data_len,scjz_col],
            'y2_axis': True,            
            })  
            
        sz_chart1.set_size({'width':1000,'height':400})
        
        #深圳融资额与中小、创业板
        sz_chart2=wbk.add_chart({'type':'line'})
        
        sz_chart2.add_series({
            'name':['data', 0, szye_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,szye_col, 1+data_len,szye_col],
            })       
        
        sz_chart2.add_series({
            'name':['data', 0, zxbjz_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,zxbjz_col, 1+data_len,zxbjz_col],
            'y2_axis': True,            
            })  
            
        sz_chart2.add_series({
            'name':['data', 0, cybjz_col],
            'categories':['data', 1, date_col, 1+data_len,date_col],
            'values':['data', 1,cybjz_col, 1+data_len,cybjz_col],
            'y2_axis': True,            
            })  
        
        sz_chart2.set_size({'width':1000,'height':400})
        
        #插入图片
        pic_sheet.insert_chart(0,0,lrye_chart)
            
        pic_sheet.insert_chart(20,0,sh_chart)
        
        pic_sheet.insert_chart(40,0,sz_chart1)
        
        pic_sheet.insert_chart(60,0,sz_chart2)
        
        wbk.close()

if __name__ == '__main__':
    
    r=Rzye()
    
    r.get_rzye()
    
    r.plot_rzye()