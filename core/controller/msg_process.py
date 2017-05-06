# -*- coding: utf-8 -*-
import os
import os.path
import json
import uuid
import time
import random
import string
import hashlib
import urllib
import copy
from functools import partial
import logging
import pprint


import tornado
import tornado.web
import tornado.escape
import tornado.websocket
import tornado.httpclient

from setting import settings
from setting import conn

from chat_mgr import chat_mgr

from datetime import datetime


from base import WebRequest
from base import WebSocket


import tornado.web
import tornado.escape
from tornado.escape import json_encode, json_decode, url_escape
from tornado import gen


import xmltodict

from weixin_jssdk import WeixinJSSDK

import nomagic.auth
from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc





logger = logging.getLogger(__name__)

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc


"""
data model
"""
from order_m import order_m

# NEW_ORDER = 0
# SUBMITED = 1
# IN_PROCESS = 2
# DELIVERY = 3
# COMPLETE = 4
# CANCELLED = 5

users = {
    "user_id": {
        "order_ids": [],
        "clients": set()
    }
}

orders = {
    # "xxx": {
    #     "order_id": "xxx",
    #     "add": "home",
    #     "tel": "tel",
    #     "user_id": "",
    #     "seats": 4,
    # }
}

message_queue = []


class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime):  
            return obj.__str__()  
        return json.JSONEncoder.default(self, obj)  


