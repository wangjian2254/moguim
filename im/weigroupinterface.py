#coding=utf-8
#author:u'王健'
#Date: 13-3-21
#Time: 下午6:51
import urllib
from tools.page import Page
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

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
        pass

class ReplayWeiNote(Page):
    '''
    1.对跟帖的回复
    2.对回复的回复
    '''
    def get(self):
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
        pass


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

