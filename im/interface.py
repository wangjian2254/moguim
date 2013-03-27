#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime,time
import json
from model.models import User,Group, Tag
from groupinterface import infoAllGroup,infoUpdateGroup
from tool import getorAddUser
from setting import APPCODE
import setting
from tools.page import Page, getUUID
from google.appengine.api import memcache
from xml.dom.minidom import Document
import logging
__author__ = u'王健'

timezone=datetime.timedelta(hours =8)
replayType='30'
class Index(Page):
    def get(self):
        self.render('templates/index.html',{})
class GroupHtml(Page):
    def get(self):
        self.render('templates/group.html',{'grouplist':Group.all(),'taglist':Tag.all()})

#memcache.Client().set(username+"_request_token1",auth_client.request_token,36000)
def getuser(m,uid):
    if not m.has_key(uid):
        m[uid]=User.get_by_key_name('u'+uid)
    return m[uid]


#获取信息（给我的通信、申请情况）
class InfoUpdate(Page):
    def get(self):
        d1 = datetime.datetime.utcnow()+timezone
        username=self.request.get('UserName') or ''
        saylist=memcache.get(username) or []
        contentlist=[]
        usermap={}
        usersaymap={}
        hasSay=False
        person=getorAddUser(username)
        if person:
            for uid,date,say in saylist:
                title='2'
                if uid in person.friends:
                    title='1'
                if not usermap.has_key(uid):
                    user=getuser(usermap,uid)
                    usersaymap[uid]=0
                    if not user:
                        continue
                    userdic=user2dic(user,True)
                    getMapList(contentlist,APPCODE+'-s1-'+uid,APPCODE+'-s1',title,APPCODE,'101',json.dumps(userdic),d1,'1',replayType)
                getMapList(contentlist,APPCODE+'-s1-'+uid+'-'+getUUID(),APPCODE+'-s1-'+uid,title,APPCODE,'102',say,date,'1',replayType)
                usersaymap[uid]+=1
            if contentlist:
                memcache.set(username+'InfoUpdate',{'num':0},12000)
            memcache.set(username,[],1000)
            xml,datas=infoallxmldic(contentlist)
            datas.setAttribute('type','infoupdate')
            datas.setAttribute('code',APPCODE)

#            noticenotenum=infoUpdateGroup(self,datas,getMapList,infoallxmldic,xml,person)
            infoUpdateGroup(self,datas,getMapList,infoallxmldic,xml,person)

            timespan=memcache.get(username+'InfoUpdate')
    #        logging.info(str(timespan))
            if not timespan :
                timespan={'num':0}

            if datas.hasChildNodes():#
                timespan['num']+=1
            if timespan['num']>4 :
                datas.setAttribute('timespan','120')
            else:
                datas.setAttribute('timespan','30')
            memcache.set(username+'InfoUpdate',timespan,12000)
    #        logging.info(str(timespan))
#            if contentlist or noticenotenum:
            if contentlist :
#                datas.setAttribute('noticetitle',u'收到新消息')
#                datas.setAttribute('noticecode',APPCODE)
                noticecontent=u'收到 '
                for uid in usermap.keys():
                    noticecontent+=(usermap[uid].nickname or str(uid)) +' :'+str(usersaymap[uid])+u'条新消息;'
#                datas.setAttribute('noticecontent',noticecontent[:-1])

                msg=xml.createElement('notice')
                msg.setAttribute('id','%s1'%(setting.APPCODE[1:],))
                msg.setAttribute('title',u'收到新消息')
                msg.setAttribute('content',noticecontent[:-1])
                msg.setAttribute('code','%s-s1'%(APPCODE,))
                datas.appendChild(msg)
            strxml=xml.toxml('utf-8')
            self.response.out.write(strxml)
            #logging.info(strxml)
#            person.put()
#        logging.info(strxml)
#            self.response.out.write('<textarea rows="15" cols="50">'+xml.toxml('utf-8')+'</textarea5>')

#def msgNode(groupmap,msgid,appcode,xml,datas):
#    if groupmap:
#        contentstr=''
#        for groupid,groupcode in groupmap.keys():
#            group=memacheGroup(groupid)
#            if group and hasattr(group,'name'):
#                contentstr+=u'%s ，新收到%s条信息；'%(getattr(memacheGroup(groupid),'name'),groupmap[(groupid,groupcode)])
#            else:
#                continue
#        msg=xml.createElement('notice')
#        msg.setAttribute('id','%s'%(setting.APPCODE[1:],))
#        msg.setAttribute('title',u'群应用')
#        msg.setAttribute('content',contentstr)
#        msg.setAttribute('code','%s;00001'%(appcode,))
#        datas.appendChild(msg)


