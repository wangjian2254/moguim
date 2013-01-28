#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from google.appengine.api import memcache
from im.model.models import User, UserPoint, GuPiaoNote

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
    images=xml.createElement('images')
    images.setAttribute('codeid','a777_id')
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
    img=xml.createElement('img')
    img.setAttribute('id','weekly%s'%imagestr)
    img.setAttribute('var',str(ver))
    group.appendChild(img)
    img=xml.createElement('img')
    img.setAttribute('id','monthly%s'%imagestr)
    img.setAttribute('var',str(ver))
    group.appendChild(img)
    return group