#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-15 09:51:24
# Project: s8

import xlsxwriter

from sqlalchemy import create_engine 

import pandas as pd

import os

import tushare as ts

from merchandise import merchandise

import sys
sys.path.append("..")
reload(sys)      
sys.setdefaultencoding('utf-8')

class mdsePlot:
    
    def __init__(self,sdate,edate):
        
        self.engine=create_engine('mysql://root:lzg000@127.0.0.1/stocksystem?charset=utf8')
        
        self.fdir=u'E:\\work\\报表\\商品\\'
        
        self.chaindir=u'E:\\work\\商品数据\\产业链\\'
        
        self.elsedir=u'E:\\test\\预焙阳极.xlsx'
        
        self.lenlist=[]
                
        self.sdate=sdate        
        
        self.edate=edate
        

    #得到关联上下游股票名称的series
    def relatedStock(self,merchandise,streamdata):
        #streamdata=pd.read_sql('select * from industryday where date >=  "'+sdate+'" and date <= "'+edate+'"')
        relatedup=streamdata[streamdata.name==merchandise]['up']
        
        relateddown=streamdata[streamdata.name==merchandise]['down']
            
        return relatedup,relateddown
        
    #计算累计涨幅
    def allChg(self,df):
        
        df=df.sort_values('date')
        
        close0=df['close'].iat[0]
        
        df['chg']=df['close']/close0-1    
        
        df['endchg']=df['chg'].iat[-1]
        
        self.lenlist.append(len(df))
        
        return df  

    #补全数据
    def completing(self,szdata,data):  
