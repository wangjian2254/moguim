#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
import re
import time
import uuid

from im.model.models import Tag, Group, Note, Replay, User, AdNote, Img,PaiMai
from im.tool import getorAddUser, getorAddUserPoint
import setting
from tools.page import Page
import json
from google.appengine.api import memcache
from xml.dom.minidom import Document
from google.appengine.ext import db
import logging
from google.appengine.api.images import Image
from google.appengine.api import images

from google.appengine.api import urlfetch
import urllib

__author__ = u'王健'

import datetime
timezone=datetime.timedelta(hours =8)

loginurl='/login'
def login_required(fn):
    def auth(*arg):
        web=arg[0]
        user=get_current_user(web)
        if user:
            arg=arg[1:]
            if len(arg)==0:
                fn(web)
            elif len(arg)==1:
                fn(web,arg[0])
            elif len(arg)==2:
                fn(web,arg[0],arg[1])
#            fn(web,arg)
        else:
#            web.redirect('/paper/234.html','post')
            if web.request.method=='GET':
                web.redirect(loginurl+'?fromurl='+web.request.path_url)
            else:
                web.redirect(loginurl+'?fromurl='+web.request.environ['HTTP_REFERER'])
    return auth



timezone=datetime.timedelta(hours =8)
groupReplayType='40'
noteReplayType='41'
replayReplayType='42'

def getAllTags():
    tagslist=memcache.get('alltags')
    if not tagslist:
        tagslist=[]
        for tag in Tag.all():
            tagslist.append({'id':tag.key().id(),'name':tag.name})
        memcache.set('alltags',tagslist,36000)
    return tagslist

class UserInfo(Page):
    def get(self):
        userName=self.request.get('UserName')
        user=User.get_by_key_name('u'+userName)
        if user:
            self.render('templates/userinfo.html',{'user':user})
        else:
            self.response.out.write(u'查无此人')
class GroupInfo(Page):
    def get(self):
        groupId=self.request.get('GroupId')
        if groupId:
            try:
                groupId=int(groupId)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
#        group=Group.get_by_id(groupId)
        group=getGroup(groupId)
        if group:
            msg=''
            msgid=self.request.get('msgid')
            if msgid:
                msg=memcache.get(msgid)
            self.render('templates/groupinfo.html',{'group':group,'taglist':Tag.all(),'msg':msg})
        else:
            self.response.out.write(u'查无此人')

class GroupListM(Page):
    def get(self):
        self.post()
    def post(self):
        tagmap={}
        for tag in Tag.all():
            tagmap[str(tag.key().id())]=tag.name
        username=get_current_user(self)
        if '000'==username:
            type=self.request.get('type','')
            value=self.request.get('value',0)
            list=[]
            if type=='username':
                list=Group.all().filter('author =',str(value))
            if type=='groupid':
                list=Group.get_by_id([int(value)])
        else:
            list=Group.all().filter('author =',username)
        listgroup=[]
        for group in list:
            group.tagname=tagmap[str(group.tag)]
            listgroup.append(group)
        self.render('templates/groupList.html',{'list':listgroup,'tagmap':tagmap,'isadmin':('000'==username and [True] or [False])[0]})
class RemoveGroupM(Page):
    @login_required
    def get(self):
        groupid=self.request.get('groupid')
        tagmap={}
        for tag in Tag.all():
            tagmap[str(tag.key().id())]=tag.name

        username=get_current_user(self)
        user=getorAddUser(username)
        if groupid:
            groupid=int(groupid)
#            group=Group.get_by_id(groupid)
            group=getGroup(groupid)
            if group.author==username:
                group.delete()
                nlist=[]
                rnlist=[]
                for n in Note.all().filter('group =',groupid):
                    nlist.append(n)
                    rnlist.append('r'+str(n.key().id()))
                db.delete(Replay.get_by_key_name(rnlist))
                db.delete(nlist)
                if groupid in user.createGroup:
                    user.createGroup.remove(groupid)
                    user.put()
                if groupid in user.createGroupAdd:
                    user.createGroupAdd.remove(groupid)
                    user.put()


        groupidlist=user.createGroup+user.createGroupAdd
        list=Group.get_by_id(groupidlist)
