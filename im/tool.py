#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from xml.dom.minidom import Document
from google.appengine.api import memcache
from model.models import User, UserPoint, GuPiaoNote, NewRSSList
from tools.page import Page

__author__ = u'王健'

def getorAddUser(uname):
    user=User.get_by_key_name('u'+uname)
    if not user:
        user=User(key_name='u'+uname)
        user.put()
    return user

def getorAddUserPoint(uname):
    user=UserPoint.get_by_key_name('u'+uname)
    if not user:
        user=UserPoint(key_name='u'+uname)
        user.put()
    return user

def doUserPoint(uname,do,point):
    user=UserPoint.get_by_key_name('u'+uname)
    if not user:
        user=UserPoint(key_name='u'+uname)
    if do=='+':
        user.point+=point
    else:
        user.point-=point
    user.put()


#添加需要同步的股票群id
def addNeedSyncGuPiao(groupid):
    groupidhasmemcache=memcache.get('needsyncgupiao_groupidg%s'%groupid)
    if groupidhasmemcache:
        return
    needsyncgupiao=memcache.get('needsyncgupiao')
    if not needsyncgupiao:
        needsyncgupiao=set()
        memcache.set('needsyncgupiao',needsyncgupiao,3600)
    if str(groupid) not in needsyncgupiao:
        needsyncgupiao.add(str(groupid))
        memcache.set('needsyncgupiao',needsyncgupiao,3600)
        memcache.set('needsyncgupiao_groupidg%s'%groupid,'True',3600)


def getGuPiaoNote(groupid):
    guPiaoNote=memcache.get('gupiaonoteg'+groupid)
    if not guPiaoNote:
        guPiaoNote=GuPiaoNote.get_by_key_name('g'+groupid)
        memcache.set('gupiaonoteg'+groupid,guPiaoNote,36000)
    return guPiaoNote

def getGuPiaoImage(xml,datas):
    images=xml.createElement('imagesTemp')
    images.setAttribute('codeid','a777_1')
    images.setAttribute('code','a777')
    images.setAttribute('type','infoupdate')
    images.setAttribute('timespan',str(24*3600))
    datas.appendChild(images)
    lib=xml.createElement('lib')
    lib.setAttribute('name','sys')
    images.appendChild(lib)
    group=xml.createElement('group')
    group.setAttribute('name','001')
    group.setAttribute('text',u'股票图库')
    lib.appendChild(group)
    return group

def addGuPiaoImage(xml,datas,group,imagestr,ver):
    if not group:
        group=getGuPiaoImage(xml,datas)
    img=xml.createElement('img')
    img.setAttribute('id','min%s'%imagestr)
    img.setAttribute('var',str(ver))
    group.appendChild(img)
    img=xml.createElement('img')
    img.setAttribute('id','daily%s'%imagestr)
    img.setAttribute('var',str(ver))
    group.appendChild(img)
#    img=xml.createElement('img')
#    img.setAttribute('id','weekly%s'%imagestr)
#    img.setAttribute('var',str(ver))
#    group.appendChild(img)
#    img=xml.createElement('img')
#    img.setAttribute('id','monthly%s'%imagestr)
#    img.setAttribute('var',str(ver))
#    group.appendChild(img)
    return group


class Test(Page):
    def get(self):
        for chart in 'abcdefghijklmnopqrstuvwxyz':
            self.response.out.write(chart)
            self.response.out.write('</bar>')
            self.response.out.write('<img src="http://ichart.finance.yahoo.com/%s?s=601006.sz"/>'%chart)


def getNewRssList():
    newrsslist=memcache.get('newrsslist')
    if not newrsslist:
        newrsslist=NewRSSList.get_by_key_name('newrsslist')
        memcache.set('newrsslist',newrsslist,360000)
    return newrsslist


def queryWeiNoteXmlDic(contents,xml=None,datas=None,delete=None):
    if not xml:
        xml=Document()
        datas=xml.createElement('datas')
        #datas.setAttribute('time','%s' %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
#        datas.setAttribute('type','infoall')
        xml.appendChild(datas)
    for c in contents:
        if not c:
            continue
        data=xml.createElement('data')
        if not delete and c['status']=='1':
            data.setAttribute('code',c['code'] or '')
            data.setAttribute('father',c['father'] or '')
            if c.has_key('title'):
                data.setAttribute('title',c['title'] or '')
            if c.has_key('updateSpanTime'):
                data.setAttribute('updateSpanTime',c['updateSpanTime'] or '')
            if c.has_key('replyType'):
                data.setAttribute('replyType',c['replyType'] or '')
            data.setAttribute('maincode',c['maincode'] or '')
            data.setAttribute('level',c['level'] or '')
            data.appendChild(xml.createTextNode(c['content'] or ''))
            data.setAttribute('status',c['status'] or '')
            if c.has_key('lastUpdateTime'):
                data.setAttribute('lastUpdateTime',str(c['lastUpdateTime']) or '')
        else:
            if type(c) is str:
                data.setAttribute('code',c)
            else:
                data.setAttribute('code',c['code'] or '')
            data.setAttribute('status','0' or '')
        datas.appendChild(data)
    return (xml,datas)