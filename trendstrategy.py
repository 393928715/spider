# -*- coding: utf-8 -*-
"""
Created on Thu Sep 07 11:01:32 2017

@author: Administrator
"""

import tushare as ts

import pandas as pd

import xlsxwriter

from sqlalchemy import create_engine

import numpy as np

class trend:
    
    def __init__(self,sdate,edate):
        
        self.sdate=sdate
        
        self.edate=edate
        
        self.indexlist=['399317','000001','399107','399101','399102','000016','399300','399905','399678']#
        
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
        self.trenddir=u'E:\\work\\报表\\趋势\\'
        
        self.indexWeekDir=u'E:\\work\\股票数据\\板块周线\\'
        
        self.table=[]
        
        self.data=[]
      
      
    def prediction(self,code,DB):
        
        if  DB == True:#code == '399678' or
            
            names=['date','open','high','low','close','vol']
            
            df=pd.read_table(self.indexWeekDir+code+'.txt',header=1,usecols=[0,1,2,3,4,5],names=names,dtype={'date':str,'close':float,'vol':float,'open':float,'high':float,'low':float},encoding='gbk').dropna()
                    
            df['date']=df['date'].apply(lambda x:x.replace('/','-').strip())
            
            df=df[(df.date>=self.sdate)&(df.date<=self.edate)]
            
        else:
            df=ts.get_k_data(code,ktype='W',index=True,start=self.sdate,end=self.edate)
            
        moreFlag=(self.indexlist.index(code))*3+2
        
        lessFlag=(self.indexlist.index(code))*3
        
        for i in range(1,len(df)+1):
            
            #找到前四周的最高价和最低价
            maxhigh=df[-i-4:-i]['high'].max()
            
            minlow=df[-i-4:-i]['low'].min()
            
#            low=df.iloc[-i]['low']
#            
#            high=df.iloc[-i]['high']
            
            close=df.iloc[-i]['close']
                   
            trend=None
            
            if close>maxhigh:
                
                trend=moreFlag
                
            elif close<minlow:
                
                trend=lessFlag
    
            df.loc[df.index[-i],'trend']=trend

     
        #若未打破趋势，延续之趋势
        df=df.fillna(method = 'ffill')
        df.fillna(method = 'bfill',inplace=True)
        
        #得到板块名称
        name=self.judgeName(code)
        df['name']=name
        
        #计算板块趋势统计内容
        lastTrend=df.iloc[-1]['trend']
        lastClose=df.iloc[-1]['close']
        lastMinLow=df[-5:-1]['low'].min()
        lastMaxHigh=df[-5:-1]['high'].max()
        
        if lastTrend == moreFlag:
            criticalValue=lastMinLow
            
        else:
            criticalValue=lastMaxHigh    

        #trendDays=1
        
        for trendDays in range(1,len(df)):
            
            if lastTrend==lessFlag:
                
                if df.iloc[-trendDays-1]['trend'] == moreFlag:
                    trendDays-=1
                    break
                
            elif lastTrend==moreFlag:
                
                if df.iloc[-trendDays-1]['trend'] == lessFlag:
                    trendDays-=1
                    break
                
            #date=df.iloc[-trendDays-1]['date']
                
            
           
        self.formContent(lastTrend,criticalValue,lastClose,code,trendDays)
        
        return df    


    def judgeName(self,code):
        
        code=filter(lambda x:x not in 'shz',code)
        
        if code == '000001':
            name = u'上证指数'
            
        elif code == '399102':
            name = u'创业板综'
        
        elif code == '000016':
            name = u'上证50'
            
        elif code == '399300':
            name = u'沪深300'
            
        elif code == '399905':
            name = u'中证500'
            
        elif code == '399317':
            name = u'国证A指'
            
        elif code == '399678':
            name = u'次新股'
            
        elif code == '399107':
            name = u'深证A指'   
            
        elif code == '399101':
            name = u'中小板综'  
            
        return name

       
    def formContent(self,trend,criticalValue,close,code,trendDays):
        
        name=self.judgeName(code)        

        criticalRatio=criticalValue/close-1
        
        if trend == (self.indexlist.index(code))*3+2:
            judgement=u'多'       
        else:
            judgement=u'空'
        
        self.table.append([name,judgement,close,criticalValue,criticalRatio,trendDays])
        
    
    def trendChart(self):
        pass
        
    
    def buildTrendFrom(self,DB):
        
        wbk=xlsxwriter.Workbook(self.trenddir+self.sdate+'-'+self.edate+' trendTable.xlsx') 
        
        #添加格式
        PER=wbk.add_format({'font_name':'Arial','align':'center','valign':'vcenter','font_size':9,'num_format':'0.0%','font_color':'#003366'})
        title=wbk.add_format({'font_name':u'微软雅黑','align':'center','valign':'vcenter','font_size':9})
        red=wbk.add_format({'font_name':'Arial','align':'center','valign':'vcenter','font_size':9,'font_color':'red','num_format':'0.0%'})
        green=wbk.add_format({'font_name':'Arial','align':'center','valign':'vcenter','font_size':9,'font_color':'green','num_format':'0.0%'})
        zw_red=wbk.add_format({'align':'center','valign':'vcenter','font_size':9,'font_color':'red','num_format':'0.0%'})
        zw_green=wbk.add_format({'align':'center','valign':'vcenter','font_size':9,'font_color':'green','num_format':'0.0%'})        
        zwfloat=wbk.add_format({'font_name':'Arial','align':'center','valign':'vcenter','font_size':9,'num_format':'0','font_color':'#003366'})
        blue = wbk.add_format({'font_name':'黑体','align':'center','bg_color':'#728EAA','font_size':9,'font_color':'white'})
        zw=wbk.add_format({'align':'center','valign':'vcenter','font_size':9,'font_color':'#003366'})
        #建立sheet
        trendSheet=wbk.add_worksheet(u'趋势统计')
        dataSheet=wbk.add_worksheet('data')        

        
        #定义数据起始位置
        
        left=0
        loopindex=0
        
        #初始化图表
        trendChart=wbk.add_chart({'type': 'line'}) 
        
        for i in xrange(len(self.indexlist)):  
            
            code=self.indexlist[i]

            df_index=self.prediction(code,DB).loc[:,[u'name','date','trend','close']]
            
            if i ==0:
                dataLen=len(df_index)
                dfhead=list(df_index.columns)
                namecol=dfhead.index('name')           
                datecol=dfhead.index('date')           
                trendcol=dfhead.index('trend')     
                interval=len(dfhead)+1
                  
            dataSheet.write_row(0,left,df_index)
            
            for j in range(1,len(df_index)+1):
                
                dataSheet.write_row(j,left,df_index.iloc[j-1])
               
           #向图表添加数据 

            trendChart.add_series({
                'name':['data', 1, namecol+loopindex*interval],
                'categories':['data', 1, datecol+loopindex*interval, 0+dataLen, datecol+loopindex*interval],
                'values':['data', 1, trendcol+loopindex*interval, 0+dataLen,trendcol+loopindex*interval],
                #'line':{'color':'#336699'},
                #'line':   {'dash_type': 'dash_dot'}
                #'marker': {'type': 'circle','fill':{'color': 'red'}}
                })                
                