#        list=Group.all().filter('author =',username)
        listgroup=[]
        ischange=False
        for i,group in enumerate(list):
            if not group:
                if groupidlist[i] in user.createGroup:
                    user.createGroup.remove(groupidlist[i])
                    ischange=True
                if groupidlist[i] in user.createGroupAdd:
                    user.createGroupAdd.remove(groupidlist[i])
                    ischange=True
            else:
                group.tagname=tagmap[str(group.tag)]
                listgroup.append(group)
        if ischange:
            user.put()
        self.render('templates/removegroupList.html',{'list':listgroup})
    @login_required
    def post(self):
        pass
#创建群
class CreateGroupM(Page):
    @login_required
    def get(self):
        groupId=self.request.get("GroupId",0)
#        username=
        group={}
        if groupId:
#            group=Group.get_by_id(int(groupId))
            group=getGroup(int(groupId))
        self.render('templates/groupAdd.html',{'group':group,'taglist':Tag.all()})
    @login_required
    def post(self):
        try:
            userName=get_current_user(self)
            user=getorAddUser(userName)
            groupName=self.request.get("GroupName")
            groupgonggao=self.request.get("GroupGonggao")
            groupId=self.request.get("GroupId",0)
            groupHead=self.request.get("GroupHead",0)
            type=self.request.get("GroupType")
            tagName=self.request.get("GroupTag")
            tagNameId=self.request.get("GroupTagId")
            if groupId:
                try:
                    groupId=int(groupId)
                except Exception,e:
                    logging.info(str(e))
                    self.response.out.write('1')
                    return
            if groupHead:
                try:
                    groupHead=int(groupHead)
                except Exception,e:
                    logging.info(str(e))
                    self.response.out.write('1')
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
                msg=u'创建群成功。'
                if groupId:
#                    group=Group.get_by_id(groupId)
                    group=getGroup(groupId)
                    msg=u'修改群信息成功。'
                else:
                    group=None
#                group=Group.get_by_id(groupId)
                if not group:
                    num=len(user.createGroup)+len(user.createGroupAdd)
                    user.createGroup=list(set(user.createGroup))
                    user.createGroupAdd=list(set(user.createGroupAdd)-set(user.createGroup))
                    if (len(user.createGroup)+len(user.createGroupAdd))!=num:
                        user.put()
                    if '000'==userName or len(user.createGroupAdd)+len(user.createGroup)<2:
                        group=Group()
                    else:
                        self.render('templates/groupAdd.html',{'group':{},'taglist':Tag.all(),'message':u'每人只能创建两个群。'})

                group.name=groupName[:500]
                group.author=userName
                group.gonggao=groupgonggao[:500]
                group.head=groupHead
                group.type=int(type)
                if tag:
                    group.tag=tagName
                group.put()
                user.createGroupAdd.append(group.key().id())
                user.put()
                #self.response.out.write('0')
                msgid=str(uuid.uuid4())

                memcache.set(msgid,msg,3600)
                self.redirect('/groupinfo?GroupId='+str(group.key().id())+'&msgid='+msgid)
            else:
                self.response.out.write(u'信息不全')

        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')


#参加、退出群
class JoinGroup(Page):
    def post(self):
        try:
            userName=self.request.get("TheUserName")
            user=getorAddUser(userName)
            groupId=self.request.get("GroupId")
            if groupId:
                try:
                    groupId=int(groupId)
                except Exception,e:
                    logging.info(str(e))
                    self.response.out.write('1')
                    return
            type=self.request.get("DoType")# 1:作为参与着加入 2：作为参与者退出 3：作为群主加入 4：作为群主退出 5:参与者升为群主 6：群主将为参与者
            if groupId and type:
