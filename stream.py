# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:24:14 2017

@author: Administrator
"""

import pandas as pd 
from sqlalchemy import create_engine
from pyquery import PyQuery as pq
import xlsxwriter
import numpy as np
import glob

class stream:
    def __init__(self):
        
        self.csvdir=u'E:\\work\\股票数据\\上下游\\'
        
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
    def download(self):

        doc=pq('http://stock.100ppi.com/ssgs.html')
        
        mainhtml=doc.html()
        
        #获得大板块名称列表
        index=doc('div[class="catetitle"]').text().split()
        
        indexnum=len(index)
        
        for i in xrange(indexnum):
            
            if i==7:
                usehtml=mainhtml[mainhtml.find('<div class="catetitle">'+index[i]):]
            else:       
                usehtml=mainhtml[mainhtml.find('<div class="catetitle">'+index[i]):mainhtml.find('<div class="catetitle">'+index[i+1])]
            
            usedoc=pq(usehtml)
            
            #获得二级分类名称
            secondindex=usedoc('li[class="cbc1 w74 fl"]').text().split()
            
            secondindexnum=len(secondindex)
            
            wbk =xlsxwriter.Workbook(self.csvdir+index[i]+'.xlsx') 
            
     
            for j in xrange(secondindexnum):
                
                n=2*j
                
                #获得上游股票
                upstocks=pd.Series(usedoc('li[class="cbc3 fl"]').eq(n).text().split())
                
                #获得下游股票
                downstocks=pd.Series(usedoc('li[class="cbc3 fl"]').eq(n+1).text().split())
                
                df=pd.DataFrame({'up':upstocks,'down':downstocks})
                
                df['index1']=index[i]
                
                df['index2']=secondindex[j]  
                
                wsheet= wbk.add_worksheet(secondindex[j])
                
                wsheet.write_row(0,0,[u'大类',u'小类',u'上游',u'下游'])
                
                for k in xrange(len(df)):
                    wsheet.write_row(k+1,0,df.loc[k,['index1','index2']])
                    try:
                        wsheet.write(k+1,2,df.loc[k,'up'])
                    except:
                        pass                
                    try:
                        wsheet.write(k+1,3,df.loc[k,'down'])
                    except:
                        pass
                    
            wbk.close()
            
            print self.csvdir+index[i]+'.xlsx'
            
        self.toSql()
        
    def toSql(self):
        flist=glob.glob(self.csvdir+'*.xlsx')
        for f in flist:
            s1=pd.read_excel(f,None)
            for key  in s1:  
                s1[key].columns=['industry','name','up','down']
                s1[key].to_sql('stream',con=self.engine,if_exists='append',index=None)    
            
            print f+u' 入库'
     
if __name__ == '__main__':
    s=stream()
    s.toSql()

       
