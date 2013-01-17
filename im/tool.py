#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from google.appengine.api import memcache
from im.model.models import User, UserPoint

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