#                group=Group.get_by_id(groupId)
                group=getGroup(groupId)
                if type=='1':
                    if userName not in group.member:
                        group.member.append(userName)
                    if group.key().id() not in user.memberGroup:
                        if group.key().id() not in user.memberGroupAdd:
                            user.memberGroupAdd.append(group.key().id())
                            if group.key().id() in user.memberGroupRemove:
                                user.memberGroupRemove.remove(group.key().id())
                if type=='2':
                    if userName in group.member:
                        group.member.remove(userName)
                    if group.key().id() in user.memberGroup:
                        gid=user.memberGroup.remove(group.key().id())
                        if group.key().id() not in user.memberGroupRemove:
                            user.memberGroupRemove.append(gid)
                            if gid in user.memberGroupAdd:
                                user.memberGroupAdd.remove(gid)

                    pass
                if type=='3':
                    if userName not in group.partner:
                        group.partner.append(userName)
                    if group.key().id() not in user.partnerGroup:
                        if group.key().id() not in user.partnerGroupAdd:
                            user.partnerGroupAdd.append(group.key().id())
                            if group.key().id() in user.partnerGroupRemove:
                                user.partnerGroupRemove.remove(group.key().id())
                if type=='4':
                    if userName in group.partner:
                        group.partner.remove(userName)
                    if group.key().id() in user.partnerGroup:
                        gid=user.partnerGroup.remove(group.key().id())
                        if group.key().id() not in user.partnerGroupRemove:
                            user.partnerGroupRemove.append(gid)
                            if gid in user.partnerGroupAdd:
                                user.partnerGroupAdd.remove(gid)
                if type=='5':
                    if userName in group.member:
                        group.member.remove(userName)
                        if userName not in group.partner:
                            group.partner.append(userName)
                    if groupId in user.memberGroup or groupId in user.memberGroupAdd or groupId in user.memberGroupRemove:
                        user.memberGroup.remove(groupId)
                        user.memberGroupAdd.remove(groupId)
                        user.memberGroupRemove.remove(groupId)
                        if groupId not in user.partnerGroup:
                            if groupId not in user.partnerGroupAdd:
                                user.partnerGroupAdd.append(groupId)
                                if groupId in user.partnerGroupRemove:
                                    user.partnerGroupRemove.remove(groupId)
                if type=='6':
                    if userName in group.partner:
                        group.partner.remove(userName)
                        if userName not in group.member:
                            group.member.append(userName)
                    if groupId in user.partnerGroup or groupId in user.partnerGroupAdd or groupId in user.partnerGroupRemove:
                        user.partnerGroup.remove(groupId)
                        user.partnerGroupAdd.remove(groupId)
                        user.partnerGroupRemove.remove(groupId)
                        if groupId not in user.memberGroup:
                            if groupId not in user.memberGroupAdd:
                                user.memberGroupAdd.append(groupId)
                                if groupId in user.memberGroupRemove:
                                    user.memberGroupRemove.remove(groupId)
                group.put()
                user.put()
