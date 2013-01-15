#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

import pickle
import time
import uuid

from im.model.models import Tag, Group, Note, Replay, User, MecacheNote, Img, HoTNote, AdNote, RssNote, RssImg, DaTingNote, PaiMai
from im.tool import getorAddUser, doUserPoint
import setting
from tools.page import Page
import json
from google.appengine.api import memcache
from xml.dom.minidom import Document
from google.appengine.ext import db
import logging

__author__ = u'王健'

import datetime
timezone=datetime.timedelta(hours =8)
groupReplayType='40'
noteReplayType='41'
replayReplayType='42'

class UserInfo(Page):
    def get(self):
        userName=self.request.get('UserName')
        user=User.get_by_key_name('u'+userName)
        if user:
            self.render('templates/userinfo.html',{'user':user})
        else:
            self.response.out.write(u'查无此人')


#创建群
class CreateGroup(Page):
    def post(self):
        try:
            userName=self.request.get("UserName")
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
                if groupId:
#                    group=Group.get_by_id(groupId)
                    group=memacheGroup(groupId)
                else:
                    group=None
#                group=Group.get_by_id(groupId)
                if not group:
                    if len(user.createGroupAdd)+len(user.createGroup)<2:
                        group=Group()
                    else:
                        self.response.out.write('2')

                group.name=groupName
                group.author=userName
                group.gonggao=groupgonggao
                group.head=groupHead
                group.type=int(type)
                if tag:
                    group.tag=tagName
                group.put()
                user.createGroupAdd.append(group.key().id())
                user.put()
                #self.response.out.write('0')
                self.response.out.write(setting.WEBURL[7:]+'/InfoAll')
            else:
                self.response.out.write('1')

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
                group=memacheGroup(groupId)
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
                        user.memberGroup.remove(group.key().id())
                        if group.key().id() not in user.memberGroupRemove:
                            user.memberGroupRemove.append(group.key().id())
                            if group.key().id() in user.memberGroupAdd:
                                user.memberGroupAdd.remove(group.key().id())

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
                        user.partnerGroup.remove(group.key().id())
                        if group.key().id() not in user.partnerGroupRemove:
                            user.partnerGroupRemove.append(group.key().id())
                            if group.key().id() in user.partnerGroupAdd:
                                user.partnerGroupAdd.remove(group.key().id())
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


#生成RSSjson
class Rssjson(Page):
    def get(self):
        self.render('templates/rssjson.html',{})
    def post(self):
        rssids=self.request.get('rssid','')
        rssidarr=rssids.split(',')
        rssidlist=[]
        for rssid in rssidarr:
            rssidlist.append(int(rssid))
        l=[]
        grouplist=Group.get_by_id(rssidlist)
        for group in grouplist:
            if group:
                l.append(groupToMap(group))
        self.response.out.write(json.dumps(l))