#        if data.iat[0,0]==u'预焙阳极':
#            data.fillna('miss',inplace=True)
        
        data['date']=data['date'].drop_duplicates()
        
        data.dropna(inplace=True)
        
        data.set_index('date',inplace=True)
        
        data=data.reindex(szdata.index)
        
        data.reset_index(inplace=True)
        
        data['date']=data['date'].astype(str)    
        
        data['chg'].fillna(method='bfill',inplace=True)
        
        data['name'].fillna(method='ffill',inplace=True)
        
        data.fillna('miss',inplace=True)
        
        data.sort_values('date',inplace=True)
        
        return data
    
    
    #生成4个商品为一组的图
    def addChartSet(self,wbk,namecol,datecol,chgcol,maxlen,linewidth,loopindex,setrange,width,height):
     
       data_top=1
       
       interval=linewidth+1
       
       loopinterval=setrange*interval
       
       colorlist=['#FF0033','#FFFF00','#33CC99','#99CC33','#FF9900','#336699','#CC3366','#339933','#CC9966','#003366']
       
       bk_chart = wbk.add_chart({'type': 'line'})   
          
       bk_chart.set_style(4)
       #向图表添加数据 
           #沪深300
       for i in xrange(setrange):       
           
           color=colorlist[i]
           
           bk_chart.add_series({
            'name':['data', 1, namecol+loopindex*loopinterval+interval*i],
            'categories':['data', data_top, datecol+loopindex*loopinterval+interval*i, data_top+maxlen, datecol+loopindex*loopinterval+interval*i],
            'values':['data', data_top, chgcol+loopindex*loopinterval+interval*i, data_top+maxlen,chgcol+loopindex*loopinterval+interval*i],
            'line':{'color':color},#FF6666
            })       
                 
    #   bk_chart.set_title({'name':self.sdate+'-'+self.edate,
    #                       'name_font': {'size': 10, 'bold': True}
    #                       })
                           
       bk_chart.set_x_axis({'name':u'日期',
                            'name_font': {'size': 10, 'bold': True},
                            'label_position': 'low',
                            'interval_unit': 10                           
                            })
                            
       bk_chart.set_y_axis({'name':'',
                           'name_font': {'size': 10, 'bold': True}
                           })
       
       bk_chart.set_size({'width':width,'height':height})  
     
       return bk_chart 
           
 

    #生成单商品图
    def addChart(self,wbk,namecol,datecol,chgcol,datalen,linewidth,loopindex,name,width,height):
        
       data_top=1
       
       interval=linewidth+1  
       
       bk_chart = wbk.add_chart({'type': 'line'})   
          
       bk_chart.set_style(4)
       
       #向图表添加数据 
       bk_chart.add_series({
        'name':['data', 0, chgcol+loopindex*interval],
        'categories':['data', data_top, datecol+loopindex*interval, data_top+datalen, datecol+loopindex*interval],
        'values':['data', data_top, chgcol+loopindex*interval, data_top+datalen,chgcol+loopindex*interval],
        'line':{'color':'#336699'},#FF6666
        })
    
    
    #   bk_chart.add_series({
    #    'name':['data', 0, closecol+loopindex*interval],
    #    'categories':['data', data_top, datecol+loopindex*interval, data_top+datalen, datecol+loopindex*interval],
    #    'values':['data', data_top, closecol+loopindex*interval, data_top+datalen,closecol+loopindex*interval],
    #    'line':{'color':'FF0033'},  
    #    'y2_axis': True,            
    #    })
                 
       bk_chart.set_title({'name':name,
                           #'name_font': {'size': 10, 'bold': True}
                           })
                           
       bk_chart.set_x_axis({#'name':u'日期',
                            #'name_font': {'size': 10, 'bold': True},
                            'label_position': 'low',
                            'interval_unit': 10                           
                            })
                            
    #   bk_chart.set_y_axis({#'name':'',
    #                       'name_font': {'size': 10, 'bold': True}
    #                       })
       
       bk_chart.set_size({'width':width,'height':height})  
     
       return bk_chart    
       
       
       
    def plot(self,scope): 
    
        if scope == 'industry':
            table = 'industryday'
            #得到商品日线数据
            mdseday=pd.read_sql('select name,industry,date,close from '+table+' where date >= "'+self.sdate+'" and date <= "'+self.edate+'"',con=self.engine)#.drop_duplicates()#board,      
            #得到行业类别
            industries=mdseday['industry'].drop_duplicates()        
            
        else:
            table='boardday'
            #得到商品日线数据
            mdseday=pd.read_sql('select name,board,date,close from '+table+' where date >= "'+self.sdate+'" and date <= "'+self.edate+'"',con=self.engine)#.drop_duplicates()#board,
            #得到板块类别
            industries=mdseday['board'].drop_duplicates() 
            
            
        mdseday['date']=mdseday['date'].astype(str)  
 
        df_stream=pd.read_sql_table('stream',con=self.engine)
        
        if not os.path.exists(self.fdir):
            os.mkdir(self.fdir)
        
        
        for industry in industries:
            
            fname = self.fdir+industry+'.xlsx'
            
            wbk =xlsxwriter.Workbook(fname) 
            
            picsetsheet=wbk.add_worksheet(u'商品组')
            
            picsheet=wbk.add_worksheet(u'商品及股票')
            
            datasheet=wbk.add_worksheet('data')
            datasheet.hide()
            
            PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})
            
            if scope == 'industry':
                df_mdse=mdseday[mdseday.industry==industry]
            
            else:
                df_mdse=mdseday[mdseday.board==industry]
            
            #顶部
            top=0
            
            #左端
            left=0
            
            #数据行宽
            linewidth=6
            
            #数据头
            header=['name','industry','date','close',u'涨幅','endchg']#,'board'
            
            #获得数据列位置
            datecol=header.index('date')
            
            chgcol=header.index(u'涨幅')
            
            namecol=header.index('name')
            
           # closecol=header.index('close')
    
            df_mdse=df_mdse.groupby('name').apply(self.allChg)
            
            #按累计涨幅最大排序
            df_mdse.sort_values('endchg',inplace=True,ascending=False)
            
            #得到最新的，按涨幅排序的商品名
            lastdate=df_mdse['date'].max()
            
            sortnames=df_mdse[df_mdse.date==lastdate]['name'].drop_duplicates()
            
            namenum=len(sortnames)
            
            lenlist=[]
            
            streamleft=19
            streamtop=0
            loop=0
            for name  in sortnames:    
                
                #处理每种商品对应的数据
                data=df_mdse[df_mdse.name==name] 
                datalen=len(data)
                lenlist.append(datalen)
                datasheet.write_row(top,left,header )    
                data.sort_values('date',inplace=True)
                
                #得到每种商品的上下游
                up,down=self.relatedStock(name,df_stream)   
                
                #上下游股票写在图片右边
                picsheet.write(streamtop+2,streamleft,u'上游:')
                picsheet.write_row(streamtop+2,streamleft+1,up)
                
                picsheet.write(streamtop+4,streamleft,u'下游:')
                picsheet.write_row(streamtop+4,streamleft+1,down)                

