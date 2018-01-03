# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:06:40 2017

@author: Administrator
"""
import sys
reload(sys)      
sys.setdefaultencoding('utf-8')

import pandas as pd

from pyquery import PyQuery as pq

from sqlalchemy import create_engine 

import xlsxwriter

import datetime

from itertools import izip_longest

chunk_list = lambda a_list, n: izip_longest(*[iter(a_list)]*n) 

class Holder:
    
    def __init__(self):

        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
        self.stockNames=pd.read_table(u'E:\\work\\股票数据\\股票细分板块\\allboard.txt',usecols=[0,1],header=0,names=['code','name'],dtype=str)
        
        self.codes=self.stockNames['code']
        
        self.excel_dir=u'E:/work/报表/股东人数变化/shareholders.xlsx'
        
        self.today=str(datetime.datetime.now()).split()[0]
        
        self.shareholder_table='shareholder'
        
        self.quarters=['03-31','06-30','09-30','12-31']


    def getShareholder(self,shareholderDoc,code,stockName):
        
        shareholderText=shareholderDoc("table[id='tabh']")('td').text().split()
        
        shareholderText.pop(0)
        
        shareholderList=list(chunk_list(shareholderText, 5))
        
        df_shareholder = pd.DataFrame(shareholderList[1:],columns=['date','avehold','holder','chg','chgper'])
        
        df_shareholder['code']=code
        
        df_shareholder['name']=stockName
        
        df_shareholder=df_shareholder.replace('--',0)
        
        df_shareholder.to_sql('shareholder',con=self.engine,if_exists='append',index=None)  
    

    def getKeyHolder(self,keyHolderDoc,code,stockName):
        
        keyHolderDoc1=keyHolderDoc("table[id='tabh']").eq(0)
        
        keyHolderDoc1=keyHolderDoc1('td')
        
        keyHolderText1=[]
        
        for each in keyHolderDoc1:
            
            if each != keyHolderDoc1[0]:
            
                eachText=pq(each).text()
                
                keyHolderText1.append(eachText)
        
        #keyHolderText1=keyHolderDoc.text()
      
        #keyHolderText1=keyHolderText1[keyHolderText1.find('截止日期'):].split()
        
        keyHolderList1=list(chunk_list(keyHolderText1, 5))
        
        df_keyHolder=pd.DataFrame(keyHolderList1[1:],columns=['date','holder_name','hold','holdper','type']).dropna().replace('--',0)
        
        df_keyHolder['code']=code
        
        df_keyHolder['name']=stockName
        
        keyHolderDoc2=keyHolderDoc("table[id='tabh']").eq(1)
        
        keyHolderDoc2=keyHolderDoc2('td')
        
        keyHolderText2=[]
        
        for each in keyHolderDoc2:
            
            if each != keyHolderDoc2[0]:
            
                eachText=pq(each).text()
                
                keyHolderText2.append(eachText)
                
        keyHolderList2=list(chunk_list(keyHolderText2, 5))
        
        df_keyHolderFlow=pd.DataFrame(keyHolderList2[1:],columns=['date','holder_name','hold','holdper','type']).dropna().replace('--',0)
        
        df_keyHolderFlow['code']=code
        
        df_keyHolderFlow['name']=stockName    
        
        df_keyHolder.to_sql('keyholder',con=self.engine,if_exists='append',index=None)
        
        df_keyHolderFlow.to_sql('keyholderflow',con=self.engine,if_exists='append',index=None)    
        
        return df_keyHolder,df_keyHolderFlow
        
        
    def get_day_df(self,textdoc):
        
        shareholderList=[]
        
        for each in textdoc:
            
            text=pq(each).text().split()
            
            data_number=len(text)
            
            if data_number<6:
                
                miss_len=6-data_number
                
                for i in xrange(miss_len):
                    
                    text.insert(-1,None)
            
            shareholderList.append(text)
    
        #shareholderList=list(chunk_list(text, 6))
        
        df=pd.DataFrame(shareholderList[1:],columns=['rank','name','code','holder','chgper','date'])
        
        df.drop('rank',axis=1,inplace=True)
        
        df['chgper']=df['chgper'].str.replace('%','')
        
        return df       
        
        
    def get_page(self,page_url,main_url):
        
        page_url=page_url.replace('window.location.href=','').replace("'",'')
        
        end_day=page_url.split('&EndDay=')[-1]
        
        end_day=end_day[:end_day.find('&')]
        
        #超过今天数据肯定不全，放弃更新
        beyong=end_day > self.today
        
        #如果在季报里已经更新过了，就放弃更新
        in_quarters=end_day[5:] in self.quarters
        
        if beyong or in_quarters:
            
            page_url=None
        
        else:
            
            page_url=main_url+page_url
        
        return page_url       
        
        
    def get_day_shareholder(self):
        
        
             
        main_url='http://www.yidiancangwei.com/'
        
        main_doc=pq(main_url)
        
        page_doc=main_doc('div[class="Time "]')
        
        page_urls=[]
        
        for each in page_doc:
            
            page_url=pq(each).attr.onclick
            
            page_url=self.get_page(page_url,main_url)
            
            if page_url:
            
                page_urls.append(page_url)
            
                print page_url
        
        
        next_page_url=main_doc('div[class="Time atv"]').attr.onclick    
        
        page_url=self.get_page(next_page_url,main_url)
        
        if page_url:
        
            page_urls.append(page_url)
            
            print page_url
            
        for page_url in page_urls:
        
            page_doc=pq(page_url)
            
            while page_doc:
                
                textdoc=page_doc('tr')
                
                df=self.get_day_df(textdoc)
                
                df.to_sql(self.shareholder_table,con=self.engine,if_exists='append',index=None)
                
                next_page_url=page_doc('a[class="previous "]').attr.href
                
                page_doc=pq(next_page_url)
                
                print next_page_url
    
  
    def holderChg(self,df,last_year_4_quarter,last_quarter):
 
        df.loc[:,'holder_chg']=df['holder']/df['holder'].iat[0]    
        
        try:
            last_quarter_hold=df[df.date==last_quarter]['holder_chg'].iat[0]
            quarter_chgper=(df['holder_chg'].iat[-1]-last_quarter_hold)/last_quarter_hold
        except:
            quarter_chgper='miss'
        
        df['quarter_chgper']=quarter_chgper
        
        try:
            last_year_hold=df[df.date==last_year_4_quarter]['holder_chg'].iat[0]
            year_chgper=(df['holder_chg'].iat[-1]-last_year_hold)/last_year_hold
        except:
            year_chgper='miss'   
        
        df['year_chgper']=year_chgper
              
        return df
        
        
    def plotShareholder(self,sdate,edate):
        
        readsql='select code,name,holder,date,chgper from shareholder where date >= "'+sdate+'" and date <= "'+edate+'" order by date'
            
        df_shareholder=pd.read_sql(readsql,con=self.engine)
        
        #删掉未上市前的数据
        df_shareholder.drop(df_shareholder[df_shareholder.holder<1000].index,inplace=True)
        
        df_shareholder['date']=df_shareholder['date'].astype(str)
        
        df_shareholder['chgper']=df_shareholder['chgper']/100
        
        print readsql
        
        #得到去年4季度时间
        this_year=self.today.split('-')[0]
        
        last_year_4_quarter=str(int(this_year)-1)+'-'+self.quarters[3]
        
        #得到上个季度时间，若上个季度离今天太近，就取上上季度
        for i in xrange(len(self.quarters)):
            
            last_quarter=this_year+'-'+self.quarters[-i-1]
            
            if last_quarter < self.today:
                
                days_to_last_quarter=(datetime.datetime.now()-datetime.datetime.strptime(last_quarter,'%Y-%m-%d')).days
                
                if days_to_last_quarter < 45:
                    
                    continue
                
                break
        
        df_shareholder=df_shareholder.groupby('code').apply(lambda x :self.holderChg(x,last_year_4_quarter,last_quarter))
        
        df_shareholder.sort_values('quarter_chgper',inplace=True)
        
        df_shareholder.drop(['chgper'],axis=1,inplace=True)
        
        wbk=xlsxwriter.Workbook(self.excel_dir)
        
        PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})  
   
        codes=df_shareholder['code'].drop_duplicates().tolist()
        
        df_shareholder.sort_values('date',inplace=True)
        
        header=list(df_shareholder.columns)
        
        name_col,date_col,chg_col=header.index('name'),header.index('date'),header.index('holder_chg')
        
        pic_sheet=wbk.add_worksheet(u'股东户数')
        
        data_sheet=wbk.add_worksheet('data')        
                 
        top=0
        
        pic_top=0
        
        n=0
        
        pic_sheet.write_row(0,15,[u'排名',u'代码',u'股票',u'本季变动',u'本年变动'])
        
        df_shareholder.fillna(0,inplace=True)
        
        for code in codes:
            
            df_thecode=df_shareholder[df_shareholder.code==code]
            
            the_name=df_thecode['name'].iat[0]
            
            the_datalen=len(df_thecode)
            
            if the_datalen>=4:
            
                data_sheet.write_row(top,0,header)
                
                for i in xrange(len(df_thecode)):
                    
                    data_sheet.write_row(top+i+1,0,df_thecode.iloc[i])
                    
                pic_sheet.write(pic_top,0,code)
                
                pic_sheet.write(pic_top+1,0,the_name)

                pic_sheet.write_row(n+1,15,[str(n),code,the_name])
                
                pic_sheet.write_row(n+1,18,[df_thecode['quarter_chgper'].iat[0],df_thecode['year_chgper'].iat[0]],PER)
                    
                chart=wbk.add_chart({'type': 'line'})
                
                chart.add_series({
                 'name':['data', top+1, name_col],#
                 'categories':['data', top+1, date_col, top+1+the_datalen, date_col],
                 'values':['data', top+1, chg_col, top+1+the_datalen, chg_col],
                 #'line':{'color':'red'},      
                })        
                
                chart.set_size({'width':800,'height':300})
                
                pic_sheet.insert_chart(pic_top,1,chart)        
                
                top+=the_datalen+2  
                
                pic_top+=20
                
                n+=1
                
                print n
                
     
        print '数据输入完毕'
        wbk.close()
            
        return df_shareholder
        

    def run(self,keyholder):
        
        codes=self.codes
        
        codes=codes
        
        n=0
        
        for code in codes:
              
            stockName=self.stockNames[self.stockNames.code==code]['name'].iat[0]
            
            #对应股票主页
            mainUrl='http://quote.cfi.cn'
            
            mainDoc=pq('http://quote.cfi.cn/quote_'+code+'.html')
            
            if keyholder==True:
                #大股东变化页面
                keyHolderUrl=mainUrl+mainDoc("div[id='nodea22']")('a').attr.href
                
                stockid=keyHolderUrl.split('/')[-2]
                
                keyHolderDoc=pq(keyHolderUrl)
                
                #该股票股东变化的日期列表
                dates=keyHolderDoc("select[id='sel']").text().split()
                
                dates=pd.Series(dates)
                
                if len(dates>0):
                
                    dates=dates[dates>'2000-01-01']
                    
                    for date in dates:
                        
                        #第一次直接读取数据，第二次开始从下一个日期读取数据
                        if date!=dates[0]:
                            keyHolderDoc=pq('http://quote.cfi.cn/quote.aspx?stockid='+stockid+'&contenttype=gdtj&jzrq='+date)
                
                        df_keyHolder,df_keyHolderFlow=self.getKeyHolder(keyHolderDoc,code,stockName)
                        
                        print date+' '+code
                                    
            else:
                
                #股东户数页面
                shareholderUrl=mainUrl+mainDoc("div[id='nodea23']")('a').attr.href
                
                shareholderDoc=pq(shareholderUrl)
                
                #股东户数图，但不完善，只到16年
               # picUrl=shareholderDoc("img[alt='"+stockName+'('+code+')'+"股东户数图']").attr.src
                
                self.getShareholder(shareholderDoc,code,stockName)
                
                n+=1
            
                print code+' '+str(n)
                

def groupPlot(df_thecode,wbk,pic_sheet,data_sheet,codes,header,name_col,date_col,chg_col):
    
    the_datalen=len(df_thecode)
    
    code=df_thecode['code'].iat[0]
    
    the_name=df_thecode['name'].iat[0]
    
    n=codes.index(code)
    
    top=n*(the_datalen+2)
    
    pic_top=n*20
   
    data_sheet.write_row(top,0,header)
    
    for i in xrange(len(df_thecode)):
        
        data_sheet.write_row(top+i+1,0,df_thecode.iloc[i])
        
    pic_sheet.write(pic_top,0,code)
    
    pic_sheet.write(pic_top+1,0,the_name)
        
    chart=wbk.add_chart({'type': 'line'})
    
    chart.add_series({
     'name':['data', top+1, name_col],
     'categories':['data', top+1, date_col, top+1+the_datalen, date_col],
     'values':['data', top+1, chg_col, top+1+the_datalen, chg_col],
     #'line':{'color':'red'},      
    })        
    
    chart.set_size({'width':800,'height':300})
    
    pic_sheet.insert_chart(pic_top,1,chart)
    
    print code
    
                
if __name__ == '__main__':
            
    h=Holder()
    
    #更新前要把数据库里的，上一季报后的数据删除掉，再更新
    #h.get_day_shareholder()
        
#    h.run(keyholder=False) 
#    
    h.plotShareholder('2000-01-01','2017-12-08') 