#查找群
class SearchGroup(Page):
    def post(self):
        groupid=self.request.get("GroupId")
        tagid=self.request.get("TagId")
        tagname=self.request.get("Tagname")
        page=self.request.get("page") or 0
        logging.info('tagid:'+str(tagid))
        logging.info('Tagname:'+tagname)
        l=[]
        if groupid:
            try:
                groupid=int(groupid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
#            group=Group.get_by_id(int(groupid))
            group=memacheGroup(groupid)
            if group:
                l.append(groupToMap(group))
            self.response.out.write(json.dumps(l))
            return
        if tagname:
            tagset=memcache.get('tagnameset')
            if not tagset:
                tagset=set()
                for t in Tag.all():
                    tagset.add((t.key().id(),t.name))
                memcache.set('tagnameset',tagset,36000)
            i=0
            logging.info(str(tagset))
            for s,n in tagset:
                if n.find(tagname)>-1:
                    tagid=s
                i=s
            if not tagid:
                tagid=i

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
        if not tagname and not tagid:
            grouplist=Group.all().order('-__key__').fetch(20)
            for g in grouplist:
                l.append(groupToMap(g))
        self.response.out.write(json.dumps(l))

#发帖、修改
class CreateNote(Page):
    def post(self):
        noteid=self.request.get('Noteid')
        mod='add'
        if noteid:
            mod='update'
        username=self.request.get("UserName")
#        isTop=self.request.get("IsTop")
        content=self.request.get("NoteContent")
        title=self.request.get("NoteTitle")
        groupid=self.request.get("GroupId")
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
        group=memacheGroup(groupid)
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
                    r=Replay.get_by_key_name('g'+str(groupid)+'r'+str(note.key().id()))
                    if r:
                        r.content=''
                        r.updateTime=noteupdate
                        r.put()
            else:
                note=Note.get_by_id(noteid)
            note.group=groupid
            note.author=username
            note.content=content
            note.title=title
            note.updateTime=noteupdate
            note.put()
            if group.notenum<group.notecount:
                group.notenum+=1
                group.put()
            self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
        else:
            self.response.out.write('3')
        return


#        noteid=self.
#删除帖子
class DelNote(Page):
    def post(self):
        noteid=self.request.get('Noteid')
        if noteid:
            try:
                noteid=int(noteid)
            except Exception,e:
                logging.info(str(e))
                self.response.out.write('1')
                return
        username=self.request.get("UserName")
        note=Note.get_by_id(noteid)
        if note:
#            group=Group.get_by_id(note.group)
            group=memacheGroup(note.group)
            if group:
                if group.type==1:
                    if username not in group.partner and username!=group.author:
                        self.response.out.write('2')
                        return
                elif group.type==2:
                    if username!=group.author and username!=note.author:
                        self.response.out.write('2')
                        return
                note.updateTime=datetime.datetime.utcnow()+timezone
                note.isDelete=True;
                note.put()
                group.notenum-=1
                replay=Replay.get_by_key_name('g'+str(group.key().id())+'r'+str(noteid))
                if replay:
                    replay.delete()
                self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
            else:
                replay=Replay.get_by_key_name('g'+str(group.key().id())+'r'+str(noteid))
                if replay:
                    replay.delete()
                note.delete()
                self.response.out.write('3')
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
            replay=Replay.get_by_key_name('g'+str(note.group)+'r'+str(noteid))
            if not replay:
                replay=Replay(key_name='g'+str(note.group)+'r'+str(noteid))
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
            hasdo=memcache.get('u'+username+'donote'+str(noteid))#标记用户是否进行过操作
            if not hasdo:
                if note.point%100==1 and note.point/100>0:
                    if mod=='down':
                        doUserPoint(username,'-',1)
                elif note.point%100==99:
                    if mod=='up':
                        doUserPoint(username,'+',1)
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
            else:
                memcache.set('u'+username+'donote'+str(noteid),True,36000*24)
            self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
        else:
            self.response.out.write('1')
            return
#设置、取消 置顶帖子
class TopNote(Page):
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
#            group=Group.get_by_id(note.group)
            group=memacheGroup(note.group)
            if group:
                if group.type==1:
                    if username not in group.partner and username!=group.author:
                        self.response.out.write('1')
                        return
                    if mod=='do':
                        note.isTop=True
#                        addDTNote(note.key().id())
                    else:
                        note.isTop=False
#                        delDTNote(note.key().id())
                    note.updateTime=datetime.datetime.utcnow()+timezone
                    note.put()
                    self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
                    return
        self.response.out.write('1')
        return
#def getDTNote():
#    m=memcache.get('DTNoteList')
#    if not m:
#        m=DTNote.get_by_key_name('note')
#    if not m:
#        m=DTNote(key_name='note')
#        m.content=json.dumps({'notelist':{},'noteset':set()})
#        m.put()
#    return m
#def addDTNote(noteid):
#    m=getDTNote()
#    dtnote=json.loads(m.content)
#    if noteid not in dtnote['noteset']:
#        dtnote['notelist'].append((noteid,time.mktime((datetime.datetime.utcnow()+timezone).timetuple())))
#        m.content=json.loads(notelist[-100:])
#        saveDTNote(m)
#def delDTNote(noteid):
#    m=getDTNote()
#    notelist=json.loads(m.content)
#    if noteid in notelist:
#        notelist.remove(noteid)
#        m.content=json.loads(notelist)
#        saveDTNote(m)
#def saveDTNote(m):
#    memcache.set('DTNoteList',m,3600)
#    try:
#        m.put()
#    except:
#        logging.info('DTNoteList:'+m.key().name())

def getMecacheNote(username):
    m=memcache.get('mecachenote'+'u'+username)
    if not m:
        m=MecacheNote.get_by_key_name('u'+username)
    if not m:
        m=MecacheNote(key_name='u'+username)
        m.content='[]'
    return m
def saveMecacheNote(m):
    memcache.set('mecachenote'+m.key().name(),m,36000)
    try:
        m.put()
    except :
        logging.info("mecachenote："+m.key().name())

#带上群应用的infoall
#第一个参数是 响应类 第二个参数 是xml 第三个参数是 obj2map 然后加进list里
def infoAllGroup(self,datas,getMapList,infoallxmldic,xml,user):
    appparm='&'#应用参数
#    userName=self.request.get('UserName') or ''
#    user=getorAddUser(userName)
    codepre= setting.APPCODE +'-s%s-0'
#    codepre= setting.APPCODE +'-s1-0'
    fathercode=setting.APPCODE+'-s%s'
    status='1'
    groupset=set()
    groupmap={}
    contentlist=[]


    user.createGroup+=user.createGroupAdd
    user.partnerGroup+=user.partnerGroupAdd
    user.memberGroup+=user.memberGroupAdd


    getMapList(contentlist,codepre%(999)+'0000',fathercode%(999),'10',setting.APPCODE,'101',json.dumps(groupDigTingToMap()),None,status,groupReplayType)

    for group in user.createGroup+user.partnerGroup+user.memberGroup:
        if group not in groupset:
            groupset.add(group)
#            groupmap[str(group)]=Group.get_by_id(group)
            groupmap[str(group)]=memacheGroup(group)
            if groupmap[str(group)]:
                title='13'
                if group in user.createGroup:
                    title='11'
                elif group in user.partnerGroup:
                    title='12'
                getMapList(contentlist,codepre%(groupmap[str(group)].apptype)+str(group),fathercode%(groupmap[str(group)].apptype),title,setting.APPCODE,'101',json.dumps(groupToMap(groupmap[str(group)])),None,status,groupReplayType)
#            else:
#                getMapList(contentlist,codepre+str(group),fathercode,title,setting.APPCODE,'101','',None,'0',groupReplayType)
#                fathergroup=codepre+str(group)
#                replaylist=[]
#                for n in Note.all().filter('group =',group).filter('isDelete =',False):
#                    getMapList(contentlist,codepre+str(group)+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n.content,n.updateTime,status,noteReplayType)
#                    replaylist.append('r'+str(n.key().id()))
#                for replay in Replay.get_by_key_name(replaylist):
#                    if replay and replay.content:
#                        notefather=codepre+str(group)+'-'+replay.key().name()[1:]
#                        notecode=notefather+'-'
#                        for r in json.loads(replay.content):
#                            getMapList(contentlist,notecode+str(r['index']),notefather,'15',setting.APPCODE,'103',json.dumps(r),datetime.datetime(*tuple(time.gmtime(r['datetime']))[:6]),status,replayReplayType)
#    logging.info(str(len(contentlist)))
    infoallxmldic(contentlist,xml,datas)
    datas.setAttribute('appcode', setting.APPCODE)
    timeline=self.request.get('timeline') or ''
    if not timeline:
        appparm+='timeline=0&'
    else:
        appparm+='timeline='+timeline+'&'
    dttimeline=self.request.get('dttimeline') or ''
    if not dttimeline:
        appparm+='dttimeline=0&'
    else:
        appparm+='dttimeline='+dttimeline+'&'
    datas.setAttribute('appparm',appparm[:-1])


def getRssNoteList(group):
    rssnotelist=memcache.get('rssgroupmemcach'+str(group))
    if not rssnotelist:
        rssnote=RssNote.get_by_key_name('rss'+str(group))
        if not rssnote:
            return []
        rssnotelist=rssnote.getNoteList()
        try:
            memcache.set('rssgroupmemcach'+str(group),rssnotelist,3600)
        except :
            logging.error('rss group note too big:'+str(len(rssnotelist)))
    return rssnotelist

#带上群应用的infoupdate
#第一个参数是 响应类 第二个参数 是xml 第三个参数是 obj2map 然后加进list里
def infoUpdateGroup(self,datas,getMapList,infoallxmldic,xml,user):


    groupdic={}
#    noticenum=0
    timelineold=self.request.get('timeline') or ''
    timeline=self.request.get('timeline') or ''
    dttimeline=self.request.get('dttimeline') or '0'
    timelineint=0
    dttimelineint=0

    dt=datetime.datetime.utcnow()
    dt = dt+timezone
    codepre= setting.APPCODE +'-s%s-0'
#    codepre= setting.APPCODE +'-s1-0'
    fathercode=setting.APPCODE+'-s%s'
    status='1'
    groupset=set()
    groupmap={}
    contentlist=[]
    if not timeline:
        infoAllGroup(self,datas,getMapList,infoallxmldic,xml,user)
        return
    try:
        timeline=float(timeline)
        timelineint=timeline
        dttimelineint=float(dttimeline)
    except :
        return
    timeline=datetime.datetime(*tuple(time.gmtime(timeline))[:6])
    appparm='&'#应用参数
    datas.setAttribute('appcode', setting.APPCODE)

    notenum=0

    #rss 帖子单独计算，不在tempmecachenote里
    rssnotenum=0
    m=getMecacheNote(user.key().name()[1:])
    mecachenote=json.loads(m.content)
    #logging.info(len(mecachenote))
    tempmecachenote=mecachenote[:50]
    mecachenote=mecachenote[50:]
    m.content=json.dumps(mecachenote)
    saveMecacheNote(m)
    replaylist=[]
    for flag,noteid,group,fathergroup in tempmecachenote:
        n=memcache.get('note'+str(noteid))
        if not n:
            n=Note.get_by_id(noteid)
            memcache.set('note'+str(n.key().id()),n,36000)
        groupObj=memacheGroup(group)
        if not groupObj:
            continue
        if n.isDelete:
            getMapList(contentlist,codepre%(groupObj.apptype)+str(group)+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102','',n.updateTime,'0',noteReplayType)
        else:
#            noticenum+=1
            getMapList(contentlist,codepre%(groupObj.apptype)+str(group)+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n.content,n.updateTime,status,noteReplayType)
            #计算群帖子数量
            groupCount(groupdic,group,fathergroup)
        if flag:
            replaylist.append('g'+str(group)+'r'+str(n.key().id()))
    for replay in Replay.get_by_key_name(replaylist):

        if replay and replay.content:
            groupObj=memacheGroup(replay.group)
            if not groupObj:
                continue
            notefather=codepre%(groupObj.apptype)+str(replay.group)+'-'+replay.key().name()[replay.key().name().find('r')+1:]
            notecode=notefather+'-'
            for r in json.loads(replay.content):
                getMapList(contentlist,notecode+str(r['index']),notefather,'15',setting.APPCODE,'103',json.dumps(r),datetime.datetime(*tuple(time.gmtime(r['datetime']))[:6]),status,replayReplayType)
    if tempmecachenote:
        appparm+='timeline='+timelineold+'&dttimeline='+dttimeline+'&'
        datas.setAttribute('appparm',appparm[:-1])
        infoallxmldic(contentlist,xml,datas)
        msgNode(groupdic,setting.APPCODE[1:],setting.APPCODE,xml,datas)
        return
#        return noticenum

    #间隔10分钟
    if self.request.get('isSync'):
        lastUpdate=memcache.get('lastupdate'+str(user.key().name()[1:]))
        if lastUpdate:
            utctime=datetime.datetime.utcnow()+datetime.timedelta(minutes=-10)
            if utctime<lastUpdate:
                return
    memcache.set('lastupdate'+str(user.key().name()[1:]),datetime.datetime.utcnow(),3600)
    #间隔10分钟止

    mecachenote=[]

    hotnotelist=getHotNote(user.key().name()[1:])
#    logging.info(str(len(hotnotelist))+str(user.key().name()[1:]))
    group='0000'
    fathergroup=codepre%(999)+str(group)
    num=0
    if hotnotelist and 0<len(hotnotelist):
        maxtimeline=0
#        memcache.delete('adnote')

        adnote=getAdNoteMap()
        if adnote:
#            logging.info('dttime:%s-%s'%(time.mktime(adnote['updateTime'].timetuple()),dttimelineint))
            if time.mktime(adnote['updateTime'].timetuple())>dttimelineint:
                maxtimeline=time.mktime(adnote['updateTime'].timetuple())
                adnote['updateTime']=str(adnote['updateTime'])
                contentstr=adnote.get('content','')
                if adnote.has_key('content'):
                    del adnote['content']
                getMapList(contentlist,fathergroup+'-'+str(num),fathergroup,'10',setting.APPCODE,'102',json.dumps(adnote)+contentstr,datetime.datetime.utcnow(),status,'43')#广告贴
                #计算群帖子数量
                groupCount(groupdic,group,fathergroup)
        num+=1
        hotcount=31

        for i in range(hotcount):
            notenum+=1
            if i>=len(hotnotelist):
                getMapList(contentlist,fathergroup+'-'+str(num),fathergroup,'10',setting.APPCODE,'102','',None,'0','43')
                num+=1
                continue
            n=hotnotelist[i]
#            logging.info('dttime:%s-%s'%(time.mktime(n.updateTime.timetuple()),dttimelineint))
    #        noticenum+=1
            if time.mktime(n.updateTime.timetuple())<=dttimelineint:
                num+=1
                continue
            if maxtimeline==0 or maxtimeline<time.mktime(n.updateTime.timetuple()):
                maxtimeline=time.mktime(n.updateTime.timetuple())
            getMapList(contentlist,fathergroup+'-'+str(num),fathergroup,'10',setting.APPCODE,'102',json.dumps(hotNoteToMap(n))+n.content,n.updateTime,status,'43')
    #        getMapList(contentlist,codepre+str(group)+'-'+str(num),fathergroup,'10',setting.APPCODE,'102',json.dumps(noteToMap(n))+n.content,n.updateTime,status,noteReplayType)
            #计算群帖子数量
            groupCount(groupdic,group,fathergroup)
#            replay=Replay.get_by_key_name('g'+str(n.group)+'r'+str(n.key().id()))
#            if replay and replay.content:
#                notefather=fathergroup+'-'+str(num)
#                notecode=notefather+'-'
#                for r in json.loads(replay.content):
#                    getMapList(contentlist,notecode+str(r['index']),notefather,'15',setting.APPCODE,'103',json.dumps(r),datetime.datetime(*tuple(time.gmtime(r['datetime']))[:6]),status,replayReplayType)
            num+=1
        if maxtimeline>0:
            dttimelineint=maxtimeline

    #新加入的群
    for group in user.createGroupAdd +user.partnerGroupAdd +user.memberGroupAdd :
        if group not in groupset:
            logging.info('add-%s'%group)
            groupset.add(group)
#            groupmap[str(group)]=Group.get_by_id(group)
            groupmap[str(group)]=memacheGroup(group)
            if groupmap[str(group)]:
                title='13'
                if group in user.createGroup:
                    title='11'
                elif group in user.partnerGroup:
                    title='12'
                getMapList(contentlist,codepre%(groupmap[str(group)].apptype)+str(group),fathercode%(groupmap[str(group)].apptype),title,setting.APPCODE,'101',json.dumps(groupToMap(groupmap[str(group)])),None,status,groupReplayType)
                fathergroup=codepre%(groupmap[str(group)].apptype)+str(group)
                replaylist=[]

                ####
                #### 判断是否rss群 ，单独处理
                ####
                #logging.info('g:'+str(groupmap[str(group)].type))
                if groupmap[str(group)].type==3:
                    rssnotelist=getRssNoteList(group)
#                    if not rssnotelist:
#                        rssnote=RssNote.get_by_key_name('rss'+str(group))
#                        rssnotelist=rssnote.getNoteList()
                    for n in rssnotelist:

                        rssnotenum+=1
                        getMapList(contentlist,fathergroup+'-'+str(n['id']),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n['content'],datetime.datetime(*tuple(time.gmtime(n['updateTime']))[:6]),status,noteReplayType)
                        #计算群帖子数量
                        groupCount(groupdic,group,fathergroup)
                        replaylist.append('g'+str(n['group'])+'r'+str(n['id']))
                    continue


                for n in Note.all().filter('group =',group).filter('isDelete =',False).order('-updateTime').fetch(groupmap[str(group)].notecount+groupmap[str(group)].topcount):
                    if notenum>50:
                        mecachenote.append((True,n.key().id(),group,fathergroup))
                        continue
                    notenum+=1
#                    noticenum+=1
                    getMapList(contentlist,fathergroup+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n.content,n.updateTime,status,noteReplayType)
                    #计算群帖子数量
                    groupCount(groupdic,group,fathergroup)
                    replaylist.append('g'+str(n.group)+'r'+str(n.key().id()))
                for replay in Replay.get_by_key_name(replaylist):
                    if replay and replay.content:
                        notefather=fathergroup+'-'+replay.key().name()[replay.key().name().find('r')+1:]
                        notecode=notefather+'-'
                        for r in json.loads(replay.content):
                            getMapList(contentlist,notecode+str(r['index']),notefather,'15',setting.APPCODE,'103',json.dumps(r),datetime.datetime(*tuple(time.gmtime(r['datetime']))[:6]),status,replayReplayType)
    #删除的群
    for group in user.createGroupRemove +user.partnerGroupRemove +user.memberGroupRemove :
        if group not in groupset:
            groupset.add(group)
            groupObj=memacheGroup(group)
            if not groupObj:
                continue
            getMapList(contentlist,codepre%(groupObj.apptype)+str(group),fathercode%(groupObj.apptype),'13',setting.APPCODE,'101','',None,'0',groupReplayType)

    #原有的群
    for group in user.createGroup +user.partnerGroup +user.memberGroup :
        if group not in groupset:
            groupset.add(group)
#            groupmap[str(group)]=Group.get_by_id(group)
            groupmap[str(group)]=memacheGroup(group)
            if groupmap[str(group)]:
                title='13'
                if group in user.createGroup:
                    title='11'
                elif group in user.partnerGroup:
                    title='12'
                fathergroup=codepre%(groupmap[str(group)].apptype)+str(group)

                ####
                #### 判断是否rss群 ，单独处理
                ####
                if groupmap[str(group)].type==3:
                    rssnotelist=getRssNoteList(group)
#                    if not rssnotelist:
#                        rssnote=RssNote.get_by_key_name('rss'+str(group))
#                        rssnotelist=rssnote.getNoteList()
                    for n in rssnotelist:
                        if datetime.datetime(*tuple(time.gmtime(n['updateTime']))[:6])>timeline:
#                            logging.info('rss=%s-%s'%(datetime.datetime(*tuple(time.gmtime(n['updateTime']))[:6]),timeline))
                            rssnotenum+=1
                            getMapList(contentlist,fathergroup+'-'+str(n['id']),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n['content'],datetime.datetime(*tuple(time.gmtime(n['updateTime']))[:6]),status,noteReplayType)
                            #计算群帖子数量
                            groupCount(groupdic,group,fathergroup)
                            replaylist.append('g'+str(group)+'r'+str(n['id']))
                    continue

                for n in Note.all().filter('group =',group).filter('updateTime >',timeline):
                    if n.isDelete:
                        getMapList(contentlist,fathergroup+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102','',n.updateTime,'0',noteReplayType)
                    else:
                        if notenum>50:
                            mecachenote.append((False,n.key().id(),group,fathergroup))
                            continue
                        notenum+=1
#                        noticenum+=1
                        getMapList(contentlist,fathergroup+'-'+str(n.key().id()),fathergroup,'14',setting.APPCODE,'102',json.dumps(noteToMap(n))+n.content,n.updateTime,status,noteReplayType)
                        #计算群帖子数量
                        groupCount(groupdic,group,fathergroup)
                for replay in Replay.all().filter('group =',group).filter('updateTime >',timeline):
                    if  replay.content:
                        notefather=fathergroup+'-'+replay.key().name()[replay.key().name().find('r')+1:]
                        notecode=notefather+'-'
                        for r in json.loads(replay.content):
                            if r['datetime']>timelineint:
                                getMapList(contentlist,notecode+str(r['index']),notefather,'15',setting.APPCODE,'103',json.dumps(r),datetime.datetime(*tuple(time.gmtime(r['datetime']))[:6]),status,replayReplayType)

    userneedsave=False
    if user.createGroupRemove:
        user.createGroupRemove=[]
        userneedsave=True
    if user.partnerGroupRemove:
        user.partnerGroupRemove=[]
        userneedsave=True
    if user.memberGroupRemove:
        user.memberGroupRemove=[]
        userneedsave=True

    if user.createGroupAdd:
        user.createGroup+=user.createGroupAdd
        user.createGroupAdd=[]
        userneedsave=True
    if user.partnerGroupAdd:
        user.partnerGroup+=user.partnerGroupAdd
        user.partnerGroupAdd=[]
        userneedsave=True
    if user.memberGroupAdd:
        user.memberGroup+=user.memberGroupAdd
        user.memberGroupAdd=[]
        userneedsave=True
    if userneedsave:
        user.put()
    infoallxmldic(contentlist,xml,datas)
    if mecachenote:
        m=getMecacheNote(user.key().name()[1:])
        m.content=json.dumps(mecachenote)
        saveMecacheNote(m)

    appparm+='timeline='+str(time.mktime(dt.timetuple()))+'&dttimeline='+str(dttimelineint)+'&'
#    if user.createGroup:
#        appparm+='createGroupId='+str(user.createGroup[-1])+'&'
#    if user.partnerGroup:
#        appparm+='partnerGroupId='+str(user.partnerGroup[-1])+'&'
#    if user.memberGroup:
#        appparm+='memberGroupId='+str(user.memberGroup[-1])+'&'
    datas.setAttribute('appparm',appparm[:-1])
    msgNode(groupdic,setting.APPCODE[1:],setting.APPCODE,xml,datas)
    return
#    return noticenum

def groupCount(groupmap,groupid,groupcode):
    groupid=str(groupid)
    if not groupmap.has_key((groupid,groupcode)):
        groupmap[(groupid,groupcode)]=0
    groupmap[(groupid,groupcode)]+=1

#def msgNode(groupmap,msgid,appcode,xml,datas):
#    if groupmap:
#        for groupid,groupcode in groupmap.keys():
#            msg=xml.createElement('notice')
#            msg.setAttribute('id','%s%s'%(msgid,groupid))
#            group=memacheGroup(groupid)
#            if group and hasattr(group,'name'):
#                msg.setAttribute('title',u'%s'%(getattr(memacheGroup(groupid),'name'),))
#            else:
#                continue
#            msg.setAttribute('content',u'新收到%s条信息'%(groupmap[(groupid,groupcode)],))
#            msg.setAttribute('code','%s;%s'%(appcode,groupcode))
#            datas.appendChild(msg)
#            pass
def msgNode(groupmap,msgid,appcode,xml,datas):
    if groupmap:
        tempGroup={}
        for groupid,groupcode in groupmap.keys():
            group=memacheGroup(groupid)
            if group:
                if not tempGroup.has_key(group.apptype):
                    tempGroup[group.apptype]=''

                if group and hasattr(group,'name'):
                    tempGroup[group.apptype]+=u'%s ，新收到%s条信息；'%(getattr(group,'name'),groupmap[(groupid,groupcode)])
                else:
                    continue
        for k in tempGroup.keys():
            msg=xml.createElement('notice')
            msg.setAttribute('id','%s%s'%(setting.APPCODE[1:],k))
            msg.setAttribute('title', setting.APPCODE_APPTYPE[k])
            msg.setAttribute('content',tempGroup[k])
            msg.setAttribute('code','%s-s%s'%(appcode,k))
            datas.appendChild(msg)
        pass
def memacheGroup(groupid):
    group=memcache.get('groupbyid'+str(groupid))
    if not group:
        if '0000'==groupid:
            group=Group()
            group.apptype='999'
            group.name=u'系统信息'
            return group
        groupid=int(groupid)
        if groupid:
            group=Group.get_by_id(int(groupid))
            memcache.set('groupbyid'+str(groupid),group,36000)
        else:
            return None
    return group
def getAdNoteMap():
    note=memcache.get('adnote')
    if not note:
        paimailist=PaiMai.all().order('-__key__').fetch(2)
        if 0!=len(paimailist):
            paimai=paimailist[-1]
            if not paimai.updateTime:
                paimai.put()
            note=AdNote.get_by_key_name('u'+paimai.user)
            if not note:
                return None
            note={'noteid':0000,'group':0000,'content':note.content,'title':u'[广告]'+note.title,'author':note.key().name()[1:],'nickname':getNickName(note.key().name()[1:]),'point':0,'up':0,'down':0,'updateTime':paimai.updateTime,'isTop':False}
#            adnote={'time':datetime.datetime.strptime(adnote.key().name()[1:],'%Y%m%d'),'content':adnote.content,'imgid':"[*TempLink/%s/%s*]" %(adnote.imgid,setting.APPCODE_ID),'link':adnote.link}

            memcache.set('adnote',note,36000)
        else:
            return None
    return note

def groupDigTingToMap():
    return {'groupid':0000,'name':u'大厅','head':'0' or 0,'tagid':0,'tagname':u'大厅','gonggao': u'大厅','author':'000','nickname':u'管理员','partner':[],'member':[],'type':3}

def groupToMap(group):
    if group:
        if group.type==3:
            return {'groupid':group.key().id(),'name':group.name,'head':group.head or 0,'tagid':group.tag,'tagname':getTagName(group.tag),'gonggao':group.gonggao or '','author':group.author,'nickname':getNickName(group.author),'partner':group.partner,'member':group.member,'type':1}
        return {'groupid':group.key().id(),'name':group.name,'head':group.head or 0,'tagid':group.tag,'tagname':getTagName(group.tag),'gonggao':group.gonggao or '','author':group.author,'nickname':getNickName(group.author),'partner':group.partner,'member':group.member,'type':group.type}
    else:
        return None

def hotNoteToMap(note):
    return {'noteid':note.key().id(),'group':note.group,'title':note.title,'author':note.author,'nickname':getNickName(note.author),'updateTime':str(note.updateTime)}


def noteToMap(note):
    if note:
        if isinstance(note,dict):
            return {'noteid':note['id'],'group':note['group'],'title':note['title'],'author':note['author'],'nickname':getNickName(note['author']),'point':note['point'],'up':note['up'],'down':note['down'],'updateTime':str(datetime.datetime(*tuple(time.gmtime(note['updateTime']))[:6])),'isTop':note['isTop']}
        else:
            return {'noteid':note.key().id(),'group':note.group,'title':note.title,'author':note.author,'nickname':getNickName(note.author),'point':note.point,'up':note.up,'down':note.down,'updateTime':str(note.updateTime),'isTop':note.isTop}
#        return {'noteid':note.key().id(),'group':note.group,'title':note.title,'content':note.content,'author':note.author,'nickname':getNickName(note.author),'point':note.point,'up':note.up,'down':note.down,'updateTime':str(note.updateTime),'isTop':note.isTop}
    else:
        return None

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

class ShowImg(Page):
    def get(self):
        imgid=self.request.get("image_id")
        if not imgid:
            self.error(500)
            return
        img=memcache.get('image_id'+str(imgid))
        if not img:
            if str(imgid)[0]=='0' :
                gnum=str(imgid).find('G')
                if gnum==-1:
                    self.error(404)
                    return
                else:
                    groupidstr=str(imgid)[1:gnum]
                    rssimg=memcache.get('rssimg'+groupidstr)
                    if not rssimg:
                        rssimg=RssImg.get_by_key_name('rss'+groupidstr)
                    if rssimg:
                        rssimgdic=rssimg.getImgDic()
                        for imgdic in rssimgdic.values():
                            for imgkey in imgdic.keys():
                                memcache.set('image_id'+str(imgkey),imgdic[imgkey],3600*24*20)
                                if imgkey == imgid:
                                    img=imgdic[imgkey]
            else:
                img=Img.get_by_id(int(imgid))
                memcache.set('image_id'+str(imgid),img,36000)

        if not img:
            self.error(404)
#        elif greeting!='noimg':
#            self.response.headers['Content-Type'] = "application/x-www-form-urlencoded"
#            self.response.out.write(greeting)
        else:
            if str(imgid)[0]=='0':
                self.response.headers['Content-Type'] = "text/html"
                self.response.out.write(img)
            elif img.src:
                self.response.headers['Content-Type'] = "text/html"
                self.response.out.write(img.src)
            else:
                self.response.headers['Content-Type'] = str(img.type)
                self.response.out.write(img.afile)


class DeleteNote(Page):
    def get(self):
        nowtime=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)
        if nowtime.hour<15 or nowtime.hour>14:
            return
        timeline=datetime.datetime.utcnow()+ datetime.timedelta(hours=-24)
        db.delete(Note.all().filter('isDelete =',True).filter('updateTime <',timeline).fetch(100))

class DoHotNote(Page):
    def get(self):
        getHotDaTingNate()


def getHotDaTingNate():
#    hotnotlist=memcache.get('hotnotlist')
#    if not hotnotlist:
        hotnotlist=[]
        for note in DaTingNote.all().filter('isPub =',True).order('createTime'):
            hotnotlist.append(note)
        memcache.set('hotnotelist',hotnotlist,36000)
        memcache.set('hotnoteflag',str(uuid.uuid4()),3600*3)
#    return hotnotlist
        #doHotNote()

def doHotNote():
    hothour=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)
    hot3hour=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)-datetime.timedelta(hours=3)
    hot24hour=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)-datetime.timedelta(hours=24)-datetime.timedelta(hours=3)
    hot24_7hour=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)-datetime.timedelta(hours=24*7)-datetime.timedelta(hours=3)
    hot24_30hour=datetime.datetime.utcnow()+ datetime.timedelta(hours=8)-datetime.timedelta(hours=24*30)-datetime.timedelta(hours=3)
    memcache.set('hotnoteflag',str(uuid.uuid4()),36000)
    hotnotemap=[]
    noteset=set()
    for note in Note.all().filter('updateTime <=',hothour).filter('updateTime >',hot3hour).filter('isDelete =',False).order('-updateTime').order('-point').fetch(5):
        hotnotemap.append(note)
        noteset.add(note.key().id())
    for note in Note.all().filter('updateTime <=',hothour).filter('updateTime >',hot24hour).filter('isDelete =',False).order('-updateTime').order('-point').fetch(10):
        if len(noteset)<10:
            if note.key().id() not in noteset:
                hotnotemap.append(note)
                noteset.add(note.key().id())
        else:
            break
    for note in Note.all().filter('updateTime <=',hothour).filter('updateTime >',hot24_7hour).filter('isDelete =',False).order('-updateTime').order('-point').fetch(12):
        if len(noteset)<12:
            if note.key().id() not in noteset:
                hotnotemap.append(note)
                noteset.add(note.key().id())
        else:
            break
    for note in Note.all().filter('updateTime <=',hothour).filter('updateTime >',hot24_30hour).filter('isDelete =',False).order('-updateTime').order('-point').fetch(14):
        if len(noteset)<14:
            if note.key().id() not in noteset:
                hotnotemap.append(note)
                noteset.add(note.key().id())
        else:
            break

    memcache.set('hotnotemap',hotnotemap,360000)
    logging.info(str(noteset))
#        m=HoTNote.get_by_key_name('note')
#        if not m:
#            m=HoTNote(key_name='note')
#        m.content=pickle.dumps(hotnotemap).encode('utf-8')
#        m.put()
    return

def getHotNote(username):
    hasdown=memcache.get('hotnoteflag')
    if hasdown:
        hasdown2=memcache.get(hasdown+'hotnote'+username)
        if hasdown2:
            return []
        else:
            l=memcache.get('hotnotelist')
            if not l:
                getHotDaTingNate()
                return []
            memcache.set(hasdown+'hotnote'+username,True,36000)
            return l
    else:
        return []