def user2dic(user,s=False):
    u={'username':user.key().name()[1:],'nickname':user.nickname or '','header':user.header or 0,'birthday':user.birthday or '','sheng':user.sheng or 0,'city':user.city or 0,'sex':user.sex}
    u['desc']=user.desc or ''
    if s:
        setOnlineUser(u)
    return u
#获取基础信息（我的基础信息、好友的基础信息、好友列表）
class InfoAll(Page):
    def get(self):
        username=self.request.get('UserName') or ''

        contentlist=[]
#        getMapList(contentlist,APPCODE+'-s1',APPCODE,'',APPCODE,'100',u'聊天',None,'1',replayType)
        if username:
            user=getorAddUser(username)
            userdic=user2dic(user)
            getMapList(contentlist,APPCODE+'-s1-'+username,APPCODE+'-s1','0',APPCODE,'101',json.dumps(userdic),None,'1',replayType)
            for uid in user.friends:
                u=User.get_by_key_name('u'+uid)
                userdic=user2dic(u)
                getMapList(contentlist,APPCODE+'-s1-'+uid,APPCODE+'-s1','1',APPCODE,'101',json.dumps(userdic),None,'1',replayType)
            for uid in user.stranger:
                u=User.get_by_key_name('u'+uid)
                userdic=user2dic(u)
                getMapList(contentlist,APPCODE+'-s1-'+uid,APPCODE+'-s1','2',APPCODE,'101',json.dumps(userdic),None,'1',replayType)
            xml,datas=infoallxmldic(contentlist)
            datas.setAttribute('type','infoall')
            datas.setAttribute('code',APPCODE)
            datas.setAttribute('timespan',str(10*60*1*60))
            infoAllGroup(self,datas,getMapList,infoallxmldic,xml,user)
            self.response.out.write(xml.toxml('utf-8'))
#            user.put()

            

#发出删除好友
class DelFriend(Page):
    def get(self):
        try:
            username=self.request.get('UserName') or ''
            friend=self.request.get('Friend') or ''
            if username and friend:
                user=User.get_by_key_name('u'+username)
                if friend in user.friends:
                    user.friends.remove(friend)
                    user.put()
                self.response.out.write('0')#成功了
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')
#发出删除好友
class AddFriend(Page):
    def get(self):
        try:
            username=self.request.get('UserName') or ''
            friend=self.request.get('Friend') or ''
            if username==friend:
                self.response.out.write('0')#成功了
                return
            if username and friend:
                user=User.get_by_key_name('u'+username)
                if friend not in user.friends:
                    user.friends.append(friend)
                    user.put()
                self.response.out.write('0')#成功了
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')


def setOnlineUser(user):
    online=memcache.get('online')
#    logging.info(str(online))
    if not online:
        online=[]
    num=len(online)
    if num==0:
        s=set()
        s.add(user['username'])
        online.append(s)
        online.append(user)
    if num>0 and num<=500:
        if user['username'] not in online[0]:
            online[0].add(user['username'])
            online.append(user)
    if num>=500:
        for u in online[1:-400]:
            online[0].remove(u['username'])
            online.remove(u)
    memcache.set('online',online,360000)

class PrintOnline(Page):
    def get(self):
#        online=memcache.get('online') or [{"username":'232',"nickname":u'王健','birthday':'2012-02-22','sheng':5,'city':'3','sex':False}]
        online=memcache.get('online') or []
        self.render('templates/userinfolist.html',{'userlist':online})

#根据条件查找用户
class Search(Page):
    def post(self):
#        type=self.request.get('searchType')
        try:
            sendusername=self.request.get('UserName')
            logging.info("sendusername:"+sendusername)
            username=self.request.get('searchUname') or ''
            logging.info("searchUname:"+username)
            nickname=self.request.get('nickname') or ''

            nickname=nickname.encode('utf-8')
            nickname=nickname.decode('utf-8')
            logging.info("nickname:"+nickname)
            minage=self.request.get('minage') or '0'
            logging.info("minage:"+str(minage))
            maxage=self.request.get('maxage') or '99'
            logging.info("maxage:"+str(maxage))
            sheng=self.request.get('sheng') or ''
            logging.info("sheng:"+sheng)
            if sheng:
                sheng=int(sheng)
            city=self.request.get('city') or ''
            logging.info("city:"+city)
            if city:
                city=int(city)
            sex=self.request.get('sex') or ''
            logging.info("sex:"+sex)
            userlist=[]

            if username:
                user=User.get_by_key_name('u'+username)
                if user and username!=sendusername:
                    userlist.append(user2dic(user))
            else:
                online=memcache.get('online') or []
