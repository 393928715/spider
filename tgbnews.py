# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 13:17:41 2017

@author: Administrator
"""
from pyquery import PyQuery as pq

import pandas as pd

doc=pq('https://www.taoguba.com.cn/Article/1793029/1')

s1=doc('div[class="p_coten"]')

text=s1.html()

s2=text.split(r'<br/>')

s2=pd.Series(s2)
   
s2=s2.apply(lambda x:filter(lambda y:(y >= u'\u4e00' and y<=u'\u9fa5') or (y in '0123456789') or (y in u'，。,.'),x))

s2=list(s2+'\n')

#fopen=open(r'E:\test\test.text','w')
#
#fopen.writelines(s2)
#    
#fopen.close()