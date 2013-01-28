#coding=utf-8
#
from im.datingmanage import daTingNoteDel, daTingNote, daTingNoteList
from im.groupinterface import CreateGroup, JoinGroup,  TopNote, DoNote, PutReplay, DelNote, CreateNote, SearchGroup, UserInfo, ShowImg, DeleteNote, DoHotNote
from im.groupinterfacemanage import CreateGroupM, NoteListM, CreateNoteM, GroupListM, DelNoteM, TopNoteM, Login, Top, Menu,PutAdNote, DoingAdNote, JingPai, RemoveGroupM,GroupInfo, DelNoteImgM
from im.gupiaointerface import SearchGuPiao, NeedSyncGuPiao, DeleteNeedSyncGuPiao, JoinGuPiao, SyncGuPiao
from im.rssinterface import RssMsg, SyncGroup
from im.groupinterface import  Rssjson

__author__ = u'王健'
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
from im.interface import Index, InfoAll, InfoUpdate, DelFriend, Search, SendSay, UpdateInfo, AddFriend, GroupHtml, PrintOnline


app = webapp2.WSGIApplication([
    ('/', Login),
    ('/login', Login),
    ('/index', Index),
    ('/top',Top),
    ('/menu',Menu),
    #####################
    ('/group', GroupHtml),
    ('/userinfo', UserInfo),
    ('/groupinfo', GroupInfo),
#    ('/(\d+)/(\d+)/(\d+)/(j\d+)[/]{0,1}', listHaHa),
#    ('/(\d+)/(\d+)[/]{0,1}', newHaHa),
#    ('/getHaHa', getHaHa),
#    ('/check', checkHaHa),
    ('/InfoUpdate',InfoUpdate),
    ('/InfoAll',InfoAll),
    ('/DelFriend',DelFriend),
    ('/AddFriend',AddFriend),
    ('/Search',Search),
    ('/SendSay',SendSay),
    ('/UpdateInfo',UpdateInfo),
####################有关群的新接口
    ('/CreateGroup',CreateGroup),#
    ('/JoinGroup',JoinGroup),#
    ('/SearchGroup',SearchGroup),#
    ('/CreateNote',CreateNote),#
    ('/DelNote',DelNote),#
    ('/PutReplay',PutReplay),#
    ('/DoNote',DoNote),#
    ('/TopNote',TopNote),#
    ('/PutAdNote',PutAdNote),#
    ('/DoingAdNote',DoingAdNote),#
#    ('/DeleteNote',DeleteNote),#
    ('/DoHotNote',DoHotNote),#定期保存热帖
###################################
##########################有关股票的接口
    ('/SearchGuPiao',SearchGuPiao),#查找股票
    ('/SyncGuPiao',SyncGuPiao),#同步股票数据
    ('/NeedSyncGuPiao',NeedSyncGuPiao),#需要同步的股票
    ('/JoinGuPiao',JoinGuPiao),#订阅股票
    ('/DeleteNeedSyncGuPiao',DeleteNeedSyncGuPiao),#删除需要同步的股票
###################################

    ('/RssMsg',RssMsg),#
    ('/SyncGroup',SyncGroup),#
    ('/downLoad', ShowImg),

############################管理界面

    ('/CreateGroupM',CreateGroupM),#
    ('/GroupListM',GroupListM),#
    ('/CreateNoteM',CreateNoteM),#
    ('/RemoveGroupM',RemoveGroupM),#
    ('/NoteListM',NoteListM),#
    ('/DelNoteM',DelNoteM),#
    ('/DelNoteImgM',DelNoteImgM),#
    ('/TopNoteM',TopNoteM),#
    ('/PutAdNote',PutAdNote),#
    ('/JingPai',JingPai),#
    ('/daTingNoteList',daTingNoteList),#
    ('/daTingNote',daTingNote),#
    ('/daTingNoteDel',daTingNoteDel),#
############################### 生成rss json


    (r'/rssjson',Rssjson),
    (r'/printOnline',PrintOnline),
#    ('/PubWeibo',PubWeib),



                              ],
                                         debug=True)
def main():
    pass

#    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
