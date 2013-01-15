#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import json
from google.appengine.api import memcache

__author__ = u'王健'

from google.appengine.ext import db

class User(db.Model):
    nickname=db.StringProperty(indexed=False)#昵称
    desc=db.StringProperty(indexed=False)
    birthday=db.StringProperty(indexed=False)#生日
    header=db.IntegerProperty(indexed=False,default=0)#生日
    sheng=db.IntegerProperty()#省
    city=db.IntegerProperty()#市
    sex=db.BooleanProperty(default=True)#true 为女性
    say=db.StringProperty(indexed=False)
    friends=db.StringListProperty(indexed=False)
    stranger=db.StringListProperty(indexed=False)
#    frienddel=db.StringListProperty(indexed=False)
    #有群功能后添加的属性
    createGroup=db.ListProperty(item_type=int,indexed=False)
    createGroupAdd=db.ListProperty(item_type=int,indexed=False)
    createGroupRemove=db.ListProperty(item_type=int,indexed=False)
    partnerGroup=db.ListProperty(item_type=int,indexed=False)
    partnerGroupAdd=db.ListProperty(item_type=int,indexed=False)
    partnerGroupRemove=db.ListProperty(item_type=int,indexed=False)
    memberGroup=db.ListProperty(item_type=int,indexed=False)
    memberGroupAdd=db.ListProperty(item_type=int,indexed=False)
    memberGroupRemove=db.ListProperty(item_type=int,indexed=False)

class UserPoint(db.Model):
    point=db.IntegerProperty(indexed=False,default=0)#群主积分

class Tag(db.Model):#int id
    name=db.StringProperty()#标签名


class Group(db.Model):#int id
    name=db.StringProperty()#群名称
    gonggao=db.StringProperty(indexed=False)
    head=db.IntegerProperty(indexed=False)
    author=db.StringProperty()#群拥有者
    partner=db.StringListProperty()#群主
    member=db.StringListProperty()#参与者
    type=db.IntegerProperty()#群类型
    apptype=db.StringProperty(default='3')
    topcount=db.IntegerProperty(indexed=False,default=10)#置顶帖数量
    topnum=db.IntegerProperty(indexed=False,default=0)#设置的置顶帖
    notecount=db.IntegerProperty(indexed=False,default=200)#帖最大数量
    notenum=db.IntegerProperty(indexed=False,default=0)#帖数量
    tag=db.IntegerProperty()#群标签

    def put(self, **kwargs):
        if self.name:
            self.name=self.name.replace('<','[').replace('>',']')
        if self.gonggao:
            self.gonggao=self.gonggao.replace('<','[').replace('>',']')
        super(Group,self).put(**kwargs)
        memcache.set('groupbyid'+str(self.key().id()),self,3600)


class RssImg(db.Model):
    imgdic=db.TextProperty(default='{}')
    def getImgDic(self):
            return json.loads(self.imgdic)
    def setImgDic(self,imgdic=None):
        if imgdic:
            self.imgdic=json.dumps(imgdic)

class RssNote(db.Model):#rss 帖子
    notelist=db.TextProperty(default='[]')

    def getNoteList(self):
        return json.loads(self.notelist)
    def setNoteList(self,notelist=None):
        if notelist:
            self.notelist=json.dumps(notelist)


#class RssReplay(db.Model):# string id 和 Note一致
#    group=db.IntegerProperty()#所属群
#    content=db.TextProperty()#帖子内容json
#    updateTime=db.DateTimeProperty()#最后一次修改时间

class Note(db.Model):#int id
    group=db.IntegerProperty()#所属群
    title=db.StringProperty(indexed=False)
    content=db.TextProperty()#帖子内容
    author=db.StringProperty()#帖子作者
    point=db.IntegerProperty(default=0)#帖子积分
    up=db.IntegerProperty(default=0,indexed=False)#帖子顶的次数
    down=db.IntegerProperty(default=0,indexed=False)#帖子踩的次数
    updateTime=db.DateTimeProperty()#最后一次修改时间
    isTop=db.BooleanProperty(default=False)#是否置顶
    isDelete=db.BooleanProperty(default=False)#是否被删除

    def put(self, **kwargs):
        if self.title:
            self.title=self.title.replace('<','[').replace('>',']').replace("'",u"“").replace('"',u"“")
        if self.content:
            self.content=self.content.replace('<','[').replace('>',']')
        super(Note,self).put(**kwargs)
        memcache.set('note'+str(self.key().id()),self,36000)

class DaTingNote(db.Model):
    group=db.IntegerProperty()#所属群
    title=db.StringProperty(indexed=False)
    content=db.TextProperty()#帖子内容
    author=db.StringProperty(default='000',indexed=False)#帖子作者
    updateTime=db.DateTimeProperty()#最后一次修改时间
    createTime=db.DateTimeProperty(auto_now_add=True)#创建时间
    isPub=db.BooleanProperty(default=False)#是否被删除

class HoTNote(db.Model):#热帖
    content=db.TextProperty()

class AdNote(db.Model):#广告贴
    content=db.StringProperty()#内容
    title=db.StringProperty()#链接
    imgid=db.IntegerProperty()#图片



class PaiMai(db.Model):
    maxpoint=db.IntegerProperty(indexed=False,default=0)
    user=db.StringProperty(indexed=False)
    adnote=db.StringProperty(indexed=False)
    updateTime=db.DateTimeProperty(auto_now=True,indexed=False)


class Replay(db.Model):# string id 和 Note一致
    group=db.IntegerProperty()#所属群
    content=db.TextProperty()#帖子内容json
    updateTime=db.DateTimeProperty()#最后一次修改时间

class Img(db.Model):# int id
    type=db.StringProperty(indexed=False,default='image/jpeg')
    afile=db.BlobProperty()
    src=db.StringProperty(indexed=False)

class MecacheNote(db.Model):
    content=db.TextProperty()
    