class MessageHandler(tornado.web.RequestHandler):
    MESSAGE_SIGNATURE_TOKEN = "newtest"
    USER_INFO_URL           = "https://api.weixin.qq.com/cgi-bin/user/info"

    chat_mgr_m = chat_mgr()

    def check_message_signature(self):
        signature = self.get_argument("signature", None)
        timestamp = self.get_argument("timestamp", None)
        nonce = self.get_argument("nonce", None)
        
        if signature and timestamp and nonce:
            param = sorted([self.MESSAGE_SIGNATURE_TOKEN, timestamp, nonce])
            sha = hashlib.sha1("".join(param)).hexdigest()
            if sha == signature:
                return True
        return False

    @gen.coroutine
    def post(self):
        print "recv message signature"

        if not self.check_message_signature():
            print "check failed"
            self.finish()
            return

        #logger.info(self.request.body)
        request = xmltodict.parse(self.request.body)
        print request
        to_user_name = request['xml']['FromUserName']
        from_user_name = request['xml']['ToUserName']
        create_time = int(time.time())

        weixin_openid = to_user_name
        login_openid = "weixin:%s" % weixin_openid
        content_type = "text"

        if request['xml'].get('Event', "") in ["subscribe", "SCAN"]:
            content = u'欢迎您关注'
            yield WeixinJSSDK.get_value(self.request.full_url())
            access_token = WeixinJSSDK.access_token

            http_client = tornado.httpclient.AsyncHTTPClient()
            url = '%s?access_token=%s&openid=%s&lang=zh_CN' % (self.USER_INFO_URL, access_token, weixin_openid)
            response = yield http_client.fetch(url)
            data = json_decode(response.body)
            data['dd_type'] = "ddgongzhonghao";
            weixin_unionid = data.get('openid', '')
            login_unionid = "unionid:%s" % weixin_unionid

            print "login unionid" + login_unionid

            user_id = nomagic.auth.get_user_id_by_login(login_unionid)
            if user_id:
                nomagic.auth.update_user(user_id, {'weixin_data': data, 'weixin': weixin_openid, 'name': data.get('nickname', '')})
                user_id_by_openid = nomagic.auth.get_user_id_by_login(login_openid)
                if not user_id_by_openid:
                    assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_openid, user_id)

            else:
                user_id = nomagic.auth.get_user_id_by_login(login_openid)
                if user_id:
                    nomagic.auth.update_user(user_id, {'weixin_data': data, 'weixin': weixin_openid, 'name': data.get('nickname', '')})
                else:
                    user_id, user = nomagic.auth.create_user({'weixin_data': data, 'weixin': weixin_openid, 'name': data.get('nickname', '')})
                    assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_openid, user_id)

                if weixin_unionid:
                    assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_unionid, user_id)

        user_digital_id = ""
        index_login = conn.get("SELECT * FROM index_login WHERE login = %s", login_openid)
        if index_login:
            user_digital_id = index_login["id"]

        elif request['xml'].get('Event', "") == "unsubscribe":
            self.finish()
            return


        if request['xml'].get('MsgType') == "text" or  request['xml'].get('MsgType') == "voice" or request['xml'].get('MsgType') == "image" or request['xml'].get('MsgType') == "video":

            user_id = nomagic.auth.get_user_id_by_login("weixin:" + request['xml']['FromUserName'])

            user = get_user(user_id)

            weixin_name  = user.get("name")

            http_client = tornado.httpclient.AsyncHTTPClient()

            data_send = ""

            if  request['xml'].get('MsgType') == "text":

                if "/::)" in request['xml']['Content'][0:5]:
                    print request['xml']['Content'][4:]

                    group_id = self.chat_mgr_m.get(request['xml']['FromUserName'])
                    if group_id != None:
                        self.chat_mgr_m.out(request['xml']['FromUserName'])
                        self.chat_mgr_m.delete(group_id, request['xml']['FromUserName'])

                    self.chat_mgr_m.add(request['xml']['Content'][4:], request['xml']['FromUserName'])
                    self.chat_mgr_m.join(request['xml']['FromUserName'], request['xml']['Content'][4:])

                    content = u'欢迎进 %s房' %  request['xml']['Content'][4:]

                    response = u"""<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                        </xml>""" % (to_user_name, from_user_name, create_time, content)

                    self.finish(response)
                    return

                elif  "/::X" in request['xml']['Content'][0:5]:
                    group_id = self.chat_mgr_m.get(request['xml']['FromUserName'])
                    if group_id == None:
                        group_id = '' 
                    self.chat_mgr_m.out(request['xml']['FromUserName'])
                    self.chat_mgr_m.delete(group_id, request['xml']['FromUserName'])

                    content = u'欢迎退%s房' %  group_id

                    response = u"""<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                        </xml>""" % (to_user_name, from_user_name, create_time, content)
                    self.finish(response)
                    return
                else:
                    group_id = self.chat_mgr_m.get(request['xml']['FromUserName'])
                    members = self.chat_mgr_m.members(group_id)

                    for m in members:
                        if m !=  request['xml']['FromUserName']:
                    
                            data = u'{ \
                                    "touser": "%s",\
                                    "msgtype":"text",\
                                    "text":\
                                    {\
                                        "content":"%s"\
                                    }\
                                    }' % (m, weixin_name + " : " + request['xml']['Content'])
                            data_send = data

                            access_token = WeixinJSSDK.access_token

                            url = u"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" %  access_token

                            response = yield http_client.fetch(url, method='POST', body=data_send)

                    self.finish()
                    return

            if  request['xml'].get('MsgType') in ["image", "video", "voice"]:

                group_id = self.chat_mgr_m.get(request['xml']['FromUserName'])
                members = self.chat_mgr_m.members(group_id)

                logger.info(members)
                logger.info(request['xml']['FromUserName'])

                for m in members:

                    if m !=  request['xml']['FromUserName']:

                        data = u'{ \
                                "touser": "%s",\
                                "msgtype":"text",\
                                "text":\
                                {\
                                    "content":"%s"\
                                }\
                                }' % (m, weixin_name + " : " + request['xml'].get('MsgType'))
                        data_send = data

                        access_token = WeixinJSSDK.access_token

                        url = u"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" %  access_token

                        response = yield http_client.fetch(url, method='POST', body=data_send)

                        data = u'{ \
                                "touser": "%s",\
                                "msgtype":"%s",\
                                "%s":\
                                    {\
                                     "media_id":"%s"\
                                    }\
                                }' % (m, request['xml'].get('MsgType'), request['xml'].get('MsgType'), request['xml']['MediaId'])


                        data_send = data

                        logger.info(data_send)
                        
                        access_token = WeixinJSSDK.access_token

                        url = u"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" %  access_token

                        logger.info(url)
                        response = yield http_client.fetch(url, method='POST', body=data_send)

                self.finish()
                return


        if request['xml'].get('EventKey'):
            if (request['xml'].get('EventKey',"").startswith("qrscene_") and request['xml'].get('Event',"").startswith("subscribe")) or (request['xml'].get('EventKey') and request['xml'].get('Event',"") == "SCAN"):
                scene_id = int(request['xml'].get('EventKey',"").replace("qrscene_",""))
                pass
                # stage_plan = conn.get("SELECT doc_id FROM stage_plan WHERE id = %s", scene_id)
                # if stage_plan:
                #     content_type = "news"
                #     doc_id = stage_plan["doc_id"]
                #     doc = get_doc(doc_id)
                #
                #     title = doc.get("title",u"微社群")
                #     content = u"""您已经预约活动 <a href="http://www.qishu.co/%s">%s</a>""" % (doc_id, title)
                #     description = u"您已经预约活动，记得点击进入查看"
                #     doc_img_url = doc.get('doc_img_url', u'http://www.qishu.co/static/img/stage_audio/weixin_notify.jpg')
                #     url = u"http://www.qishu.co/%s" % doc_id
                #
                #     to_user_name_have_doc_id = conn.get("SELECT doc_id FROM stage_notification WHERE doc_id = %s and open_id = %s",doc_id, to_user_name)
                #     if not to_user_name_have_doc_id:
                #         assert conn.execute_rowcount("INSERT INTO stage_notification (doc_id, open_id, sent) VALUES(%s, %s, 0)", doc_id, to_user_name)

        if content_type == "news":
            response = u"""<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[news]]></MsgType>
                <ArticleCount>1</ArticleCount>
                <Articles>
                <item>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[%s]]></Description>
                <PicUrl><![CDATA[%s]]></PicUrl>
                <Url><![CDATA[%s]]></Url>
                </item>
                </Articles>
                </xml>""" % (to_user_name, from_user_name, create_time, title, description, doc_img_url, url)
        else:
            response = ""
            #response = u"""<xml>
            #    <ToUserName><![CDATA[%s]]></ToUserName>
            #    <FromUserName><![CDATA[%s]]></FromUserName>
            #    <CreateTime>%s</CreateTime>
            #    <MsgType><![CDATA[text]]></MsgType>
            #    <Content><![CDATA[%s]]></Content>
            #    </xml>""" % (to_user_name, from_user_name, create_time, content)
        self.finish(response)

    def get(self):
        if self.check_message_signature():
            echostr = self.get_argument("echostr")
            self.finish(echostr)


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        print "-------------"
        print self.request.files['file'][0].keys()
        print self.request.files['file'][0]['content_type']

        print "-------------"

        for x in range(0, len(self.request.files['file'])):
            file1 = self.request.files['file'][x]
            original_fname = self.request.arguments['filename'][0][9:]
            print original_fname
            output_file = open("/home/cccloud/git/dada/soa/public/myapp/www/img/" + original_fname, 'wb')
            output_file.write(self.request.files['file'][x]['body'])

        self.finish("")

