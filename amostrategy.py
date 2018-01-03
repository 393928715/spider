# -*- coding: utf-8 -*-
"""
Created on Fri Sep 01 13:53:36 2017

@author: Administrator
"""
import sys
reload(sys)      
sys.setdefaultencoding('utf-8')

import pandas as pd 

from sqlalchemy import create_engine 

import xlsxwriter

class amoStrategy:
    
    def __init__(self,sdate,edate,window):
        
        #不属于56个行业的板块数据文件
        self.stocBoardFile=u'E:\\work\\标的\\stock_info.txt'
        
        self.powerIndexDir=u'E:/work/报表/量能选股/'
        
        self.index56=u'E:/work/标的/index56.txt'
        
        self.index110=u'E:/work/标的/index110.txt'
        
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
        self.sdate=sdate
        
        self.edate=edate
        
        #定义要筛选几天的票，给出对应天数的股票dataframe
        self.window=window


    #获取股票关联板块
    def getStockRelated(self,df_stock,stockrelated):
           
        stockrelated['cFlag']=stockrelated['board_name'].str.contains(u'通达信行业-')
        
        stockrelated=stockrelated[stockrelated['cFlag']]
        
        stockrelated['board_name']=stockrelated['board_name'].apply(lambda x:x.replace(u'通达信行业-',''))     
        
        df_stock.index=df_stock.hq_code
        
        stockrelated.index=stockrelated.stock_id
        
        stockrelated['board_name']
        
        return  stockrelated['board_name']
        
        
        
    #获取指数代码对应名称
    def getIndexNames(self,df_index,indexNames):
        
        if 'hq_code' in df_index:
            df_index.set_index('hq_code',inplace=True)
            
        df_index['hq_name']=indexNames['board_name']
        
        df_index['hq_name']=df_index['hq_name'].apply(lambda x:x.replace(u'通达信行业-','').replace(u'通达信细分行业-',''))  
        
        df_index.index=range(len(df_index))
        
        return df_index['hq_name']
    
    
    #获取股票代码对应名称
    def getStockNames(self,df_stock,stockNames):
        
        if 'hq_code' in df_stock.columns:     
            df_stock.index=df_stock['hq_code']
            
        df_stock['hq_name']=stockNames['hq_name']
        
        return df_stock['hq_name']  
        
     
    #板块日线成交额效能计算,时间窗口为20天
    def amoPower(self,df,marketAmoSeries,threshold):
        
       dataLen=len(marketAmoSeries)
      
       df.index=xrange(dataLen)
       
       df['amo_ratio']=df['hq_amo']/marketAmoSeries
       
       usepower=0
       
       highpower=[]
       
       amoRatioSum=[]
       
       for i in range(dataLen-self.window,dataLen):
           
           amoRatioMean=df[i-20:i]['amo_ratio'].mean()
           amoRatioStd=df[i-20:i]['amo_ratio'].std()
           
           if amoRatioStd != 0:
               amo_power=df.loc[i,'amo_power']=(df.iloc[i]['amo_ratio']-amoRatioMean)/amoRatioStd
               
           else:
               amo_power=None
           
           if amo_power>=threshold:
               usepower+=1
               highpower.append(amo_power)
               amoRatioSum.append(df.iloc[i]['amo_ratio'])
            
       highpower=pd.Series(highpower)
       amoRatioSum=pd.Series(amoRatioSum)
       
       df['usecount']=usepower
       df['usepower_avg']=highpower.mean()
       df['amoratio_avg']=amoRatioSum.mean()

       return df

    #得到标的数据,要穿一个hq_code列
    def getRF(self,name,df_stock):
                   
        if name==30:      
            codelist=self.getCode(u'E:\\work\\标的\\30.txt')
        else:
            codelist=self.getCode(u'E:\\work\\标的\\200.txt')
                   
        if 'hq_code' in df_stock.columns:        
            df_stock['cFlag']=df_stock['hq_code'].isin(codelist)        
            df_stock200=df_stock[df_stock['cFlag']]  
        else:
            df_stock['cFlag']=df_stock.index.isin(codelist)        
            df_stock200=df_stock[df_stock['cFlag']]             
            
        del df_stock200['cFlag'],df_stock['cFlag']   
        
        return df_stock200 
        
    #得到标的代码
    def getCode(self,fname):
        try:
            s1=pd.read_table(fname,usecols=[0],dtype=str,encoding='utf-8')
        except:
            s1=pd.read_table(fname,usecols=[0],dtype=str,encoding='gbk')
        
        s1.columns=['code']
        
        try:
            codelist=s1['code'].astype('int')
        except:
            codelist=s1['code']
            codelist.drop(codelist[codelist==u'数据来源:通达信'].index,inplace=True)
            codelist=codelist.astype('int')
        
        return codelist 
        
    def plotPowerIndexs(self,index_high_amo,enddate):
        
        #获取头以及对应列
        header=list(index_high_amo.columns)
        
        datecol=header.index('hq_date')
        
        powercol=header.index('amo_power')
        
        namecol=header.index('hq_code')
        
        ratiocol=header.index('amo_ratio')
        
        #数据之间的间隔
        interval=len(header)+1
        
        wbk =xlsxwriter.Workbook(self.powerIndexDir+enddate+' powerindex.xlsx') 
        
        picSheet=wbk.add_worksheet('pic')
        
        dataSheet=wbk.add_worksheet('data')
        
        codelist=index_high_amo['hq_code'].drop_duplicates()
        
        left=0
        
        for code in codelist: 
            
            top=0
            
            amoratio_test=index_high_amo[index_high_amo.hq_code==code]
            
            dataLen=len(amoratio_test)
            
            dataSheet.write_row(0,left,header)
            
            for i in xrange(dataLen):
                
                dataSheet.write_row(1+top,left,amoratio_test.iloc[i])
                
                top+=1
            
            left+=interval
            
        #画图
        data_top=1
        
        width=800
        
        height=400
        
        for loopindex in xrange(len(codelist)): 
                
            bk_chart=wbk.add_chart({'type': 'line'})
            
            bk_chart.set_style(4)
               
               #向图表添加数据 
            bk_chart.add_series({
                'name':['data', 1, namecol+loopindex*interval],
                'categories':['data', data_top, datecol+loopindex*interval, data_top+dataLen, datecol+loopindex*interval],
                'values':['data', data_top, powercol+loopindex*interval, data_top++dataLen,powercol+loopindex*interval],
                'line':{'color':'#336699'},
                })
            
        
        #   bk_chart.set_title({'name':self.sdate+'-'+self.edate,
        #                       'name_font': {'size': 10, 'bold': True}
        #                       })
                                   
            bk_chart.set_x_axis({#'name':u'日期',
                                    #'name_font': {'size': 10, 'bold': True},
                                    'label_position': 'low',
                                    'interval_unit': 2                          
                                    })
        
            bk_chart.set_size({'width':width,'height':height})     
            
            
            picSheet.insert_chart(0+loopindex*(height/20),0,bk_chart)
        
        wbk.close()    
  
    def plotPowerStocks(self,wbk,date,powerindexs,day_powerstock,day_stock):
        
        PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})
        
        powerSheet=wbk.add_worksheet(str(date))
  
        powerSheet.write_row(0,0,[u'板块排名',u'效能'])
      
        for i in xrange(len(powerindexs)):
            powerSheet.write_row(i+1,0,powerindexs.iloc[i])
        
        for i in xrange(len(day_stock)):
            if i == 0:
                powerSheet.write_row(0,3,[u'名称',u'板块',u'占比'])                  
            powerSheet.write_row(i+1,3,day_stock.iloc[i],PER)
        
        top=0
        for powerindex in powerindexs['hq_name']:
            
            tmp_powerstock=day_powerstock[day_powerstock.board_name==powerindex]
            
            powerSheet.write_row(top,7,[u'名称',u'板块',u'占比'])
            
            datalen=len(tmp_powerstock)
            
            for i in xrange(datalen):
                
                powerSheet.write_row(top+1+i,7,tmp_powerstock.iloc[i],PER)
            
            top+=datalen+2
               
        return wbk
                
    
    def powerStocks(self,threshold,RF=False,index_num=56):
        
        if index_num==56:
            #得到所需板块数据
            index56=self.getCode(self.index56)
        else:
            index56=self.getCode(self.index110)
            
