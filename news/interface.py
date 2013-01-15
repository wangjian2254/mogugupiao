#coding=utf-8
#author:u'王健'
#Date: 12-7-10
#Time: 下午9:50
from news.models import  NeedSyncGuPiao
import setting
from tools.page import Page
from google.appengine.api import urlfetch
import urllib
import logging
import datetime
from google.appengine.api import memcache
__author__ = u'王健'


gpdm=['sh','sz','hk']
#baseurl='http://hq.sinajs.cn/list='
#http://suggest3.sinajs.cn/suggest/type=&name=suggestdata_1357476438968&key=shg
class GuPiao(Page):
    def get(self):
        self.render('templates/gupiao.html',{})

    def post(self):
        gupiaono=self.request.get('gupiaono')
        if gupiaono:
            #http://hq.sinajs.cn/list=
            baseurl='http://hq.sinajs.cn/list='
            for dm in gpdm:
                baseurl+=dm+gupiaono+','
            result = urlfetch.fetch(
                url = baseurl,
#                    payload = login_data,
                method = urlfetch.GET,
                headers = {'Content-Type':'application/x-www-form-urlencoded',
                           'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
                follow_redirects = False,deadline=20)
            if result.status_code == 200 :
                gupiaoArr=result.content.decode('gbk').split('\n')
                succ=False
                for g in gupiaoArr:
                    if g and  g.rindex('"')-g.index('"')>1:
                        succ=True
                        self.response.out.write(g[g.index('"'):g.rindex('"')])
                if not succ:
                    self.response.out.write(u'查询的 “%s” 代码不存在'%gupiaono)
            else:
                self.response.out.write(u'查询“%s”出错'%gupiaono)

class InfoUpdate(Page):
    def get(self):
        memcacheFlag=self.request.get('memcache','')
        if memcacheFlag:
            urllist=memcache.get('needsyncgupiao')
            if not urllist:
                urllist=[]
        else:
            needGuPiao=NeedSyncGuPiao.get_by_key_name('syncgupiao')
            if not needGuPiao:
                needGuPiao=NeedSyncGuPiao(key_name='syncgupiao')
                needGuPiao.put()
            baseurl='http://hq.sinajs.cn/list='
    #        for gp in needGuPiao.gpcode:
            tempurl=baseurl
            urllist=[]
            for gp in needGuPiao.gpcode:
                if len(tempurl)+len(gp)>2047:
                    urllist.append(tempurl)
                    tempurl=baseurl
                tempurl+='%s,'%gp
        memcache.set('needsyncgupiao',urllist[10:],3600)


        resultlist=[]
        rpcs=[]
        for url in urllist[:10]:
            rpc = urlfetch.create_rpc()
            rpc.callback = self.create_callback(rpc,resultlist)
            rpc.deadline=30
            urlfetch.make_fetch_call(rpc, url,headers = {'Content-Type':'application/x-www-form-urlencoded',
                                   'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'})
            rpcs.append(rpc)
        for rpc in rpcs:
            rpc.wait()
        gpstrlist=[]
        for gupiaoArr in resultlist:
            gpstrlist.extend(gupiaoArr.split('\n'))
            #self.response.out.write(u'%s'%gupiaoArr)
        for gupiaostr in gpstrlist:
            pass
#        result = urlfetch.fetch(
#            url = baseurl,
##                    payload = login_data,
#            method = urlfetch.GET,
#            headers = {'Content-Type':'application/x-www-form-urlencoded',
#                       'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
#            follow_redirects = False,deadline=30)
#        if result.status_code == 200 :
#            self.response.out.write(u'%s长度'%len(baseurl))
#            gupiaoArr=result.content.decode('gbk')
#
#            self.response.out.write(u'%s'%gupiaoArr)
#        else:
#            self.response.out.write(u'查询出错:%s长度'%len(baseurl))


    def handle_result(self,rpc,resultlist):
        result = rpc.get_result()
        if result.status_code == 200 :
            #self.response.out.write(u'%s长度'%len(baseurl))
            gupiaoArr=result.content.decode('gbk')
            resultlist.append(gupiaoArr)

#        else:
#            self.response.out.write(u'查询出错:%s长度'%len(baseurl))
        # ... Do something with result...

    # Use a helper function to define the scope of the callback.
    def create_callback(self,rpc,resultlist):
        return lambda: self.handle_result(rpc,resultlist)