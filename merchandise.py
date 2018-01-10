# -*- coding: utf-8 -*-
"""
Created on Tue Aug 08 13:56:18 2017

@author: Administrator
"""
from pyquery import PyQuery as pq

import pandas as pd

from sqlalchemy import create_engine

import os

import glob

import time

from industrychain import industryChain

from stream import stream


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#from itertools import izip_longest    # zip_longest -> Python 3, izip_longest -> Python 2  
#chunk_list = lambda a_list, n: izip_longest(*[iter(a_list)]*n)

class merchandise():
    
    def __init__(self):
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')   
        self.csvdir=u'E:/work/商品数据/'
        self.mdseElseDir=u'E:\\work\\商品数据\\其他商品数据\\'
        #self.rooturl='http://top.100ppi.com/'
    
    def periodUrl(self,findname,hyhtml,period):
        
        tmphtml=hyhtml[hyhtml.find(findname):]
        
        if period == '日':        
            tmphtml=tmphtml[:tmphtml.find(unicode(period))]
            
        elif period == '周':
            tmphtml=tmphtml[tmphtml.find(u'日'):tmphtml.find(unicode(period))]
        
        elif period == '月':
            tmphtml=tmphtml[tmphtml.find(u'周'):tmphtml.find(unicode(period))]
            
        elif period == '季':
            tmphtml=tmphtml[tmphtml.find(u'月'):tmphtml.find(unicode(period))]        
            
        elif period == '年':
            tmphtml=tmphtml[tmphtml.find(u'季'):tmphtml.find(unicode(period))]            
        
        findurl=pq(tmphtml)('a').attr.href
        
        return findurl


    def table(self,nydoc):
    
        textdoc=nydoc('table')('tr')
        
        tmplist=[]
        
        for i in textdoc:       
            
            tmptext=textdoc(i).text().split()      
            
            if len(tmptext)!=7:
                
                tmpdoc=textdoc(i)('td')
                
                tmptext=[]
                
                for j in tmpdoc:
                    
                    tmpchar=tmpdoc(j).text()
                    
                    if len(tmpchar)<=1:
                        
                        tmpchar=-1
                        
                    tmptext.append(tmpchar)          
                         
            tmplist.append(tmptext)
        
        #nylist = list(chunk_list(nytext.split(), 7))
        
        df_theday=pd.DataFrame(tmplist[1:],columns=['name','industry','close0','close','unit','chg','tbchg'])
               
        df_theday.drop(df_theday.columns[2],axis=1,inplace=True)
             
        return df_theday
    
    
    def download(self,name,period,days,update):
        
        name=unicode(name)
        
        now=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        
        if update == False:        
        
            fdir=os.path.join(self.csvdir,unicode(period))
                
            if not os.path.exists(fdir):
                os.mkdir(fdir)
                
            fname=os.path.join(fdir,name+'.csv')     
            
            if os.path.exists(fname):
                print fname
                flag=input(u'该文件已存在,是否要继续(1/0)')
                if flag != 1 :
                    return 0
                
        rooturl='http://top.100ppi.com/'
        
        doc=pq(rooturl)
        
        if name in ['期货近约榜','期货主约榜','农产品近约榜','工业品近约榜','有色金属近约榜','能源石化近约榜','农产品主约榜','工业品主约榜','有色金属主约榜','能源石化主约榜']:
        
            hydoc=doc('div[class="fl"]').eq(4)
            
            hyhtml=hydoc.html()
            
            url='http://top.100ppi.com/'+self.periodUrl(name,hyhtml,period).strip()   
            
            headurl=url[:url.find('fdetail')]
            
        
        elif name in ['稀土榜','化肥榜','氟化工榜','磷化工榜','溴化工榜','氯碱产业榜','甲醇产业榜','丙烯产业榜','苯乙烯产业榜','乙二醇产业榜','PTA产业榜','橡胶榜','塑料榜','资源商品榜','商品题材榜','五大钢材榜']:
            hydoc=doc('div[class="fl"]').eq(1)
        
            hyhtml=hydoc.html()
            
            url=self.periodUrl(name,hyhtml,period).strip()
        
            headurl=url[:url.find('detail')]
            
            table = 'boardday'
            
            nextclassid=1
            
        elif name in ['能源榜','化工榜','橡塑榜','纺织榜','有色榜','钢铁榜','建材榜','农副榜']:
            hydoc=doc('div[class="fl"]')
        
            hyhtml=hydoc.html()
            
            url=self.periodUrl(name,hyhtml,period).strip()
        
            headurl=url[:url.find('detail')]
            
            table = 'industryday' 
            
            nextclassid=2
            
        doc=pq(url)
               
        df_days=pd.DataFrame()
        for i in xrange(days): 
                     
            df_theday=self.table(doc)
            
            title=doc('title').text()
            
            date=title[title.find('(')+1:title.find(')')].replace(u'年','-').replace(u'月','-').replace(u'日','')
            
            if i==0:
                lastdate=0
            
            if date!=lastdate:
                
    #            
    #            print date
    #            
    #            if date != now:
    #                flag=input(u'数据未更新到今天，是否继续(1/0)')
    #                if flag != 1 :
    #                    return 0                
    #            
                df_theday[u'date']=date
                
                if table == 'boardday':
                    board=title[:title.find(u'价格')]             
                    board=filter(lambda x:x not in '#0123456789',board)                
                    df_theday['board']=board
                
                df_theday['chg']=(df_theday['chg'].str.replace('%','')).astype('float')
                            
                if update == False:
                    if i==0:
                        df_theday.to_csv(fname,index=None,encoding='gbk')
                    else:
                        df_theday.to_csv(fname,index=None,mode='a',encoding='gbk',header=None)            
                else:
                    df_days=df_days.append(df_theday)  
                    if i%30==0:
                        df_days.drop_duplicates(inplace=True)
                        df_days.to_sql(table,con=self.engine,if_exists='append',index=None)
                        df_days=pd.DataFrame()
                        
                    elif i == (days-1):
                        df_days.drop_duplicates(inplace=True)
                        df_days.to_sql(table,con=self.engine,if_exists='append',index=None)
                        
                print name+' '+date
                
            try:
                nynexturl=headurl+doc('div[class="phone"]').eq(nextclassid).find('a').attr.href
            except Exception as e:
                print e
                break
            
            doc=pq(nynexturl)
            
            lastdate=date



    def industrySql(self,period):
        
        flist=glob.glob(self.csvdir+period+'\\*.csv')
        for f in flist:
            s1=pd.read_csv(f,encoding='gbk').drop_duplicates()
            s1.columns=['name','industry','close','unit','chg','tbchg','date']
            #s1['chg']=(s1['chg'].str.replace('%','')).astype('float')
            s1['chg']= s1['chg']/100
            #s1.columns=['name','board','close','unit','chg','tbchg','date']
            s1.to_sql('industryday',con=self.engine,if_exists='append',index=None)
            
            print f   
            
    
    def boardSql(self,period):
        
        flist=glob.glob(self.csvdir+period+'\\*.csv')
        for f in flist:
            s1=pd.read_csv(f,encoding='gbk').drop_duplicates()
            s1.columns=['name','industry','close','unit','chg','tbchg','date','board']
            s1['chg']=(s1['chg'].str.replace('%','')).astype('float')
            #s1.columns=['name','board','close','unit','chg','tbchg','date']
            s1.to_sql('boardday',con=self.engine,if_exists='append',index=None)
            
            print f          
    

    def updateElse(self):
        import pymysql
        
        #更新产业链图
        i=industryChain()
        i.download()    
        print 'industryChain done...'
        
        conn=pymysql.connect(host='localhost',
                user='root',
                passwd='lzg000',
                db='stocksystem',
                port=3306,
                charset='utf8'
                )    
        cursor=conn.cursor()    
        
        deletesql1="SET SQL_SAFE_UPDATES=0;"
        
        deletesql2="delete FROM industryday where name in('预焙阳极','碳酸锂(电池级)','黑钨精矿','氧化铝');"
        
        deletesql3="truncate table stream;"
        
        cursor.execute(deletesql1)   
        print deletesql1
        
        cursor.execute(deletesql2)   
        print deletesql2
        
        cursor.execute(deletesql3)   
        print deletesql3
        
        conn.commit()
                       
        conn.close()
        
       
        
        #更新上下游
        s=stream()
        s.download()
        print 'stream done...'        
               
        self.updateHwjk()
        
        self.updateYbyj()
        
        self.update_yhl()
              
        df_tsl=self.updateLiBattery()
        
        df_tsl.to_sql('industryday',con=self.engine,if_exists='append',index=None)
        
        print 'done...'

   
    def updateLiBattery(self):
    
        def average(df):   
            quotationMean=df[u'报价'].mean()
            df['close']=quotationMean
            return df.iloc[0]
        
        doc=pq('http://www.100ppi.com/price/?f=search&c=product&terms=%E7%A2%B3%E9%85%B8%E9%94%82&p=1')
        df=pd.DataFrame()
        nexturl=0
        
        while 1:
            datalistdoc=doc('tr')
            
            n=0
            datalist=[]
            for datadoc in datalistdoc:
                text=pq(datadoc).text()
                if n == 0:
                    head=text.split()
                
                if u'电池级' in text and u'出厂价' in text:
                    datalist.append(text.replace(u'元/吨','').split())
                
                n+=1
                
            df_tmp=pd.DataFrame(datalist,columns=head)
            df_tmp[u'报价']=df_tmp[u'报价'].astype('int')
            df_tmp=df_tmp.groupby(u'发布时间').apply(average)
            df=df.append(df_tmp)
            
            urlsdoc=doc('div[class="page-inc"]')('a')
            
            for each in urlsdoc:
                eachdoc=pq(each)
                if eachdoc.text() == u'下一页':
                    url='http://www.100ppi.com/price/'+eachdoc.attr.href
                
            if url != nexturl:
                nexturl=url
            else:
                break
            
            doc=pq(nexturl)
            print nexturl
              
        df=df.loc[:,[u'商品名称',u'发布时间','close']].drop_duplicates().sort_values(u'发布时间')
        df.columns=['name','date','close']
        df['unit']=u'元/吨'
        df['name']=df['name']+u'(电池级)'
        
        return df
        
        
    def updateHwjk(self):
        
        doc=pq('https://hq.smm.cn/wu')
        
        hwjkText=doc('div[class="first"]').eq(0).text()
        
        hwjkPrice=hwjkText.split()[2]
        
        date=doc('div[class="itemDateTime"]').eq(0).text()
        
        date=date.replace(u'日','').replace(u'月','-')
        
        date='2017-'+date
        
        df_hwjk=pd.read_excel(self.mdseElseDir+'hwjk.xlsx')
        
        df_hwjk=df_hwjk.append(pd.DataFrame({'date':[date],'close':[hwjkPrice],'unit':[u'元/吨']}))
        
        df_hwjk.to_excel(u'E:\\work\\商品数据\\其他商品数据\\hwjk.xlsx',index=None)             
        
        df_hwjk['name']=u'黑钨精矿'        
        
        df_hwjk.to_sql('industryday',con=self.engine,if_exists='append',index=None)      
        
        print u'黑钨精矿 done...'


    def updateYbyj(self):
        
        df_ybyj=pd.read_excel(self.mdseElseDir+'ybyj.xlsx').dropna()
        
        df_ybyj.reset_index(inplace=True)
        
        df_ybyj.columns=['date','close']
        
        df_ybyj['date']=df_ybyj['date'].apply(lambda x:str(x).strip())
        
        df_ybyj['name']=u'预焙阳极'
        
        df_ybyj['unit']=u'元/吨'        
        
        df_ybyj.to_sql('industryday',con=self.engine,if_exists='append',index=None)     
        
        print u'预焙阳极 done...'
        
    def update_yhl(self):
    
        main_url='http://www.100ppi.com/price/'
        
        text_list=[]
        
        main_doc=pq('http://www.100ppi.com/price/?f=search&c=product&terms=%E6%B0%A7%E5%8C%96%E9%93%9D&p=1')
        
        n=0
        
        df_yhl=pd.DataFrame()
        
        while main_doc:
        
            text_doc=main_doc('tr')
            
            for each in text_doc:
                
                if each != text_doc[0]:
                
                    text=pq(each).text().split()
                    
                    text_list.append(text)
            
            s1=pd.DataFrame(text_list)
            
            df_yhl=df_yhl.append(s1)
            
            url_doc=main_doc('div[class="page-inc"]')('a')
            
            for each in url_doc:
                
                each_doc=pq(each)
                
                if each_doc.text()=='下一页':
                    
                    next_url=main_url+each_doc.attr.href
                    
                    break
                    
                else:
                    
                    next_url=None
            
            try:
                main_doc=pq(next_url)
            except:
                break
            
            n+=1
            
            print n
        
        df_yhl.drop([1,2,3],axis=1,inplace=True)
        
        df_yhl.columns=['name','close','date']
        
        df_yhl['close']=df_yhl['close'].apply(lambda x:x.replace(u'元/吨','')).astype(int)
        
        df_yhl['unit']=u'元/吨'
        
        def average(df):   
            quotationMean=df['close'].mean()
            df['close']=quotationMean
            return df.iloc[0]
        
        df_yhl=df_yhl.groupby('date').apply(average)
        
        df_yhl.to_sql('industryday',con=self.engine,if_exists='append',index=None)
        
        print '氧化铝done...'

            
    def update(self,types,days):
        #qh=['期货近约榜','期货主约榜','农产品近约榜','工业品近约榜','有色金属近约榜','能源石化近约榜','农产品主约榜','工业品主约榜','有色金属主约榜','能源石化主约榜']
        ts=['稀土榜','化肥榜','氟化工榜','磷化工榜','溴化工榜','氯碱产业榜','甲醇产业榜','丙烯产业榜','苯乙烯产业榜','乙二醇产业榜','PTA产业榜','橡胶榜','塑料榜','资源商品榜','商品题材榜','五大钢材榜']
        hy=['能源榜','化工榜','橡塑榜','纺织榜','有色榜','钢铁榜','建材榜','农副榜']
        
        if types == 'hy':
            ranges=[hy]
        
        elif types == 'hy,ts' or types == 'ts,hy':
            ranges=[hy,ts]
        
        elif types == 'ts':
            ranges=[ts]
       
        for names in ranges:
            for name in names:
                self.download(name,'行业日',days=days,update=True)        
    
if __name__ == '__main__':
    
    m=merchandise()
    
    #m.update(types='ts',days=7)
    
    m.updateElse()
    #m.updateYbyj()