#                for i in xrange(len(up)):
#                    picsheet.write(streamtop+1+i,streamleft,up.iat[i])
#                    try:
#                        picsheet.write(streamtop+1+i,streamleft+1,down.iat[i])
#                    except:
#                        pass
                
                tmpchart=self.addChart(wbk,namecol,datecol,chgcol,datalen,linewidth,loop,name,1200,600)
                picsheet.insert_chart(streamtop,0,tmpchart)
                    
                for i in xrange(len(data)):        
                    datasheet.write_row(top+i+1,left,data.iloc[i])
                    datasheet.write(top+i+1,left+4,data.iloc[i]['chg'],PER)
                    
                left+=linewidth+1
                streamtop+=30
                loop+=1
            
                
            maxlen=max(lenlist)
            
            lastloopflag=namenum-namenum%4
            
            n=0      
            loop=0    
            left=0        
            while 1:   
                n+=4
                
                if n>lastloopflag:
                    tmpchart=self.addChartSet(wbk,namecol,datecol,chgcol,maxlen,linewidth,loop,4,1200,600)
                    picsetsheet.insert_chart(top,left,tmpchart)
                    break
                
                tmpchart=self.addChartSet(wbk,namecol,datecol,chgcol,maxlen,linewidth,loop,4,1200,600)    
                picsetsheet.insert_chart(top,left,tmpchart)   
                top+=30      
                loop+=1
            
            wbk.close()
            
            print industry


    def plotRF(self,RF=True,update=False,days=1):
        
        if update == True:
        
            m=merchandise()   
            m.update(types='hy,ts',days=days)    
            m.updateElse()        
            
     
        #图组添加商品数目
        setrange=7 
        
        szdata=ts.get_h_data('000001', index=True,start=self.sdate,end=self.edate)
                
        rf_mdse=pd.read_table(u'E:\\work\\标的\\mdse.txt',names=['mdse'],encoding='gbk')
        
        df_mdse=pd.read_sql('select name,date,close,unit from industryday where date >= "'+self.sdate+'" and date <= "'+self.edate+'"',con=self.engine)
            
        mdsenames=df_mdse['name'].drop_duplicates()
        
        havenames=pd.Series()
        
        df_stream=pd.read_sql_table('stream',con=self.engine)
        
        #usenames=[]
        
        #获得可检测到的RF商品
        for name in rf_mdse['mdse']:
            cflag=mdsenames.str.contains(name)
            m=mdsenames[cflag]
            if not m.empty:
                havenames=havenames.append(m)
                #usenames.append(name)

        #获得有产业链图的商品名称
        chainlist=os.listdir(self.chaindir)
        chainlist=map(lambda x:x.replace('.png',''),chainlist)
        
        if RF==True:
            df_mdse=df_mdse[df_mdse['name'].isin(havenames)].drop_duplicates()
            
        else:
            df_mdse=df_mdse.drop_duplicates()

        fname = self.fdir+self.edate+u'商品监控'+'.xlsx'

        wbk =xlsxwriter.Workbook(fname) 
        
        chgsheet=wbk.add_worksheet(u'涨幅统计')
   
        picsetsheet=wbk.add_worksheet(u'商品组')
        
        picsheet=wbk.add_worksheet(u'商品明细')
        
        datasheet=wbk.add_worksheet('data')
        datasheet.hide()
        
        PER=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0.00%'})    
        title=wbk.add_format({'font_name':'微软雅黑','align':'center','valign':'vcenter','font_size':11})
        zwfloat=wbk.add_format({'align':'center','valign':'vcenter','font_size':11,'num_format':'0'})
        
        #顶部
        top=0
        
        #左端
        left=0
               
       # closecol=header.index('close')

        df_mdse=df_mdse.groupby('name').apply(self.allChg)
        
        #按累计涨幅最大排序
        df_mdse.sort_values('endchg',inplace=True,ascending=False)
            
        #得到最新的，按涨幅排序的商品名
        lastdate=df_mdse['date'].max()
        
        sortnames=df_mdse[df_mdse.date==lastdate]['name']
        
        namenum=len(sortnames)
        
        streamleft=17
        streamtop=0
        loop=0        
        
        chgList=[]
        maxlen=max(self.lenlist)
        for name  in sortnames:            
            #yearmiss=False
         
            #处理每种商品对应的数据
            data=df_mdse[df_mdse.name==name] 
                        
            data=self.completing(szdata,data)
            
            #数据头
            header=list(data.columns)
            chgindex=header.index('chg')
            header[chgindex]=u'涨幅'
            
            #数据行宽
            linewidth=len(header)      
            
            #获得数据列位置
            datecol=header.index('date')
            
            chgcol=header.index(u'涨幅')
            
            namecol=header.index('name')               

            datasheet.write_row(top,left,header)
            
            #计算周、月、季度涨幅            
            endchg=data.iloc[-1]['chg']
            daychg=endchg-data.iloc[-2]['chg']

            try:                
                weekchg=endchg-data.iloc[-6]['chg']
            except:
                weekchg='miss'
            
            try:
                monthchg=endchg-data.iloc[-23]['chg']   
            except:
                monthchg='miss'
            
            try:                
                quarterchg=endchg-data.iloc[-64]['chg'] 
            except:
                quarterchg='miss'                      
            
