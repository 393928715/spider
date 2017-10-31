# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:44:16 2017

@author: Administrator
"""

#coding=utf-8
import urllib
from pyquery import PyQuery as pq
import os


class industryChain:
    
    def __init__(self):
        
        self.picdir=u'E:/work/商品数据/产业链/'

    def downloadGroup(self):
        
        maindoc=pq('http://www.100ppi.com/monitor/')
        
        mainhtml=maindoc.html()
        
        index=maindoc('td[class="stit"]').text().split()
        
        for i in xrange(len(index)):
            
            if i==7:
                usehtml=mainhtml[mainhtml.find('target="_blank">'+index[i]):]
            else:       
                usehtml=mainhtml[mainhtml.find('target="_blank">'+index[i]):mainhtml.find('target="_blank">'+index[i+1])]
            
            usedoc=pq(usehtml)
            
            seconddoc=usedoc('td[class="w1"]')
            
            secondindex=seconddoc.text().split()
            
            for j in xrange(len(secondindex)):
                
                fdir=self.picdir#+index[i]
                
                if not os.path.exists(fdir):
                    os.mkdir(fdir)
                    
                fname=os.path.join(fdir,secondindex[j]+'.png')
                
                secondurl=seconddoc('a').eq(j).attr.href
                
                thirdhtml=pq('http://www.100ppi.com'+secondurl).html()
                
                pichtml=thirdhtml[thirdhtml.find(u'产业链'):]
                
                picurl=pq(pichtml)('img').attr.src       
        
                urllib.urlretrieve(picurl,fname)
                
                print fname
        

    def download(self):
        
        def callbackfunc(blocknum, blocksize, totalsize):
            '''回调函数
            @blocknum: 已经下载的数据块
            @blocksize: 数据块的大小
            @totalsize: 远程文件的大小
            '''
            print n
                
        
        maindoc=pq('http://www.100ppi.com/monitor/')

        maindoc=maindoc('td[class ="w1"]')('a')
        
        n=0
        
        for each in maindoc:
            
            mdseurl='http://www.100ppi.com'+str(pq(each).attr.href)
                      
            mdsedoc=pq(mdseurl)
            
            name=mdsedoc('div[class="banner"]').text()
            
            fname=os.path.join(self.picdir,name+'.png')
            
            for each2 in mdsedoc('td[align="center"]')('img'):
                
                eachurl = pq(each2).attr.src
                
                if 'product' in eachurl:
                    
                    imgurl=eachurl
                    
                    urllib.urlretrieve(imgurl,fname)
                    
                    n+=1
                    
                    print n
                    
                    break
                    
        
if __name__ == '__main__':
    i=industryChain()
    i.download()
#def getHtml(url):
#    page = urllib.urlopen(url)
#    html = page.read()
#    return html
#
#def getImg(html):
#    reg = r'src="(.+?\.png)" '
#    imgre = re.compile(reg)
    #    imglist = re.findall(imgre,html)
#    x = 0
#    for imgurl in imglist:
#        print imgurl
#        urllib.urlretrieve(imgurl,'%s.png' % x)
#        x+=1
#
#
#html = getHtml("http://www.100ppi.com/price/detail-4218781.html")
#
#getImg(html)