class WeixinJoinHandler(WebRequest):
    def post(self):
        
        chat_mgr_m = chat_mgr()

        self.user_id = self.current_user.get("id")

        user = get_user(self.user_id)
        openid = user.get("weixin")

        data     = json.loads(self.request.body)
        group_id_new = data['group_id']

        group_id = chat_mgr_m.get(openid)
        if group_id != None:
            chat_mgr_m.out(openid)
            chat_mgr_m.delete(group_id, openid)

        chat_mgr_m.add(group_id_new, openid)
        chat_mgr_m.join(openid, group_id_new)

        self.finish()

class WeixinOutHandler(WebRequest):
    def post(self):

        chat_mgr_m = chat_mgr()

        self.user_id = self.current_user.get("id")

        user = get_user(self.user_id)
        openid = user.get("weixin")

        group_id = chat_mgr_m.get(openid)
        if group_id == None:
            group_id = '' 
        chat_mgr_m.out(openid)
        chat_mgr_m.delete(group_id, openid)

        self.finish()

class WeixinConfigHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        print data
        weixin_url = data['weixin_url']
        WeixinJSSDK.get_value(weixin_url)

        res = {
                "debug": False,
                "appId": 'wx7f638d2d85dc480f',
                "signature": WeixinJSSDK.signature,
                "timestamp": WeixinJSSDK.timestamp,
                "nonceStr": WeixinJSSDK.nonceStr,
                "jsApiList": ['onMenuShareTimeline', 'onMenuShareAppMessage', 'chooseImage', 'uploadImage']
                }

        self.finish(res)


class WeixinInfo():
    @gen.coroutine
    def send(self, appid, message):

        http_client = tornado.httpclient.AsyncHTTPClient()

        data = u'{ \
                "touser": "%s",\
                "msgtype":"text",\
                "text":\
                {\
                    "content":"%s"\
                }\
                }' % (appid,  message)

        data_send = data

        access_token = WeixinJSSDK.access_token

        url = u"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" %  access_token

        response = yield http_client.fetch(url, method='POST', body=data_send)