#            try:
#                yearchg=endchg-data.iloc[-251]['chg']
#            except:
#                yearmiss=True
                 
            #涨幅数据写入统计页面
           # if name == sortnames[0]:
                #chgList.append([u'名称',u'报价',u'单位',u'日涨幅',u'周涨幅',u'月涨幅',u'季涨幅'])
#                chghead=[u'名称',u'报价',u'单位',u'日涨幅',u'周涨幅',u'月涨幅',u'季涨幅']#,u'年涨幅'
#                chgsheet.write_row(loop+1,0,chghead,title)
#                chgsheet.write_row(loop,0,[u'日期:',self.edate],title)
                
            chgList.append([name,data['close'].iat[-1],data['unit'].iat[-1],daychg,weekchg,monthchg,quarterchg])
#            chgsheet.write_row(loop+2,0,[name,'',data['unit'].iat[-1],daychg,weekchg,monthchg,quarterchg],PER)
#            chgsheet.write(loop+2,1,data['close'].iat[-1],zwfloat)
                #,yearchg
#            else:
#                chgsheet.write_row(loop+2,0,[name,daychg,weekchg,monthchg,quarterchg,yearchg],PER)
                           
            #得到每种商品的上下游
            up,down=self.relatedStock(name,df_stream)  
            
            #上下游股票写在图片右边
            picsheet.write(streamtop,streamleft-1,name+u'上游:')
            picsheet.write_row(streamtop,streamleft+1,up)
            
            picsheet.write(streamtop+2,streamleft-1,name+u'下游:')
            picsheet.write_row(streamtop+2,streamleft+1,down)           
            
            #插入产业链图
            #去掉商品名称的括号内容,用于于产业链图名称比对
            clearname='(' in name and name[:name.find('(')] or name
            
            if clearname in chainlist:
                chainpic=self.chaindir+clearname+'.png'
                picsheet.insert_image(streamtop+5,streamleft,chainpic, {'x_scale':0.85,'y_scale':0.85 })
  
            tmpchart=self.addChart(wbk,namecol,datecol,chgcol,maxlen,linewidth,loop,name,1000,600)
            picsheet.insert_chart(streamtop,0,tmpchart)
                
            for i in xrange(len(data)):        
                datasheet.write_row(top+i+1,left,data.iloc[i])
                datasheet.write(top+i+1,left+chgcol,data.iloc[i]['chg'],PER)
                
            left+=linewidth+1
            streamtop+=30
            loop+=1
        
        #向涨幅页面写入数据
        chghead=[u'名称',u'报价',u'单位',u'日涨幅',u'周涨幅',u'月涨幅',u'季涨幅']
        
        df_chg=pd.DataFrame(chgList,columns=chghead)
        
        df_chg.sort_values(u'日涨幅',ascending=False,inplace=True)
        
        for i in xrange(len(df_chg)):
            
            if i == 0 :
                chgsheet.write_row(0,0,[u'日期:',self.edate],title)
                
                chgsheet.write_row(1,0,chghead,title)
                
            chgsheet.write_row(i+2,0,df_chg.iloc[i][[u'名称',u'报价',u'单位']],zwfloat)
            
            chgsheet.write_row(i+2,3,df_chg.iloc[i][[u'日涨幅',u'周涨幅',u'月涨幅',u'季涨幅']],PER)
            
            
        chgsheet.set_column(0,len(chghead),15)
                            
        lastloopflag=namenum-namenum%setrange
        
        n=0      
        loop=0    
        left=0        
        height=1300
        width=700
        space=width/20
        
        while 1:   
            n+=setrange           
            if n>lastloopflag:
                tmpchart=self.addChartSet(wbk,namecol,datecol,chgcol,maxlen,linewidth,loop,setrange,height,width)
                picsetsheet.insert_chart(top,left,tmpchart)
                break
            
            tmpchart=self.addChartSet(wbk,namecol,datecol,chgcol,maxlen,linewidth,loop,setrange,height,width)    
            picsetsheet.insert_chart(top,left,tmpchart)   
            top+=space      
            loop+=1
        
        wbk.close()
        
if __name__ == '__main__':

    s=mdsePlot(sdate='2017-01-01',edate='2017-10-30')
    
    s.plotRF(RF=True,update=False,days=1)
