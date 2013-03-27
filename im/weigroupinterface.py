#coding=utf-8
#author:u'王健'
#Date: 13-3-21
#Time: 下午6:51
import json
import logging
import urllib
import datetime
from google.appengine.api import memcache
from model.models import WeiNote, WeiNoteReplay, WeiNotePoint, WeiUser
from tool import getorAddUser
from tools.page import Page
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


timezone=datetime.timedelta(hours =8)
resultStr='{"result":"%s","message":"%s","url":"%s"}'

__author__ = u'王健'

class CreateWeiNote(Page):
    '''
    创建或者修改 论坛帖子、跟帖
    手机端如果要发表图片，应该在先发布图片再调用此方法。

    '''
    def get(self):

        upload_url = blobstore.create_upload_url('/uploadImage')
        self.flashhtml(upload_url)
    def post(self):
        groupid=self.request.get('groupid',0)
        weinoteid=self.request.get('weinoteid','')
        title=self.request.get('title','')
        content=self.request.get('content','')
        type=self.request.get('type','0')
        image_list=self.request.get('image_list','')
        author=self.request.get('author','')
        if not groupid or not title or not author:
            self.flashhtml(resultStr%('fail',u'标题、群号、用户号为必填项。',''))
            return
        try:
            if not weinoteid:
                weinote=WeiNote()
            else:
                weinote=WeiNote.get_by_id(int(weinoteid))
            weinote.group=int(groupid)
            weinote.title=title
            weinote.content=content
            weinote.type=int(type)
            for imageid in image_list.split(','):
                weinote.image_list.append(int(imageid))
            if author[0]=='u':
                weinote.author=author
            else:
                weinote.author='u'+author
            weinote.updateTime=datetime.datetime.utcnow()+timezone
            weinote.put()
            if not weinoteid:
                weiNotePoint=WeiNotePoint()
                weiNotePoint.group=int(groupid)
                weiUser=WeiUser.get_by_key_name(weinote.author+'-'+str(groupid))
                if weiUser:
                    weiNotePoint.point=weiUser.point
                else:
                    weiNotePoint.point=0
                weiNotePoint.put()
                self.flashhtml(resultStr%('success',u'发布帖子成功。',''))
            else:
                self.flashhtml(resultStr%('success',u'修改帖子成功。',''))
            return
        except Exception,e:
            self.flashhtml(resultStr%('fail',u'服务器异常，请稍后再操作。',''))
            logging.error(str(e))
            return
class CreateWeiNoteReplay(Page):
    '''
    创建跟帖
    手机端如果要发表图片，应该在先发布图片再调用此方法。

    '''
    def post(self):
        weinoteid=self.request.get('weinoteid','')
        content=self.request.get('content','')
        image_list=self.request.get('image_list','')
        author=self.request.get('author','')
        if  not content or not weinoteid or not author:
            self.flashhtml(resultStr%('fail',u'内容、帖子号、用户号为必填项。',''))
            return
        try:
            weinotereplay=WeiNoteReplay()
            weinotereplay.content=content
            weinotereplay.note=int(weinoteid)
            for imageid in image_list.split(','):
                weinotereplay.image_list.append(int(imageid))
            if author[0]=='u':
                weinotereplay.author=author
            else:
                weinotereplay.author='u'+author
            weinotereplay.updateTime=datetime.datetime.utcnow()+timezone
            weinotereplay.put()

            self.flashhtml(resultStr%('success',u'回复帖子成功。',''))
            return
        except Exception,e:
            self.flashhtml(resultStr%('fail',u'服务器异常，请稍后再操作。',''))
            logging.error(str(e))
            return

class ReplayWeiNote(Page):
    '''
    1.对跟帖的回复
    2.对回复的回复
    '''
    def post(self):
        weinotereplayid=self.request.get('weinotereplayid','')
        content=self.request.get('content','')
        userid=self.request.get('userid','')
        to_userid=self.request.get('to_userid','')
        if not weinotereplayid or not content or not userid:
            self.flashhtml(resultStr%('fail',u'内容、帖子号、用户号为必填项。',''))
            return
        try:
            replay={'userid':userid,'to_userid':to_userid,'content':content,'updateTime':datetime.datetime.utcnow()+timezone}
            weinotereplay=WeiNoteReplay.get_by_id(int(weinotereplayid))
            if weinotereplay:
                weinotereplay.replay.append(json.dumps(replay))
                weinotereplay.put()
                memcache.set('weinotereplayid'+str(weinotereplay.key().id()),weinotereplay,36000)
                self.flashhtml(resultStr%('success',u'回复帖子成功。',''))
                return
            else:
                self.flashhtml(resultStr%('fail',u'回复失败，帖子不存在。',''))
                return
        except Exception,e:
            self.flashhtml(resultStr%('fail',u'服务器异常，请稍后再操作。',''))
            logging.error(str(e))
            return
#        username=self.request.get('username','')
#        to_username=self.request.get('to_username','')

        pass

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    '''
    上传图片
    '''
    def post(self):
        upload_files = self.get_uploads('pic')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class QueryWeiNote(Page):
    '''
    1.查询某个群下的主题贴
    2.根据主题贴查询下面的跟帖 和 回复

    分页显示
    '''
    def get(self):
        groupid=self.request.get('groupid','')
        weinoteid=self.request.get('weinoteid','')
        weinotereplayid=self.request.get('weinotereplayid','')
        start=self.request.get('start',0)
        limit=self.request.get('limit',20)
        start=int(start)
        limit=int(limit)
        if groupid:

            return
        if weinoteid:
            return
        if weinotereplayid:
            return


class DoWeiNote(Page):
    '''
    1.踩贴、顶贴
    所有操作都消耗积分
    '''
    def get(self):
        pass

class GroupUserInfo(Page):
    '''
    1.用户积分信息查询（根据群查）
    '''
    def get(self):
        pass