#            indexNames=pd.read_table(self.index110,encoding='gbk',usecols=[0,1],index_col=0).dropna()
#            
#            indexNames.columns=['hq_name']
            
            board_name=pd.read_table(self.stocBoardFile,usecols=[0,18],header=0,names=['hq_code','board_name'],encoding='gbk').dropna()
            
            board_name['hq_code']= board_name['hq_code'].astype(int)
            
            board_name.set_index('hq_code',inplace=True)
            
            board_name=board_name['board_name']
            
            
        #所有板块数据
        sql='select hq_code,hq_date,hq_amo from hindexquotationday where ((hq_code = 2 or hq_code = 399107) or (hq_code <=880497 and hq_code >= 880301)) and hq_date >="'+self.sdate+'" and hq_date <="'+self.edate+'"'
        df_index=pd.read_sql(sql,con=self.engine)
        df_index['hq_date']=df_index['hq_date'].astype(str)
        print sql
        
        #获得所有日期
        dates=df_index['hq_date'].drop_duplicates()[-self.window:]
      
        #得到所有日线级别的全市场成交额
        df_000002=df_index[df_index.hq_code==2]
        df_399107=df_index[df_index.hq_code==399107]
        marketAmoSeries=(df_000002.reset_index())['hq_amo']+(df_399107.reset_index())['hq_amo']
        
        #筛选掉不需要的板块数据
        df_index=df_index[df_index['hq_code'].isin(index56)]
      
        #计算强板块
        index_high_amo=df_index.groupby('hq_code').apply(lambda x: self.amoPower(x,marketAmoSeries,threshold))
        index_high_amo.reset_index(level=1,inplace=True,drop=True)
        index_high_amo.index=index_high_amo.hq_code
        
        index_high_amo=index_high_amo.sort_values(['usecount','usepower_avg'],ascending=False)
        
        #关联强板块名称
        indexNames=pd.read_sql_table('boardindexbaseinfo',con=self.engine,schema='stocksystem',index_col='board_code',columns=['board_code','board_name'])  
        index_high_amo['hq_name']=self.getIndexNames(index_high_amo,indexNames)  

        #关联板块数据
        stockrelated=pd.read_sql_table('boardstock_related',con=self.engine,columns=['board_name','stock_id'],schema='stocksystem')
        
        #取出该时间段股票数据，并关联板块
        stocksql='select hq_code,hq_date,hq_amo from hstockquotationday where hq_date >="'+self.sdate+'" and hq_date <="'+self.edate+'"'        
        df_stock=pd.read_sql(stocksql,con=self.engine)    
        df_stock['hq_date']=df_stock['hq_date'].astype(str)
        print stocksql
        
        #根据日期获得文件名
        if RF == True:
            df_stock=self.getRF(200,df_stock)
            fname=self.powerIndexDir+str(dates.iat[-self.window])+'-'+str(dates.iat[-1])+' RF_high_amo.xlsx'
        
        else:
            if index_num==56:
                fname=self.powerIndexDir+str(dates.iat[-self.window])+'-'+str(dates.iat[-1])+'high_amo.xlsx' 
            else:
                fname=self.powerIndexDir+str(dates.iat[-self.window])+'-'+str(dates.iat[-1])+'high_amo_110.xlsx' 
        
        #补齐股票数据
        df_000002.set_index('hq_date',inplace=True)
        df_stock.set_index('hq_date',inplace=True)
        tradingDays=len(df_000002)
        
        stockGroup=df_stock.groupby('hq_code')
        df_stock=pd.DataFrame()
        
        for code,tmp_stock in stockGroup:
            
            if len(tmp_stock) != tradingDays:
                
                tmp_stock=tmp_stock.reindex(df_000002.index)
                
                tmp_stock.fillna(method='ffill',inplace=True)
                
                tmp_stock.fillna(method='bfill',inplace=True)             
            
            df_stock=df_stock.append(tmp_stock)
            
        df_stock.reset_index(inplace=True)
        
        if index_num==56:
            df_stock['board_name']=self.getStockRelated(df_stock,stockrelated)
        else:
            df_stock.index=df_stock.hq_code
            df_stock['board_name']=board_name
    
        #获得股票名称
        stockNames=pd.read_table(self.stocBoardFile,usecols=[0,1],header=0,names=['hq_code','hq_name'],encoding='gbk').dropna()
        
        stockNames['hq_code']=stockNames['hq_code'].astype(int)
        
        stockNames.set_index('hq_code',inplace=True)        
        
        df_stock['hq_name']=self.getStockNames(df_stock,stockNames)
        
        #计算异动    
        df_stock.reset_index(inplace=True,drop=True)
        sotck_high_amo=df_stock.groupby('hq_code').apply(lambda x: self.amoPower(x,marketAmoSeries,threshold))
        
        #得到股票占比
        stock_amoratio=sotck_high_amo.loc[:,['hq_name','amo_ratio','hq_date','board_name']]
        stock_amoratio.reset_index(inplace=True,drop=True)
        
        #取出强票数据
        sotck_high_amo=sotck_high_amo[sotck_high_amo.amo_power>=threshold]
        
        #得到强票每天的成交占比
        stock_amoratio=stock_amoratio[stock_amoratio['hq_name'].isin(sotck_high_amo.hq_name)]
        
        #得到宏观分析，剔除多于数据
        sotck_high_amo['hq_name']=sotck_high_amo['hq_name'].drop_duplicates()
        sotck_high_amo.dropna(inplace=True)
        
        stock_avg_amoratio=sotck_high_amo.loc[:,['hq_name','board_name','amoratio_avg']].sort_values('amoratio_avg',ascending=False)
        sotck_high_amo=sotck_high_amo.loc[:,['hq_name','board_name','usecount','usepower_avg']].sort_values(['usecount','usepower_avg'],ascending=False)[:300]
        
        #建立EXCEL
        wbk=xlsxwriter.Workbook(fname)
        
        PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})
        
        zqSheet=wbk.add_worksheet(u'周期统计')
        
        index_high_amo=index_high_amo[index_high_amo.usecount>=1]      
        index_stats=index_high_amo.loc[:,['hq_name','usecount','usepower_avg','amoratio_avg']]
        index_stats['hq_name']=index_stats['hq_name'].drop_duplicates()
        index_stats.dropna(inplace=True)
        index_high_amo=index_high_amo.loc[:,['hq_name','amo_ratio','hq_date']]
        
        #写周期数据
          #板块周期数据
        indexHead=[u'板块',u'异动次数',u'异动均值',u'占比均值']
        indexWidth=len(indexHead)
        zqSheet.write_row(0,0,indexHead)
        for i in xrange(len(index_stats)):
            zqSheet.write_row(i+1,0,index_stats.iloc[i])
            zqSheet.write(i+1,3,index_stats.iloc[i]['amoratio_avg'],PER)
        
        stockAmoHead=[u'股票',u'板块',u'异动次数',u'异动均值']
        zqSheet.write_row(0,0+indexWidth+1,stockAmoHead)    
        for i in xrange(len(sotck_high_amo)):
            zqSheet.write_row(i+1,0+indexWidth+1,sotck_high_amo.iloc[i])
            
        stockRatioHead=[u'股票',u'板块',u'占比均值']
        stockRatioWidth=len(stockRatioHead)
        zqSheet.write_row(0,2*(indexWidth+1),stockRatioHead)    
        for i in xrange(len(stock_avg_amoratio)):
            zqSheet.write_row(i+1,2*(indexWidth+1),stock_avg_amoratio.iloc[i])
            zqSheet.write(i+1,2*(indexWidth+1)+2,stock_avg_amoratio.iloc[i]['amoratio_avg'],PER)
          
        top=0
        for index in index_stats['hq_name']:
            
            #写股票分板块统计
            df_stock=sotck_high_amo[sotck_high_amo.board_name==index]
            tmpLen=len(df_stock)
            zqSheet.write_row(top,2*(indexWidth+1)+stockRatioWidth+1,stockAmoHead)
            
            for i in xrange(tmpLen):
                zqSheet.write_row(top+1+i,2*(indexWidth+1)+stockRatioWidth+1,df_stock.iloc[i])
            
            top+=tmpLen+2
            
        #写入板块作图数据与股票作图数据       
        index_data_sheet=wbk.add_worksheet('indexdata')
        
        index_data_sheet.hide()
        
        index_head=list(index_high_amo.columns)
        
        index_name_col=index_head.index('hq_name')
        
        index_ratio_col=index_head.index('amo_ratio')
        
        index_date_col=index_head.index('hq_date')
        
        index_pic_top=0
        
        index_interval=len(index_head)+1
        
        index_col=0
        
        stock_head=list(stock_amoratio.columns)
        
        stock_name_col=index_head.index('hq_name')
        
        stock_ratio_col=index_head.index('amo_ratio')
        
        stock_date_col=index_head.index('hq_date')  
        
        stock_interval=len(stock_head)+1

        for index in index_stats['hq_name']:        
            
            #板块数据
            df_index=index_high_amo[index_high_amo.hq_name==index]
            
            index_data_sheet.write_row(0,index_col,index_head)  
            
            index_len=len(df_index)
            
            for i in xrange(index_len):
                
                index_data_sheet.write_row(i+1,index_col,df_index.iloc[i],PER)
                
            
            #做板块量比图
            index_chart=wbk.add_chart({'type':'line'})
            
            index_chart.add_series({
             'name':['indexdata', 1, index_col+index_name_col],
             'categories':['indexdata', 1, index_col+index_date_col, 1+index_len, index_col+index_date_col],
             'values':['indexdata', 1, index_col+index_ratio_col, 1+index_len,index_col+index_ratio_col],
             #'line':{'color':color},#FF6666
            })      
            
            
            index_chart.set_size({'width':1000,'height':400})  
            
            zqSheet.insert_chart(index_pic_top,20,index_chart)
            
            index_col+=index_interval
            
            index_pic_top+=20
            
            #股票数据
            stock_data_sheet=wbk.add_worksheet(index+'data')
            
            stock_data_sheet.hide()
            
            stock_pic_sheet=wbk.add_worksheet(index)
            
            df_stock=stock_amoratio[stock_amoratio.board_name==index]
            
            stock_group=df_stock.groupby('hq_name')
            
            stock_col=0
            
            stock_pic_top=0
            
            for name,df in stock_group:
                
                stock_data_sheet.write_row(0,stock_col,stock_head)
                
                stock_len=len(df)
            
                for i in xrange(stock_len):
                    
                    stock_data_sheet.write_row(i+1,stock_col,df.iloc[i],PER)
                                        
                #做股票量比图
                stock_chart=wbk.add_chart({'type':'line'})
                
                stock_chart.add_series({
                 'name':[index+'data', 1, stock_col+stock_name_col],
                 'categories':[index+'data', 1, stock_col+stock_date_col, 1+stock_len, stock_col+stock_date_col],
                 'values':[index+'data', 1, stock_col+stock_ratio_col, 1+stock_len,stock_col+stock_ratio_col],
                 #'line':{'color':color},#FF6666
                })      
                
                
                stock_chart.set_size({'width':1000,'height':400})  
                
                stock_pic_sheet.insert_chart(stock_pic_top,0,stock_chart)   

                stock_pic_top+=20                
                             
                stock_col+=stock_interval
                    