#            trendChart.set_title({'name':self.judgeName(code),
#                                   'name_font': {'size': 10, 'bold': True}
#                                   })

            left+=interval
            
            loopindex+=1
            
            print code      
            
        trendChart.set_title({'none': True})

        trendChart.set_x_axis({#'name':,
                            'name_font': {'size': 10, 'bold': True},
                            #'label_position': 'low',
                            'interval_unit': 5 ,        
                            })
                            
        trendChart.set_y_axis({'name':'',
                           'name_font': {'size': 12, 'bold': True},
                            'major_gridlines':False,
                            #'minor_gridlines':False,
                           'visible':False
                           })
       
        trendChart.set_size({'width':1200,'height':600}) 
           
        trendSheet.insert_chart(10,0,trendChart)     
   
        print 'creating the from...'
        
        header=[u'板块',u'趋势',u'收盘值',u'临界值',u'临界比',u'持续周数']
        
        table=pd.DataFrame(self.table,columns=header)
        
        table.sort_values(u'趋势',inplace=True)    
        
        #写板块趋势统计数据
            #时间
        trendSheet.merge_range(0,0,0,5,self.edate+u'趋势',title)
        
            #表头
        trendSheet.write_row(1,0,header,blue)
        
        for i in xrange(len(table)):
            
            trendSheet.write(i+2,0,table.iloc[i][u'板块'],zw)
            
            trendSheet.write_row(i+2,2,[table.iloc[i][u'收盘值'],table.iloc[i][u'临界值'],'',table.iloc[i][u'持续周数']],zwfloat)
              
            trend=table.iloc[i][u'趋势']  
            
            if trend == u'多':
                trendSheet.write(i+2,1,trend,zw_red)
                
            else:
                trendSheet.write(i+2,1,trend,zw_green)
                
            criticalRatio=table.iloc[i][u'临界比']
                        
            if criticalRatio>0:
                theFormat=green
            
            elif criticalRatio<0:
                theFormat=red
                
            else:
                theFormat=PER
                
            criticalRatio=abs(criticalRatio)
                
            trendSheet.write(i+2,4,criticalRatio,theFormat)
       
        wbk.close()
            
            
if __name__ == '__main__':
    
    t=trend('2017-01-01','2017-12-12')
    
    t.buildTrendFrom(DB=False)