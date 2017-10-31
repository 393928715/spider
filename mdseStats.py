# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 16:12:09 2017

@author: Administrator
"""

import xlsxwriter

import pandas as pd

from sqlalchemy import create_engine


class mdseStats:
    
    def __init__(self,sdate,edate,window):
        
        self.mdsedir=u'E:\\工作\\报表\\商品统计\\'
        
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
        #获取上下游数据
        self.df_stream=pd.read_sql_table('stream',con=self.engine)
        
        self.sdate=sdate
        self.edate=edate

        self.window=window
    
    #计算累计涨幅
    def allChg(self,df):
        
        close0=df['close'].iat[0]
        allChg=df['close']/close0-1    
        df['allchg']=allChg        
        
        return df   
    
    def zqChg(self,df):
        
        df['zqchg']=df['allchg'].iat[-1]-df['allchg'].iat[0]
        
        return df
    
    
    def allChgAvg(self,df,dates):
        meanChgList=[]
        for day in dates:      
            df_tmp=df[df.hq_date==day]
            tmpachg=df_tmp['allchg'].mean()
            meanChgList.append(tmpachg)     
        
        return meanChgList
        
    def writeDates(self,dates,df_window,wbk,theFormat):
                
        for date in dates:
            
            df=df_window[df_window.date==date].sort_values('chg',ascending=False).drop(['allchg','close'],axis=1) 
                
            dateSheet=wbk.add_worksheet(date)
            
            dateSheet.write_row(0,0,[u'商品',u'产业',u'涨幅',u'日期'])
            
            for i in xrange(len(df)):
              
                dateSheet.write_row(i+1,0,df.iloc[i],theFormat)
                
    
        return wbk    
    
    def writePeriod(self,df_window,zqSheet,theFormat):
        
        dataWidth=len(df_window.columns)
        
        zqSheet.write_row(0,0,[u'商品',u'产业',u'周期涨幅'])
         
        for i in xrange(len(df_window)):
            zqSheet.write_row(i+1,0,df_window.iloc[i])
            zqSheet.write(i+1,dataWidth-1,df_window.iloc[i]['zqchg'],theFormat)
        
        zqSheet.set_column(0,dataWidth,10)
            
        return zqSheet
        
        
    #得到关联上下游股票名称的series
    def relatedStock(self,merchandise,streamdata):
        #streamdata=pd.read_sql('select * from industryday where date >=  "'+sdate+'" and date <= "'+edate+'"')
        relatedup=streamdata[streamdata.name==merchandise]['up']
        
        relateddown=streamdata[streamdata.name==merchandise]['down']
            
        return relatedup,relateddown
        
        
        
    def plotChart(self,dataSheet,zqSheet,wbk,df_board,sortMdses,width=800,height=400):
    
        left=0
        loop=0
    
        boardhead=list(df_board.columns)
        interval=len(boardhead)+1
        allChgCol=boardhead.index('allchg')
        dateCol=boardhead.index('date')
        nameCol=boardhead.index('name')
        
        for name in sortMdses:
            
            top=loop*height/20+1
            
            df=df_board[df_board.name==name]
            
            dataSheet.write_row(0,left,df)
            for i in xrange(len(df)):
                
                dataSheet.write_row(i+1,left,df.iloc[i])
            
            chart=wbk.add_chart({'type': 'line'})
            
            chart.add_series({
             'name':['data', 1, nameCol+loop*interval],
             'categories':['data', 1, dateCol+loop*interval, 1+len(df), dateCol+loop*interval],
             'values':['data', 1, allChgCol+loop*interval, 1+len(df), allChgCol+loop*interval],
             'line':{'color':'336699'},            
             })
             
            chart.set_size({'width':width,'height':height})
             
            zqSheet.insert_chart(top,interval,chart)
            
            #得到商品上下游
            up,down=self.relatedStock(name,self.df_stream)
            
            #上下游股票写在图片右边
            zqSheet.write(top,interval+width/66+1,name+u'上游:')
            zqSheet.write_row(top,interval+width/66+2,up)
            
            zqSheet.write(top+2,interval+width/66+1,name+u'下游:')
            zqSheet.write_row(top+2,interval+width/66+2,down) 
            
            
            left+=interval
            
            loop+=1
            
        return dataSheet,zqSheet 


    def createFrom(self):
        
        #得到商品数据
        mdsesql='select name,board,close,chg,date from boardday where date >="'+self.sdate+'" and date <="'+self.edate+'"'        
        df_mdse=pd.read_sql(mdsesql,con=self.engine).sort_values('date')    
        print mdsesql
        df_mdse['date']=df_mdse['date'].astype(str)
        df_mdse['chg']=df_mdse['chg']/100
        
        #计算累计涨幅
        df_mdse=df_mdse.groupby('name').apply(self.allChg)

        #得到需要统计的日期
        dates=df_mdse['date'].drop_duplicates().iloc[-7:]
        period=dates.iat[0]+'--'+dates.iat[-1]
        
     
        #得到不同板块的数据
    
        mdseGroup=df_mdse.groupby('board')
        
        for name,df_board in mdseGroup:
            
            wbk=xlsxwriter.Workbook(mdsedir+period+name+'combAvg.xlsx')
            
            PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})
            
            zqSheet=wbk.add_worksheet(period)
                   
            #得到窗口期的数据
            df_window=df_board[df_board['date'].isin(dates)]
            
            #按日对涨幅排序，写入EXCEL
            wbk=m.writeDates(dates,df_window,wbk,PER)
            
            #计算周期数据的周期涨幅,并排序
            df_window=df_window.groupby('name').apply(self.zqChg)
            df_window.sort_values('zqchg',ascending=False,inplace=True)
            df_window['name']=df_window['name'].drop_duplicates()
            df_window.dropna(inplace=True)
            
            #得到按周期涨幅排序的板块
            sortMdses=df_window['name']
            df_window.drop(['chg','date','allchg','close'],axis=1,inplace=True)
                   
            #写入周期统计数据
            zqSheet=self.writePeriod(df_window,zqSheet,PER)
                
            #计算不同商品的累计涨幅
            dataSheet=wbk.add_worksheet('data')
            
            #把数据写入，并画图
            dataSheet,zqSheet=self.plotChart(dataSheet,zqSheet,wbk,df_board,sortMdses,width=800,height=400)
            
            wbk.close()
            
            print name        


if __name__ == '__main__':
    
    m=mdseStats(sdate='2017-07-07',edate='2017-09-15',window=7)

    stocBoardFile=u'E:\\工作\\股票数据\\股票细分板块\\allboard.txt'
    mdsedir=u'E:\\工作\\报表\\商品统计\\'
    
    sdate='2017-07-07'
    edate='2017-09-13'
    window=7
    
    engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
    

          
    m.createFrom()
    