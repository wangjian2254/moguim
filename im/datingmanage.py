#coding=utf-8
#author:u'王健'
#Date: 12-11-27
#Time: 下午8:58
import logging
import re
import uuid
from google.appengine.api import memcache
from im.model.models import DaTingNote, Img
from groupinterfacemanage import getGroup
from google.appengine.ext import db
from google.appengine.api import images

import datetime
import setting

timezone=datetime.timedelta(hours =8)

__author__ = u'王健'
from tools.page import Page


class daTingNote(Page):
    def get(self):
#        username=get_current_user(self)
        grouplist=[]
        noteid=self.request.get('Noteid',0)
        note={}
        imglist=[]
        if noteid:
            note=DaTingNote.get_by_id(int(noteid))
            if note:
                imgstrlist=re.findall('(?i)templink/([^/\s\?&]*)/',note.content)

                for img in imgstrlist:
                    img=int(img)
                    imglist.append(img)
                imglist=Img.get_by_id(imglist)
                news, number = re.subn('[\*TempLink/([^/]*/[^\]]*]','', note.content)
                note.content=news
        msg=memcache.get(self.request.get('msgid',''))
        if not msg:
            msg=''
        self.render('templates/daTingNoteAdd.html',{'note':note,'imglist':imglist,'msg':msg})
    def post(self):
        msgid=''
        msg=u'添加大厅帖子成功'
        noteid=self.request.get('Noteid','')
        mod='add'
        if noteid:
            mod='update'
        username=u'000'
#        isTop=self.request.get("IsTop")
        content=self.request.get("NoteContent")
        title=self.request.get("NoteTitle")
        isPub=self.request.get("isPub")
        if isPub=='Y':
            isPub=True
        else:
            isPub=False
        groupid=self.request.get("GroupId")
        if not title or not content or not groupid:
            msgid=str(uuid.uuid4())
            memcache.set(msgid,u'标题、内容、群ID 必须填写',3600)
            self.redirect('/daTingNote?&msgid='+msgid)
            return
        noteupdate=datetime.datetime.utcnow()+timezone
        if groupid:
            try:
                groupid=int(groupid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        #判断用户是否具有发表帖子的权限
        #?
#        group=Group.get_by_id(groupid)
        group=getGroup(groupid)
        if group:


            if mod=='add':
                    note=DaTingNote()
            else:
                msg=u'修改帖子成功'
                note=DaTingNote.get_by_id(noteid)
            note.group=groupid
            note.author=username
            note.content=content
            note.title=title

            note.updateTime=noteupdate
            #####

            #####
            imgfield=self.request.POST.get('imgfile')
            if imgfield!=None and imgfield!='' and imgfield!=u'':
                if imgfield.type.lower() not in ['image/pjpeg','image/x-png','image/jpeg','image/png','image/gif','image/jpg']:
                    msgid=str(uuid.uuid4())
                    memcache.set(msgid,u'图片格式不合格',3600)
                    self.redirect('/CreateNoteM?Noteid='+str(noteid)+'&GroupId='+str(groupid)+'&msgid='+msgid)
                    logging.info(imgfield.type)
                    return
                imgstrlist=re.findall('(?i)templink/([^/\s\?&]*)/',note.content)
                imglist=[]
                for img in imgstrlist:
                    img=int(img)
                    imglist.append(img)
                imglist=Img.get_by_id(imglist)
                for img in imglist:
                    db.delete(img)
                imgfile=Img()
                imgfile.type=imgfield.type
                if imgfield.type.lower().find('gif')==-1:
                    imgfile.afile=db.Blob(images.resize(self.request.get("imgfile"), height=150))
                else:
                    imgfile.afile=self.request.get("imgfile")
                imgfile.put()
                note.content+="[*TempLink/%s/%s*]" %(imgfile.key().id(),setting.APPCODE_ID)
            note.isPub=isPub
            note.put()
            memcache.delete('hotnotlist')
            noteid=note.key().id()
            msgid=str(uuid.uuid4())
            memcache.set(msgid,msg,3600)
            self.redirect('/daTingNote?Noteid='+str(noteid)+'&msgid='+msgid)
        else:
            msgid=str(uuid.uuid4())
            memcache.set(msgid,u'群ID不对',3600)
            self.redirect('/daTingNote?Noteid='+str(noteid)+'&msgid='+msgid)
        return

class daTingNoteList(Page):
    def get(self):
        notelist=[]
        for note in DaTingNote.all():
            note.groupobj=getGroup(note.group)
            notelist.append(note)
        self.render('templates/daTingNoteList.html',{'datingNoteList':notelist})
        pass



class daTingNoteDel(Page):
    def get(self):
        datingNoteId=self.request.get('id')
        if datingNoteId:
            n=DaTingNote.get_by_id(int('id'))
            if n:
                n.delete()
                self.redirect('/daTingNoteList')
                return
        notelist=[]
        for note in DaTingNote.all():
            note.groupobj=getGroup(note.group)
            notelist.append(note)
        self.render('templates/daTingNoteList.html',{'datingNoteList':notelist})
        pass


  