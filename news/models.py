#coding=utf-8
#author:u'王健'
#Date: 12-7-10
#Time: 下午9:17
__author__ = u'王健'



from google.appengine.ext import db

__author__ = 'Administrator'

class NeedSyncGuPiao(db.Model):
    gpcode=db.StringListProperty(indexed=False)
    memcachegroupid=db.StringListProperty(indexed=False)
    date=db.StringProperty(indexed=False)


class GuPiaoGroup(db.Model):
    realNo=db.StringProperty()#获取股票数据时用的股票代码 如：gb_sdf、sz0323
    gpcode=db.StringProperty()#股票代码
    type=db.StringProperty()#股票类型 A股 B股
    createTime=db.DateTimeProperty(auto_now_add=True)#创建时间

