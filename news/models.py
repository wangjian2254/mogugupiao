#coding=utf-8
#author:u'王健'
#Date: 12-7-10
#Time: 下午9:17
__author__ = u'王健'



from google.appengine.ext import db

__author__ = 'Administrator'

class NeedSyncGuPiao(db.Model):
    gpcode=db.StringListProperty(indexed=False)


class GuPiaoGroup(db.Model):
    code=db.StringProperty()#群code
    gpcode=db.StringProperty()#股票代码
    createTime=db.DateTimeProperty(auto_now_add=True)#创建时间

