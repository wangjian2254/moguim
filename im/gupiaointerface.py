#coding=utf-8
from im.model.models import GupiaoToGroup
from im.rssinterface import memacheGroup
from im.tool import getorAddUser
import setting

__author__ = 'Administrator'

from google.appengine.api import memcache
from xml.dom.minidom import Document
from google.appengine.ext import db
from google.appengine.api import urlfetch
import logging,json
from tools.page import Page
chardict={"11":u"A股","24":u"货基","13":u"权证","12":u"B股","15":u"债券","14":u"期货","22":u"ETF","23":u"LOF","33":u"港指数","32":u"窝轮","31":u"港股","42":u"外期","26":u"封基","41":u"美股","25":u"QDII","21":u"开基"}


#http://suggest3.sinajs.cn/suggest/type=&name=suggestdata_1357476438968&key=shg
#查找群
class SearchGuPiao(Page):
    def get(self):
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
                if type_n in ['11','12']:
                    pass
                elif type_n == '31':
                    realNo='hk'+dm
                elif type_n=='41':
                    realNo='gb_'+dm
                else:
                    self.response.out.write('1')
                    return
                gupiaoToGroup=GupiaoToGroup.get_by_key_name(key_names=dm)
                if gupiaoToGroup:
                    group=memacheGroup(groupId)
                    if group:
                        if userName not in group.member:
                            group.member.append(userName)
                        if group.key().id() not in user.memberGroup:
                            if group.key().id() not in user.memberGroupAdd:
                                user.memberGroupAdd.append(group.key().id())
                                if group.key().id() in user.memberGroupRemove:
                                    user.memberGroupRemove.remove(group.key().id())
                    else:
                        self.response.out.write('2')
                else:
                    pass#新被订阅的股票
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
            self.response.out.write(setting.WEBURL[7:]+'/InfoUpdate')
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')

