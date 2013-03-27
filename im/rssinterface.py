#coding=utf-8
#author:u'王健'
#Date: 12-7-11
#Time: 下午7:45
import datetime,time
import re
from model.models import Tag, Group, Img,  Replay, RssNote, RssImg
from google.appengine.ext import db
import setting

from google.appengine.api import memcache

timezone=datetime.timedelta(hours =8)

__author__ = u'王健'
from tool import getorAddUser
from tools.page import Page
import logging

#创建群
class SyncGroup(Page):
    def post(self):
        try:
            userName=self.request.get("UserName")
            user=getorAddUser(userName)
            groupName=self.request.get("GroupName")
            groupgonggao=self.request.get("GroupGonggao")
            groupId=self.request.get("GroupId",0)
            groupHead=self.request.get("GroupHead",0)
            groupAppType=self.request.get("GroupAppType",'0')
            type=self.request.get("GroupType")
            # rss群特殊对待
            type=3
            tagName=self.request.get("GroupTag")
            tagNameId=self.request.get("GroupTagId")
            if groupId:
                try:
                    groupId=int(groupId)
                except Exception,e:
                    logging.info(str(e))
                    self.response.out.write('0')
                    return
            if groupHead:
                try:
                    groupHead=int(groupHead)
                except Exception,e:
                    logging.info(str(e))
                    self.response.out.write('0')
                    return
            if tagName:
                tag=Tag.all().filter('name =',tagName).fetch(1)
                if len(tag)==1:
                    tagName=tag[0].key().id()
                else:
                    tag=Tag()
                    tag.name=tagName
                    tag.put()
                    tagName=tag.key().id()
            else:
                if tagNameId:
                    try:
                        tagName=int(tagNameId)
                    except :
                        tagName=None
                    if tagName:
                        tag=Tag.get_by_id(tagName)

            if userName and groupName and type:
                if groupId:
#                    group=Group.get_by_id(groupId)
                    group=memacheGroup(groupId)
                else:
                    group=None
                if not group:
                    group=Group()

                group.name=groupName
                group.author=userName
                group.gonggao=groupgonggao
                group.head=groupHead
                group.apptype=groupAppType
                group.notecount=30
                group.type=int(type)
                if tag:
                    group.tag=tagName
                group.put()
                user.createGroup.append(group.key().id())
                user.createGroup=list(set(user.createGroup))
                user.put()
                #self.response.out.write('0')
                self.response.out.write(str(group.key().id()))
            else:
                self.response.out.write('0')

        except Exception,e:
            logging.info(str(e))
            self.response.out.write('0')

