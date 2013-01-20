#coding=utf-8
#author:u'王健'
#Date: 12-7-10
#Time: 下午9:50
from news.models import  NeedSyncGuPiao, GuPiaoGroup
import setting
from tools.page import Page
from google.appengine.api import urlfetch
import urllib,json
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

class DeleteNeedSyncGuPiao(Page):
    def get(self):
        needGuPiao=NeedSyncGuPiao.get_by_key_name('syncgupiao')
        if needGuPiao:
            date=datetime.datetime.utcnow()+datetime.timedelta(hours =8)
            if date.strftime('%Y-%m-%d')!=needGuPiao.date:
                pam={}
                pam['needdelgroupid']=','.join(needGuPiao.memcachegroupid)
                login_data=urllib.urlencode(pam)
                result = urlfetch.fetch(
                    url =setting.WEBURL+'/DeleteNeedSyncGuPiao',
                    payload = login_data,
                    method = urlfetch.POST,
                    headers = {'Content-Type':'application/x-www-form-urlencoded',
                               'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
                    follow_redirects = False,deadline=20)
                if result.status_code == 200 :
                    needGuPiao.memcachegroupid=[]
                    needGuPiao.gpcode=[]
                    needGuPiao.put()
class NeedSyncGuPiao(Page):
    def get(self):
        groupidList=[]
        result = urlfetch.fetch(
            url =setting.WEBURL+'/NeedSyncGuPiao',
#                    payload = login_data,
            method = urlfetch.GET,
            headers = {'Content-Type':'application/x-www-form-urlencoded',
                       'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
            follow_redirects = False,deadline=20)
        if result.status_code == 200 :
            groupidList.extend(result.content.split(','))
            if groupidList:
                needGuPiao=memcache.get('syncgupiao')
                if not needGuPiao:
                    needGuPiao=NeedSyncGuPiao.get_by_key_name('syncgupiao')
                if needGuPiao :
                    for groupid in groupidList:
                        gupiaoGroup=memcache.get('group'+groupid)
                        if not gupiaoGroup:
                            gupiaoGroup=GuPiaoGroup.get_by_key_name('g'+groupid)
                        if gupiaoGroup:
                            memcache.set('group'+groupid,gupiaoGroup,36000)
                            if gupiaoGroup.realNo not in needGuPiao.gpcode:
                                needGuPiao.gpcode.append(gupiaoGroup.realNo)
                                needGuPiao.memcachegroupid.append("needsyncgupiao_groupid%s"%gupiaoGroup.key().name())
                                needGuPiao.put()
                    memcache.set('syncgupiao',needGuPiao,36000)
class MarkGroup(Page):
    def get(self):
        groupid=self.request.get('groupid')
        dm=self.request.get('dm')
        type=self.request.get('type')
        realNo=self.request.get('realNo')
        gupiaoGroup=memcache.get('group'+groupid)
        if not gupiaoGroup:
            gupiaoGroup=GuPiaoGroup.get_by_key_name('g'+groupid)
            if gupiaoGroup:
                memcache.set('group'+groupid,gupiaoGroup,36000)
        if not gupiaoGroup:
            if groupid and dm and type and realNo:
                gupiaoGroup=GuPiaoGroup(key_name='g'+groupid)
                gupiaoGroup.gpcode=dm
                gupiaoGroup.realNo=realNo
                gupiaoGroup.type=type
                gupiaoGroup.put()
                memcache.set('group'+groupid,gupiaoGroup,36000)
            else:
                self.error(500)
                return
        needGuPiao=memcache.get('syncgupiao')
        if not needGuPiao:
            needGuPiao=NeedSyncGuPiao.get_by_key_name('syncgupiao')
        if needGuPiao and gupiaoGroup.realNo not in needGuPiao.gpcode:
            needGuPiao.gpcode.append(gupiaoGroup.realNo)
            needGuPiao.memcachegroupid.append("needsyncgupiao_groupid%s"%gupiaoGroup.key().name())
            needGuPiao.put()
            memcache.set('syncgupiao',needGuPiao,36000)

        pass

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
        gupiaolist=[]
        post_data={}
        for gupiaostr in gpstrlist:
            flag=memcache.get(gupiaostr)
            if flag:
                continue
            memcache.set(gupiaostr,'flag',3600)
            gupiao_data_arr=gupiaostr[11:].split('=')
            gupiao_group=memcache.get(gupiao_data_arr[0])
            if not gupiao_group:
                gupiao_group=GuPiaoGroup.all().filter('realNo =',gupiao_data_arr[0]).fetch(1)
                if len(gupiao_group)==1:
                    gupiao_group=gupiao_group[0]
                    memcache.set(gupiao_group.realNo,gupiao_group,3600*24*3)
                else:
                    gupiao_group=None
            if gupiao_group:
                groupid=gupiao_group.key().name()
                gupiaolist.append(groupid)
#                post_data['flag'+groupid]=gupiao_data_arr[-25:]
                post_data[groupid]="{'groupid':'%s','realNo':'%s','type':'%s','min':'[*sys/min%s/a777_1*]','daily':'[*sys/daily%s/a777_1*]','weekly':'[*sys/weekly%s/a777_1*]','monthly':'[*sys/monthly%s/a777_1*]','data':'%s'}"%(groupid[1:],gupiao_group.realNo,gupiao_group.type,groupid,groupid,groupid,groupid,gupiao_data_arr[1][1:-2])
#                json.dumps({'groupid': groupid[1:], 'realNo': gupiao_group.realNo,
#                            'type': gupiao_group.type, 'data': gupiao_data_arr[1][1:-2]})
        post_data['groupids']=','.join(gupiaolist)
        result = urlfetch.fetch(
            url =setting.WEBURL+'/SyncGuPiao',
            payload = urllib.urlencode(post_data),
            method = urlfetch.POST,
            headers = {'Content-Type':'application/x-www-form-urlencoded',
                       'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
            follow_redirects = False,deadline=30)
        if result.status_code == 200 :
            return

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