#                self.response.out.write('0')
                self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
            else:
                self.response.out.write('2')
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')
#查找群
class SearchGroup(Page):
    def post(self):
        groupid=self.request.get("GroupId")
        tagid=self.request.get("TagId")
        page=self.request.get("page") or 0
        l=[]
        if groupid:
            try:
                groupid=int(groupid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
#            group=Group.get_by_id(int(groupid))
            group=getGroup(int(groupid))
            l=[groupToMap(group)]
        if tagid:
            try:
                tagid=int(tagid)
                page=int(page)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
            grouplist=Group.all().filter('tag =',tagid).fetch(20,page*20)
            for g in grouplist:
                l.append(groupToMap(g))
        self.response.out.write(json.dumps([l]))
class NoteListM(Page):
    def get(self):
        self.post()
    def post(self):
        """

        """
        username=get_current_user(self)
        if '000'==username:
            type=self.request.get('type','')
            value=self.request.get('value',0)
            list=[]
            if type=='username':
                list=Note.all().filter('author =',str(value))
            if type=='groupid':
                list=Note.all().filter('group =',int(value)).order('-isTop').order('-updateTime')
            if type=='noteid':
                list=Note.get_by_id([int(value)])
        else:
            type=self.request.get('type','')
            value=self.request.get('value',0)
            list=[]
            if type=='username':
                list=Note.all().filter('author =',str(value))
            if type=='groupid':
                list=Note.all().filter('group =',int(value)).order('-isTop').order('-updateTime')
            if not type and not value:
                groupids=[]
                for g in Group.all().filter('author =',username):
                    groupids.append(g.key().id())
                list=Note.all().filter('group in',groupids).filter('isDelete =',False).order('-updateTime')
        notelist=[]
        for note in list:
            note.groupobj=getGroup(note.group)
            notelist.append(note)
        self.render('templates/noteList.html',{'list':notelist,'isadmin':('000'==username and [True] or [False])[0]})
#发帖、修改
class CreateNoteM(Page):
    def get(self):
        username=get_current_user(self)
        grouplist=[]
        noteid=self.request.get('Noteid',0)
        note={}
        imglist=[]
        if noteid:
            note=Note.get_by_id(int(noteid))
            if note:
                imgstrlist=re.findall('(?i)templink/([^/\s\?&]*)/',note.content)

                for img in imgstrlist:
                    img=int(img)
                    imglist.append(img)
                imglist=Img.get_by_id(imglist)
                news, number = re.subn('[\*TempLink/([^/]*/[^\]]*]','', note.content)
                note.content=news
        groupid=self.request.get('GroupId')
        if note:
            groupid=note.group
        group=None
        if groupid:
#            group=Group.get_by_id(int(groupid))
            group=getGroup(int(groupid))
        if not group:
            if '000'==username:
                self.redirect('/GroupListM')
                return
            else:
                for g in Group.all().filter('author =',username):
                    grouplist.append(g)

        msg=memcache.get(self.request.get('msgid',''))
        if not msg:
            msg=''
        self.render('templates/noteAdd.html',{'group':group,'grouplist':grouplist,'note':note,'imglist':imglist,'msg':msg})
    def post(self):
        msgid=''
        msg=u'添加帖子成功'
        noteid=self.request.get('Noteid','')
        mod='add'
        if noteid:
            mod='update'
        username=get_current_user(self)
#        isTop=self.request.get("IsTop")
        content=self.request.get("NoteContent")
        title=self.request.get("NoteTitle")
        groupid=self.request.get("GroupId")
        if not title or not content:
            msgid=str(uuid.uuid4())
            memcache.set(msgid,u'请填写标题和内容',3600)
            self.redirect('/CreateNoteM?GroupId='+str(groupid)+'&msgid='+msgid)
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

            if group.type==1:
                if username not in group.partner and username!=group.author:
                    self.response.out.write('2')
                    return
            elif group.type==2:
                if username!=group.author and username!=note.author:
                    self.response.out.write('2')
                    return
            if mod=='add':

                if group.notenum<group.notecount:
                    note=Note()
                else:
                    note=Note.all().filter('group =',groupid).filter('isTop =',False).order('isDelete').order('updateTime').fetch(1)[0]
                    r=Replay.get_by_key_name('r'+str(note.key().id()))
                    if r:
                        r.content=''
                        r.updateTime=noteupdate
                        r.put()
            else:
                msg=u'修改帖子成功'
                note=Note.get_by_id(noteid)
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
                db.delete(imglist)
#                    raise 'type error'
#                imgdb=imgfield.file.read()

#                img=Image(imgdb)
                imgfile=Img()
                imgfile.type=imgfield.type
                if imgfield.type.lower().find('gif')==-1:
                    imgfile.afile=db.Blob(images.resize(self.request.get("imgfile"), height=150))
                else:
                    imgfile.afile=self.request.get("imgfile")
                imgfile.put()
                note.content+="[*TempLink/%s/%s*]" %(imgfile.key().id(),setting.APPCODE_ID)

            note.put()
            noteid=note.key().id()
            if group.notenum<group.notecount:
                group.notenum+=1
                group.put()
            msgid=str(uuid.uuid4())
            memcache.set(msgid,msg,3600)
            self.redirect('/CreateNoteM?Noteid='+str(noteid)+'&GroupId='+str(groupid)+'&msgid='+msgid)
        else:
            self.response.out.write('3')
        return

class DelNoteImgM(Page):
    def get(self):
        noteid=self.request.get('Noteid')
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
#        username=self.request.get("UserName")
        note=Note.get_by_id(noteid)
        if note:
            imgid=self.request.get('image_id','0')
            imgid=int(imgid)
            img=Img.get_by_id(imgid)
            if img:
                img.delete()
            note.content=note.content.replace("[*TempLink/%s/%s*]" %(imgid,setting.APPCODE_ID),'')
            note.put()
            self.redirect('/CreateNoteM?Noteid='+str(noteid))
        else:
            self.redirect('/GroupListM')


#删除帖子
class DelNoteM(Page):
    def get(self):
        self.post()
    def post(self):
        noteid=self.request.get('Noteid')
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
#        username=self.request.get("UserName")
        note=Note.get_by_id(noteid)
        if note:
#            group=Group.get_by_id(note.group)
            group=getGroup(note.group)
            if group:
#                if group.type==1:
#                    if username not in group.partner and username!=group.author:
#                        self.response.out.write('2')
#                        return
#                elif group.type==2:
#                    if username!=group.author and username!=note.author:
#                        self.response.out.write('2')
#                        return
                note.updateTime=datetime.datetime.utcnow()+timezone
                note.isDelete=True;
                note.put()
                imgstrlist=re.findall('(?i)templink/([^/\s\?&]*)/',note.content)
                imglist=[]
                for img in imgstrlist:
                    img=int(img)
                    imglist.append(img)
                imglist=Img.get_by_id(imglist)
                db.delete(imglist)
                memcache.delete('note'+str(noteid))
                group.notenum-=1
                replay=Replay.get_by_key_name('r'+str(noteid))
                if replay:
                    replay.delete()
                self.redirect('/NoteListM?type=groupid&value='+str(note.group))
                return
#                self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
            else:
                replay=Replay.get_by_key_name('r'+str(noteid))
                if replay:
                    replay.delete()
                note.delete()
                self.redirect('/GroupListM')
                return
#                self.response.out.write('3')
        else:
            self.response.out.write('1')

#评论帖子
class PutReplay(Page):
    def post(self):
        username=self.request.get("UserName")
        noteid=self.request.get('Noteid')
        content=self.request.get("ReplayContent")
        date=datetime.datetime.utcnow()+timezone
        timeline=time.mktime(date.timetuple())
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        note=Note.get_by_id(noteid)
        if note:
            replay=Replay.get_by_key_name('r'+str(noteid))
            if not replay:
                replay=Replay(key_name='r'+str(noteid))
                replay.group=note.group
            replay.updateTime=date
            if not replay.content:
                replaymap=[]
            else:
                replaymap=json.loads(replay.content)
            if len(replaymap)>0:
                index=replaymap[-1]['index']+1
            else:
                index=1
            replaymap.append({'index':index,'username':username,'nickname':getNickName(username),'content':content,'datetime':timeline})
            replay.content=json.dumps(replaymap[-100:])
            replay.put()
            self.response.out.write('0'+str(index))
        else:
            self.response.out.write('1')

#踩顶帖子
class DoNote(Page):
    def post(self):
        noteid=self.request.get('Noteid')
        mod=self.request.get('DoMod')
        username=self.request.get("UserName")
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        note=Note.get_by_id(noteid)
        if note and note.isDelete==False:
            if mod=='up':
                note.point+=1
                note.up+=1
            elif mod=='down':
                note.point-=1
                note.down+=1
            else:
                self.response.out.write('0')
                return
            note.updateTime=datetime.datetime.utcnow()+timezone
            note.put()
            self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
        else:
            self.response.out.write('1')
            return
#设置、取消 置顶帖子
class TopNoteM(Page):
    def get(self):
        self.post()
    def post(self):
        noteid=self.request.get('Noteid')
        mod=self.request.get('DoMod')
#        username=self.request.get("UserName")
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        note=Note.get_by_id(noteid)
        if note and note.isDelete==False:
#            group=Group.get_by_id(note.group)
            group=getGroup(note.group)
            if group:
                if group.type==1:
#                    if username not in group.partner and username!=group.author:
#                        self.response.out.write('1')
#                        return
                    if mod=='do':
                        note.isTop=True
                    else:
                        note.isTop=False
                    note.updateTime=datetime.datetime.utcnow()+timezone
                    note.put()
                    self.redirect('/NoteListM?type=groupid&value='+str(note.group))
                    return
        self.response.out.write('1')
        return


#竞拍广告贴
class PutAdNote(Page):
    @login_required
    def get(self):
        username=get_current_user(self)
        imglist=[]
        note=AdNote.get_by_key_name('u'+username)
#        note=Note.get_by_id(int(noteid))
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
        self.render('templates/adNoteShow.html',{'adnote':note,'username':username,'user':getorAddUser(username),'imglist':imglist,'msg':msg})

    @login_required
    def post(self):
        try:
            msgid=''
            username=get_current_user(self)
            note=AdNote.get_by_key_name('u'+username)
            if not note:
                note=AdNote(key_name='u'+username)
            else:
                img=Img.get_by_id(note.imgid)
                if img:
                    img.delete()

#            note.group=groupid
            note.author=username
            note.content=self.request.get('NoteContent','')
            note.title=self.request.get('NoteTitle','')

#            note.updateTime=noteupdate
            imgfield=self.request.POST.get('imgfile')
            if imgfield!=None and imgfield!='' and imgfield!=u'':

                if imgfield.type.lower() not in ['image/pjpeg','image/x-png','image/jpeg','image/png','image/gif','image/jpg']:
                    msgid=str(uuid.uuid4())
                    memcache.set(msgid,u'图片格式不合格',3600)
                    self.redirect('/PutAdNote?msgid='+msgid)
                    logging.info(imgfield.type)
                    return
#                    raise 'type error'
                imgfile=Img()
                imgfile.type=imgfield.type
                if imgfield.type.lower().find('gif')==-1:
                    imgfile.afile=db.Blob(images.resize(self.request.get("imgfile"), height=150))
                else:
                    imgfile.afile=self.request.get("imgfile")
#                imgfile.afile=db.Blob(images.resize(self.request.get("imgfile"), height=150))
                imgfile.put()
                note.imgid=imgfile.key().id()
                note.content+="[*TempLink/%s/%s*]" %(imgfile.key().id(),setting.APPCODE_ID)
            note.put()

        except Exception,e:
            logging.error(str(e))
            pass
        self.redirect('/PutAdNote?msgid='+msgid)
def jingpaiDate():
    pl=PaiMai.all().order('-__key__').fetch(1)
    pm=None
    if 1==len(pl):
        pm=pl[0]
        lasttime=datetime.datetime.strptime(pm.key().name()[1:],'%Y%m%d')
        nowdate=datetime.datetime.strptime((datetime.datetime.utcnow()+datetime.timedelta(hours =8)).strftime("%Y%m%d"),'%Y%m%d')
        #1.lasttime 小于 当前日期
        while nowdate>lasttime:
            lasttime=lasttime+datetime.timedelta(hours =24*7)
        #2.lasttime 大于 当前日期
        lasttimestr=lasttime.strftime("%Y%m%d")
        return lasttimestr
    elif 0==len(pl):
        return setting.AdNoteTime
class JingPai(Page):

    @login_required
    def get(self):
        username=get_current_user(self)
        lasttimestr=jingpaiDate()
        starttime=datetime.datetime.strptime(lasttimestr,'%Y%m%d')
        endtime=starttime+datetime.timedelta(hours =24*7)-+datetime.timedelta(minutes =1)
        pl=PaiMai.all().order('-__key__').fetch(1)
        pm=None
        if 1==len(pl):
            pm=pl[0]
            if lasttimestr!=pm.key().name()[1:]:
                pm=None
        adnote=None
        if pm:
            adnote=AdNote.get_by_key_name('u'+pm.user)
        msgid=self.request.get('msg')
        msg=None
        if msgid:
            msg=memcache.get(msgid)

        self.render('templates/jingpai.html',{'username':username,'starttime':starttime,'endtime':endtime,'paimai':pm,'adnote':adnote,'userpoint':getorAddUserPoint(username),'msg':msg})
    @login_required
    def post(self):
        msgid=''
        try:
            point=int(self.request.get('point','0'))
            username=get_current_user(self)
            user=getorAddUserPoint(username)
            msg=u'竞拍成功。'
            if point>user.point:
                msg=u'竞拍失败，积分不足。'
            else:
                pl=PaiMai.all().order('-__key__').fetch(1)
                pm=None
                if 1==len(pl):
                    pm=pl[0]
                    lasttimestr=jingpaiDate()
                    if lasttimestr!=pm.key().name()[1:]:
                        pm=PaiMai(key_name='p'+lasttimestr)
                        memcache.delete('adnote')
                elif 0==len(pl):
                    pm=PaiMai(key_name='p'+ setting.AdNoteTime)
                    memcache.delete('adnote')
                if pm.maxpoint<point:
                    pm.maxpoint=point
                    pm.user=username
                    pm.put()
                else:
                    msg=u'竞拍失败，使用积分少于 当前竞拍最高分 。'
            msgid=str(uuid.uuid4())
            memcache.set(msgid,msg,3600)
        except :
            pass
        self.redirect('/JingPai?msg='+msgid)
        return





#datestr=datetime.datetime.now().strftime("%Y%m%d")
#datetime.datetime.strptime(datestart,'%Y%m%d')+datetime.timedelta(hours =24)

#处理广告竞拍结果
class DoingAdNote(Page):
    def get(self):
        pass


def groupToMap(group):
    if group:
        return {'groupid':group.key().id(),'name':group.name,'head':group.head or 0,'tagid':group.tag,'tagname':getTagName(group.tag),'gonggao':group.gonggao or '','author':group.author,'nickname':getNickName(group.author),'partner':group.partner,'member':group.member,'type':group.type}
    else:
        return None

def noteToMap(note):
    if note:
        return {'noteid':note.key().id(),'group':note.group,'title':note.title,'content':note.content,'author':note.author,'nickname':getNickName(note.author),'point':note.point,'up':note.up,'down':note.down,'updateTime':str(note.updateTime),'isTop':note.isTop}
    else:
        return None
def getGroup(groupid):
    group=memcache.get('groupbyid'+str(groupid))
    if group:
        return group
    else:
        group=Group.get_by_id(groupid)
        memcache.set('groupbyid'+str(groupid),group,3600)
        return group
def getTagName(id):
    name=memcache.get('tag'+str(id))
    if name:
        return name
    else:
        name=Tag.get_by_id(id)
        if name:
            name=name.name
            memcache.set('tag'+str(id),name,3600)
            return name
        else:
            return ''

def getNickName(id):
    name=memcache.get('nick'+str(id))
    if name:
        return name
    else:
        name=User.get_by_key_name('u'+str(id))
        if name:
            name=name.nickname
            memcache.set('nick'+str(id),name,3600)
            return name
        else:
            return ''






def setLogin(web,username):
    uid=str(uuid.uuid4())
    memcache.set('webusername'+uid,username,36000)
    setCookie='webusername='+uid+';'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')

def setLogout(web):
    setCookie='webusername=;'
    web.response.headers.add_header('Set-Cookie', setCookie+'Max-Age = 3600000;path=/;')

def get_current_user(web):
    guist={}
    Cookies = {}  # tempBook Cookies
    Cookies['request_cookie_list'] = [{'key': cookie_key, 'value': cookie_value} for cookie_key, cookie_value in web.request.cookies.iteritems()]
    for c in Cookies['request_cookie_list']:
        if c['key']=='webusername':
                    guist["username"]=memcache.get('webusername'+c['value'])
        if c['key']=='webnickname':
                    guist["name"]=urllib.unquote(c['value'].encode("utf-8"))
        if c['key']=='auth':
                    guist["auth"]=c['value']
    if guist and guist.has_key('username') and guist['username']:
        user=memcache.get('userlogin'+guist['username'])
        if not user:
            user=getorAddUser(guist['username'])
            user=guist['username']
            memcache.get('userlogin'+guist['username'],user,36000)
        if user:
            return user
    return False









class Login(Page):
    def get(self, *args):
        fromurl=self.request.get('fromurl','/')
        self.render('templates/login.html', {'fromurl':fromurl})

    def post(self, *args):
        username=self.request.get('username')
        password=self.request.get('password')
#        pam={}
#        pam['UserName']=username
#        pam['UserPwd']=password
        login_url = setting.HOMEURL +'/UserLogin?UserName='+username+'&UserPwd='+password
#        login_data = urllib.urlencode(pam)
        result = urlfetch.fetch(
        url = login_url,
#        payload = login_data,
        method = urlfetch.GET,
        headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
        follow_redirects = False,deadline=10)
        if result.status_code == 200:
            c=result.content
            if '1'==c:
                setLogin(self,username)
                self.render('templates/workframe.html', {})
            if '3'==c:
                self.redirect('/')

        else:
            self.redirect('/')
            logging.error('send news failure !')
            return

class Top(Page):
  @login_required
  def get(self):
      username=get_current_user(self)
      self.render('templates/topnav.html',{'username':username,'user':getorAddUser(username),'userpoint':getorAddUserPoint(username)})
class Menu(Page):
  @login_required
  def get(self):
      self.render('templates/menu.html',{})

