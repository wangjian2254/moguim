#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
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