#        #写每日数据
#        for i in xrange(self.window):
#            
#            #提取每日数据
#            date=dates.iat[i]                
#    
#            day_indexpower=index_high_amo[index_high_amo.hq_date==date]
#            
#            day_stock=df_stock[df_stock.hq_date==date]                    
#            
#            day_indexpower['hq_date']=day_indexpower['hq_date'].astype(str)
#            
#            #按照异动次数，异动均值排序,获得异动板块排名
#            day_indexpower.sort_values('amo_power',inplace=True,ascending=False)
#                                                              
#            powerindexs=day_indexpower.iloc[:5][['hq_name','amo_power']]
#               
#            #获得每天的市场总成交额
#            dayMarketAmo=marketAmoSeries.iat[i-self.window]
#            
#            #获得股票的成交额占比,按照成交额占比排序
#            day_stock['amo_ratio']=day_stock['hq_amo']/dayMarketAmo
#            
#            day_stock.sort_values('amo_ratio',inplace=True,ascending=False)
#            
#            #按照板块的排序，取出关联股票进行排名
#            day_powerstock=pd.DataFrame()
#            for powerindex in powerindexs['hq_name']:
#                
#                tmp_stock=day_stock[day_stock.board_name==powerindex]
#                
#                stocknum=len(tmp_stock)
#                
#                usenum=stocknum/10
#                
#                if usenum<=5:
#
#                    usenum=5                
#                          
#                day_powerstock=day_powerstock.append(tmp_stock.iloc[:usenum])
#                
#                                 
#            day_powerstock=day_powerstock.loc[:,['hq_name','board_name','amo_ratio']]
#            
#            day_stock=day_stock.iloc[:len(day_stock)/10][['hq_name','board_name','amo_ratio']].dropna()
#                       
#            wbk=self.plotPowerStocks(wbk,date,powerindexs,day_powerstock,day_stock)
#            
#            print date
                                      
        wbk.close()
        
        return index_high_amo,sotck_high_amo
    
if __name__ == '__main__':
    
    a=amoStrategy(sdate='2017-08-01',edate='2017-12-11',window=7)
    
    index_high_amo,sotck_high_amo=a.powerStocks(threshold=3,RF=False,index_num=110)
