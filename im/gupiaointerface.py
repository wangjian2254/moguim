#coding=utf-8
from model.models import GupiaoToGroup, Group, GuPiaoNote
from rssinterface import memacheGroup
from tool import getorAddUser
import setting

__author__ = 'Administrator'

from google.appengine.api import memcache
from xml.dom.minidom import Document
from google.appengine.ext import db
from google.appengine.api import urlfetch
import logging,json
import datetime,time
from tools.page import Page
chardict={"11":u"A股","24":u"货基","13":u"权证","12":u"B股","15":u"债券","14":u"期货","22":u"ETF","23":u"LOF","33":u"港指数","32":u"窝轮","31":u"港股","42":u"外期","26":u"封基","41":u"美股","25":u"QDII","21":u"开基"}

timezone=datetime.timedelta(hours =8)
resultStr='{"result":"%s","message":"%s","url":"%s"}'
#http://suggest3.sinajs.cn/suggest/type=&name=suggestdata_1357476438968&key=shg
#查找群
class SearchGuPiao(Page):
    def post(self):
#        groupid=self.request.get("GroupId")
#        tagid=self.request.get("TagId")
        tagname=self.request.get("Tagname")
#        page=self.request.get("page") or 0
#        logging.info('tagid:'+str(tagid))
#        logging.info('Tagname:'+tagname)
        baseurl='http://suggest3.sinajs.cn/suggest/type=&name=suggestdata_1357476438968&key='+tagname
        result = urlfetch.fetch(
            url = baseurl,
#                    payload = login_data,
            method = urlfetch.GET,
            headers = {'Content-Type':'application/x-www-form-urlencoded',
                       'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
            follow_redirects = False,deadline=20)
        l=[]
        if result.status_code == 200 :
            gupiaoArr=result.content.decode('gbk')
            s=gupiaoArr[gupiaoArr.find('"')+1:gupiaoArr.rfind('"')]
            for opt in s.split(";"):
                opts=opt.split(',')
#                self.response.out.write(u"%s</br>"%opts[3])
#                self.response.out.write("%s</br>"%chardict[opts[1]])
#                if len(opts)<2:
#                    self.response.out.write(json.dumps(opts))
                if opts[1] in ['11','12','31','41']:
                    l.append({'key':opts[0],'type_n':opts[1],'type':chardict[opts[1]],'dm':opts[2],'dmall':opts[3],'name':opts[4]})
#                    self.response.out.write(u"%s %s %s %s %s %s</br>"%(opts[0],chardict[opts[1]],opts[2],opts[3],opts[4],opts[5]))

            self.response.out.write(json.dumps(l))
        else:
            self.response.out.write(json.dumps(l))

class SyncGuPiao(Page):
    def post(self):
        #获取股票数据
        noteupdate=datetime.datetime.utcnow()+timezone
        groupidlist=[]
        for gid in self.request.get('groupids','').split(','):
            if gid:
                groupidlist.append(gid)
        guPiaoNoteList=GuPiaoNote.get_by_key_name(groupidlist)
        for i,groupid in enumerate(groupidlist):
            guPiaoNote=guPiaoNoteList[i]
            if not guPiaoNote:
                guPiaoNote=GuPiaoNote(key_name=groupid)
            if self.request.get(groupid,'').find("'type':'11'")>0 or self.request.get(groupid,'').find("'type':'12'")>0:
                tmpgupiaostr=self.request.get(groupid,'').split(',')[0]+self.request.get(groupid,'')[-13:-8]
                tmpgupiaosave=guPiaoNote.content.split(',')[0]+guPiaoNote.content[-13:-8]
            else:
                tmpgupiaostr=self.request.get(groupid,'')
                tmpgupiaosave=guPiaoNote.content
            if tmpgupiaostr!=tmpgupiaosave:
#                logging.info('old:'+guPiaoNote.content)
#                logging.info('new:'+self.request.get(groupid))
                guPiaoNote.content=self.request.get(groupid)
                guPiaoNote.updateTime=noteupdate
#                guPiaoNote.imagestr=self.request.get('image'+groupid)
                guPiaoNote.put()
                memcache.set('gupiaonote'+groupid,guPiaoNote,36000)
            else:
                logging.info('no save0:'+self.request.get(groupid,''))
                logging.info('no save0:'+guPiaoNote.content)




class NeedSyncGuPiao(Page):
    def get(self):
        #获取该同步的股票群
        s=''
        needsyncgupiao=memcache.get('needsyncgupiao')
        if needsyncgupiao:
            s=','.join(needsyncgupiao)
            self.response.out.write(s)
            memcache.delete('needsyncgupiao')
        return
class DeleteNeedSyncGuPiao(Page):
    def post(self):
        #删除需要同步的股票di缓存
        gupiaogroupid=self.request.get('needdelgroupid','')
        if gupiaogroupid:
            kl=gupiaogroupid.split(',')
            memcache.delete_multi(kl)
        return
class SyncGuPiaoByID(Page):
    def post(self):
        #删除需要同步的股票di缓存
        groupid=self.request.get('gupiaoid',0)
        ###同步给股票同步应用
        result = urlfetch.fetch(
            url =setting.GUPIAOURL+'/syncGuPiaoByID?groupid=%s'%groupid,
#                    payload = login_data,
            method = urlfetch.GET,
            headers = {'Content-Type':'application/x-www-form-urlencoded',
                       'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
            follow_redirects = False,deadline=20)
        if result.status_code != 200 :
            self.response.out.write(resultStr%('fail',u'股票数据获取失败，请稍后再试',''))
            return
        else:
            guPiaoNote=GuPiaoNote.get_by_key_name(key_names='g'+str(groupid))
            logging.info(groupid)
            logging.info(result.content.decode('utf-8'))
            logging.info(guPiaoNote.content)
            if result.content and result.content.decode('utf-8')!=guPiaoNote.content:
                logging.info(u'not same')
                guPiaoNote.content=result.content.decode('utf-8')
                guPiaoNote.updateTime=datetime.datetime.utcnow()+timezone
                guPiaoNote.put()
                memcache.set('gupiaonoteg'+groupid,guPiaoNote,36000)
                self.response.out.write(resultStr%('success','',setting.WEBURL[7:]+'/InfoUpdate'))
            else:
                self.response.out.write(resultStr%('fail',u'股票数据已经是最新了',''))


#参加、退出群
class JoinGuPiao(Page):
    def post(self):
        try:
            userName=self.request.get("UserName")
            user=getorAddUser(userName)
            dm=self.request.get("dm")
            dmall=self.request.get("dmall")
            type_n=self.request.get("type_n")
            name=self.request.get("name")
            ###操作类型
            do=self.request.get('DoType')# '1'为加入 '2'为退订
            groupId=self.request.get('GroupId')
            if do=='1':
                #### 下面是加入群
                realNo=dmall
                if dmall=='sh000001':
                    dm=dmall
                if type_n in ['11','12']:
                    pass
#                    dm=dmall
                elif type_n == '31':
                    realNo='hk'+dm
                    #dm=realNo

                elif type_n=='41':
                    realNo='gb_'+dm
                    #dm=realNo
                else:
                    self.response.out.write(resultStr%('fail',u'只能订阅A股、B股、港股、美股',''))
                    return
                gupiaoToGroup=memcache.get('gupiaodm'+dm)
                if not gupiaoToGroup:
                    gupiaoToGroup=GupiaoToGroup.get_by_key_name(key_names='g'+dm)
                    if gupiaoToGroup:
                        memcache.set('gupiaodm'+dm,gupiaoToGroup,36000)
                if not gupiaoToGroup:
                    group=Group()
                    group.name=name
#                    if type_n =='11':
#                        group.gonggao=u'A股'
#                    if type_n =='12':
#                        group.gonggao=u'B股'
                    if type_n =='31':
                        group.gonggao=u'[港]'
                    if type_n =='41':
                        group.gonggao=u'[美]'
                    group.type=4
                    group.apptype='4'
                    group.author='000'
                    group.head=int(type_n)
                    group.notecount=1
                    group.put()
                    guPiaoNote=GuPiaoNote(key_name='g'+str(group.key().id()))
                    guPiaoNote.imagestr='_%s_%s'%(realNo,type_n)
                    guPiaoNote.updateTime=datetime.datetime.utcnow()+timezone
                    guPiaoNote.put()
                    gupiaoToGroup=GupiaoToGroup(key_name='g'+dm)
                    gupiaoToGroup.group=group.key().id()
                    gupiaoToGroup.name=name
                    gupiaoToGroup.dmall=dmall
                    gupiaoToGroup.type=type_n
                    gupiaoToGroup.put()
                    #######
                    ###同步给股票同步应用
                    result = urlfetch.fetch(
                        url =setting.GUPIAOURL+'/markGroup?groupid=%s&dm=%s&type=%s&realNo=%s'%(group.key().id(),dm,type_n,realNo),
        #                    payload = login_data,
                        method = urlfetch.GET,
                        headers = {'Content-Type':'application/x-www-form-urlencoded',
                                   'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'},
                        follow_redirects = False,deadline=20)
                    if result.status_code != 200 :
                        group.delete()
                        gupiaoToGroup.delete()
                        guPiaoNote.delete()
                        self.response.out.write(resultStr%('fail',u'订阅股票失败，请稍后再试',''))
                        return
                    else:
                        memcache.set('gupiaodm'+dm,gupiaoToGroup,36000)
                        logging.info(result.content)
                        logging.info(guPiaoNote.content)
                        if result.content!=guPiaoNote.content:
                            guPiaoNote.content=result.content.decode('utf-8')
                            guPiaoNote.updateTime=datetime.datetime.utcnow()+timezone
                            guPiaoNote.put()


                else:
                    group=memacheGroup(gupiaoToGroup.group)
                if group:
                    if userName not in group.member:
                        group.member.append(userName)
                        group.put()
                    if group.key().id() not in user.memberGroup:
                        if group.key().id() not in user.memberGroupAdd:
                            user.memberGroupAdd.append(group.key().id())
                            user.put()
                        if group.key().id() in user.memberGroupRemove:
                            user.memberGroupRemove.remove(group.key().id())
                            user.put()
                else:
                    self.response.out.write(resultStr%('fail',u'订阅股票失败，股票已被删除',''))
                    return


            elif do=='2':
                ##### 下面是退出群 退订股票
                if groupId:
                    try:
                        groupId=int(groupId)
                    except Exception,e:
                        logging.info(str(e))
                        self.response.out.write('1')
                        return
                    group=memacheGroup(groupId)
                    if userName in group.member:
                        group.member.remove(userName)
                    if group.key().id() in user.memberGroup:
                        user.memberGroup.remove(group.key().id())
                        if group.key().id() not in user.memberGroupRemove:
                            user.memberGroupRemove.append(group.key().id())
                            if group.key().id() in user.memberGroupAdd:
                                user.memberGroupAdd.remove(group.key().id())
            self.response.out.write(resultStr%('success','',setting.WEBURL[7:]+'/InfoUpdate'))
        except Exception,e:
            logging.info(str(e))
            self.response.out.write(resultStr%('fail',u'订阅股票失败，请稍后再试',''))