#                logging.info(str(online))
                online=online[1:]
                online.reverse()
                my=User.get_by_key_name('u'+sendusername)
                for u in online:
                    if sendusername==u['username'] or u['username'] in my.friends:
                        continue
                    isuser=True
                    logging.info("isuser:"+str(isuser))
                    if u['birthday']:
                        age=datetime.datetime.utcnow().year-time.strptime(u['birthday'],"%Y-%m-%d").tm_year
                    else:
                        age=18
#                    logging.info(str(nickname and nickname not in u['nickname'])+'-1-'+u['nickname'])
                    if nickname and nickname not in u['nickname']:
                        isuser=False
                    logging.info("nickname-isuser:"+str(isuser))
#                    logging.info(str(int(minage)<=age<=int(maxage))+'-2-'+str(age))
                    if isuser and int(minage)<=age<=int(maxage):
                        isuser=True
                    else:
                        isuser=False
                    logging.info("age-isuser:"+str(isuser))
#                    logging.info(str(sheng!=u['sheng'])+'-3-'+str(u['sheng']))
                    if sheng and sheng!=u['sheng']:
                        isuser=False
                    logging.info("sheng-isuser:"+str(isuser))
#                    logging.info(str(city!=u['city'])+'-4-'+str(u['city']))
                    if city and city!=u['city']:
                        isuser=False
                    logging.info("city-isuser:"+str(isuser))
#                    logging.info(str(sex!=u['sex'])+'-5-'+str(u['sex']))
                    if sex and sex!=u['sex']:
                        isuser=False
                    logging.info("sex-isuser:"+str(isuser))
#                    logging.info("6--"+str(isuser))
                    if isuser:
                        userlist.append(u)
                        if len(userlist)>=20:
                            break
            self.response.out.write(json.dumps(userlist))
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')


#向某用户发送通信
class SendSay(Page):
    def post(self):
        try:
            d1 = datetime.datetime.utcnow()+timezone
            fromuser=self.request.get('fromuser')
            touser=self.request.get('touser')
            say=self.request.get('say')
            say=say.encode('utf-8')
            say=say.decode('utf-8')
#            logging.info(str(say))
#            logging.info(str(self.request))
            saylist=memcache.get(touser)
            if not saylist:
                saylist=[]
            saylist.append((fromuser,str(d1),say))
            memcache.set(touser,saylist,100000)
            self.response.out.write(str(d1))
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')
#保存我的基本信息
class UpdateInfo(Page):
    def post(self):
        #u={'nickname':user.nickname,'birthday':user.birthday,'sheng':user.sheng,'city':user.city,'sex':user.sex}
        try:
            username=self.request.get('UserName') or ''
            if username:
                user=User.get_by_key_name('u'+username)
                if not user:
                    user=User(key_name='u'+username)
                user.nickname=self.request.get('nickname').encode('utf-8').decode('utf-8') or ''
                user.desc=self.request.get('desc').encode('utf-8').decode('utf-8') or ''
                user.birthday=self.request.get('birthday') or ''
                sheng=self.request.get('sheng') or ''
                if sheng:
                    user.sheng=int(sheng)
                city=self.request.get('city') or ''
                if city:
                    user.city=int(city)
                header=self.request.get('header') or 0
                if header:
                    user.header=int(header)
                sex=self.request.get('sex') or ''
                if sex.lower()=='True'.lower():
                    user.sex=True
                if sex.lower()=='False'.lower():
                    user.sex=False
                user.put()
                self.response.out.write(setting.WEBURL[7:]+'/InfoAll')
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')

def infoallxmldic(contents,xml=None,datas=None,delete=None):
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

def getMapList(l,code,father,title,maincode,level,content,lastUpdateTime,status,replyType):
    u= {'code': code, 'father': father}
    if title:
        u['title']=title
    u['maincode']=maincode
    u['level']=level
    u['content']=content
    if lastUpdateTime:
        u['lastUpdateTime']=lastUpdateTime
    u['status']=status
    u['replyType']=replyType
    l.append(u)