class RssMsg(Page):
    def post(self):
        tmpimgid=int(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        notenum=self.request.get('notenum')
        logging.info('notenum:'+str(notenum))
        if notenum:
            notenum=int(notenum)
        else:
            notenum=0
        group=None
        groupchange=False
        rssnote=None
        rssnotelist=None
        rssimg=None
        rssimgdic=None

        for num in range(notenum):
            groupid=self.request.get(str(num)+'code')
    #        logging.info('code:'+groupid)
            title=self.request.get(str(num)+'title')
            content=self.request.get(str(num)+'content')
    #        logging.info('content:'+content)
            username=self.request.get(str(num)+'username')
    #        logging.info('username:'+username)
            lastnews=memcache.get('rsscode'+str(groupid))
            if not lastnews:
                lastnews=[]
                lastnews.insert(0,title)
                memcache.set('rsscode'+str(groupid),lastnews,360000)
            else:
                if title not in lastnews:
                    lastnews.insert(0,title)
                    lastnews=lastnews[:20]
                    memcache.set('rsscode'+str(groupid),lastnews,360000)
                else:
    #                logging.error('title:'+title)
    #                logging.error('titlelist:'+str(lastnews))
                    continue
            logging.info('rsscode'+str(groupid)+'rssMsg:'+title)

            if not rssimg:
                rssimg=memcache.get('rssimg'+str(groupid))
                if not rssimg:
                    rssimg=RssImg.get_by_key_name('rss'+str(groupid))
                if not rssimg:
                    rssimg=RssImg(key_name='rss'+str(groupid))
            if not rssimgdic:
                rssimgdic=rssimg.getImgDic()
            imgdic={}
            imglist=[]
            for i in range(20):
                imgsrc=self.request.get(str(num)+'img'+str(i))
                if imgsrc:
                    img='0%sG%s%s00%s'%(groupid,tmpimgid,num,i)
                    imgdic[img]=imgsrc
                    memcache.set('image_id'+str(img),imgsrc,3600*24*20)
#                    img=Img()
#                    img.src=imgsrc
                    imglist.append(img)
                else:
                    break

            if groupid and title and content:
                try:
                    groupid=int(groupid)
                except Exception,e :
                    logging.error('e1:'+str(e))
                    return

#                db.put(imglist)
                imgstr=''
                for img in imglist:
                    imgstr+= "[*TempLink/%s/%s*]" %(img,setting.APPCODE_ID)
#                    memcache.set('image_id'+str(img.key().id()),img,36000)

    #            group=Group.get_by_id(groupid)
                if not group:
                    group=memacheGroup(groupid)
                if not rssnote:
                    rssnote=RssNote.get_by_key_name('rss'+str(groupid))
                    if not rssnote:
                        rssnote=RssNote(key_name='rss'+str(groupid))
                        group.notenum=0
                        group.put()
                if not rssnotelist:
                    rssnotelist=rssnote.getNoteList()
                if group.notenum<group.notecount:
    #                note=Note()
                    note={'id':len(rssnotelist)+1,'isDelete':False,'isTop':False,'updateTime':None,'down':0,'up':0,'point':0,'author':'','content':'','title':'','group':0}
                    rssnotelist.append(note)
                else:
    #                note=Note.all().filter('group =',groupid).filter('isTop =',False).order('isDelete').order('updateTime').fetch(1)[0]
                    note=rssnotelist.pop(0)
                    rssnotelist.append(note)
                    if note['content']:
                        imgstrlist=re.findall('(?i)templink/([^/\s\?&]*)/',note['content'])
                        imglist=[]
                        for img in imgstrlist:
                            if img[0]=='0':
                                continue
                            img=int(img)
                            imglist.append(img)
                        imglist=Img.get_by_id(imglist)
                        db.delete(imglist)
    #                memcache.delete('replay'+str(groupid)+str(note['id']))
                    r=Replay.get_by_key_name('g'+str(groupid)+'r'+str(note['id']))
                    if r:
                        r.content=''
                        r.updateTime=datetime.datetime.utcnow()+timezone
                        r.put()
                note['group']=groupid
                note['author']=username
                note['content']=content+imgstr
                note['title']=title
                noteupdate=datetime.datetime.utcnow()+timezone
                note['updateTime']=time.mktime(noteupdate.timetuple())
                note['point']=0
                note['up']=0
                note['down']=0
                note['isTop']=False
                note['isDelete']=False
                if imgdic:
                    rssimgdic[str(note['id'])]=imgdic
                else:
                    if rssimgdic.has_key(str(note['id'])):
                        del rssimgdic[str(note['id'])]
                if not note['content']:
    #                logging.error('content:'+content[:20])
                    continue

                try:
                    memcache.set('rssgroupmemcach'+str(groupid),rssnotelist,3600)
                except :
                    logging.error('rss group note too big:'+str(len(rssnotelist)))
    #            logging.info('content：'+note.content[:20])
                if group.notenum<group.notecount:
                    group.notenum+=1
                    groupchange=True
        if group and groupchange:
            group.put()
        if rssimg and rssimgdic:
            rssimg.setImgDic(rssimgdic)
            rssimg.put()
            memcache.set('rssimg'+str(groupid),rssimg,3600*24*10)
        if rssnote and rssnotelist:
            rssnote.setNoteList(rssnotelist)
            rssnote.put()




def memacheGroup(groupid):
    group=memcache.get('groupbyid'+str(groupid))
    if not group:
        if '0000'==groupid:
            group=Group()
            group.name=u'大厅'
            return group
        groupid=int(groupid)
        if groupid:
            group=Group.get_by_id(int(groupid))
            memcache.set('groupbyid'+str(groupid),group,36000)
        else:
            return None
    return group