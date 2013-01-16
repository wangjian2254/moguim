#coding=utf-8
from im.tool import getorAddUser

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
                if len(opts)<2:
                    self.response.out.write(json.dumps(opts))
                else:
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
            #### 下面是加入群
        except Exception,e:
            logging.info(str(e))
            self.response.out.write('1')

