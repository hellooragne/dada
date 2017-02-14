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


class DateEncoder(json.JSONEncoder ):  
    def default(self, obj):  
        if isinstance(obj, datetime):  
            return obj.__str__()  
        return json.JSONEncoder.default(self, obj)  

class OrderHandler(WebRequest):
    def get(self):
        if not self.current_user:
            self.redirect("/auth/weixin?redirect=/order")
            return
        self.user_id = self.current_user.get("id")
        self.user = get_user(self.user_id)
        if not self.user.get("mobile"):
            self.redirect("/bind_community_mobile")
            return
        community_id = self.user.get("community_id")
        self.community = {}
        if community_id:
            self.community = conn.get("SELECT * FROM communities WHERE id = %s", community_id)
        self.render("../template/order/order.htm")

class StatusAPIHandler(WebRequest):
    def post(self):
        global message_queue, users, orders
        if not self.current_user:
            return

        self.user_id = self.current_user.get("id")
        timestamp = self.get_argument("timestamp", "")
        if timestamp:
            new_messages = [message for message in message_queue if message["timestamp"] > float(timestamp)]
            if new_messages:
                self.finish(new_messages[0])
            else:
                self._auto_finish = False

                user = users.get(self.user_id, {})
                clients = user.setdefault("clients", set())
                clients.add(self)
                users[self.user_id] = user
                # order_ids = user.get("order_ids", [])
                # for order_id in order_ids:
                #     user_id = orders[order_id]["user_id"]
                #     clients = users[user_id].get("clients", set())
                #     clients.add(self)
                #     users[user_id]["clients"] = clients
        else:
            user = users.get(self.user_id, {})
            # order_ids = user.get("order_ids", [])
            self.finish({"orders": [order for order in orders.values()], "timestamp": time.time()})

    def on_connection_close(self):
        global message_queue, users, orders
        user = users.get(self.user_id, {})
        clients = user.setdefault("clients", set())
        if self in clients:
            clients.remove(self)
        users[self.user_id] = user

        self.finish()

class NewAPIHandler(WebRequest):
    def post(self):
        global users, orders, message_queue

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        user = users.get(user_id, {})
        order_ids = user.get("order_ids", [])

        print "add to db"
        if len(order_ids) < 1:
            order_id = uuid.uuid4().hex
            orders[order_id] = {k:v[0] for k, v in self.request.body_arguments.iteritems()}
            orders[order_id]["order_id"] = order_id
            orders[order_id]["user_id"] = user_id

            order_ids.insert(0, order_id)
            user["order_ids"] = order_ids
            users[user_id] = user


        #add to db
	    order_model = order_m()
	    data = json.loads(self.request.body)
	    order_model.add_order(data)

        message = {"orders": [orders[order_id]], "timestamp": time.time()}
        message_queue.append(message)

        for user in users.values():
            for client in user.get("clients", set()):
                client.finish(message)
            user["clients"] = set()

        pprint.pprint(users)
        self.finish(orders[order_id])



class CancelAPIHandler(WebRequest):
    def post(self):
        global users, orders, message_queue
        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        user = users.get(user_id, {})
        order_ids = user.get("order_ids", [])
        if len(order_ids) >= 1:
            order_id = order_ids.pop(0)
            order = orders.pop(order_id)
            user["order_ids"] = order_ids
            users[user_id] = user

            #add to db
	    order_model = order_m()
	    data = json.loads(self.request.body)
	    order_model.disable_order(data)

        message = {"order_to_cancel": order, "timestamp": time.time()}
        for user in users.values():
            for client in user.get("clients", set()):
                client.finish(message)
            user["clients"] = set()

        self.finish({})


class MessageHandler(tornado.web.RequestHandler):
    MESSAGE_SIGNATURE_TOKEN = "test"
    USER_INFO_URL           = "https://api.weixin.qq.com/cgi-bin/user/info"

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

        if not self.check_message_signature():
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
        #content = u'欢迎您关注"美天保养"'
        content_type = "text"
        if request['xml'].get('MsgType', "") in ["voice", "text"] or request['xml'].get('Event', "") in ["subscribe", "SCAN"]:
            yield WeixinJSSDK.get_value(self.request.full_url())
            access_token = WeixinJSSDK.access_token

            http_client = tornado.httpclient.AsyncHTTPClient()
            url = '%s?access_token=%s&openid=%s&lang=zh_CN' % (self.USER_INFO_URL, access_token, weixin_openid)
            print url
            response = yield http_client.fetch(url)
            data = json_decode(response.body)
            weixin_unionid = data.get('unionid', '')
            login_unionid = "unionid:%s" % weixin_unionid

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

        if request['xml'].get('Event', "") in ["subscribe", "SCAN"]:
            content = u'欢迎您关注"美天保养", 您的用户号是 %s' % user_id

        elif request['xml'].get('Event', "") == "unsubscribe":
            self.finish()
            return

        elif request['xml'].get('MsgType') == "voice":
            assert request['xml']['Format'] == "amr"
            media_id = request['xml']['MediaId']

            recognition = request['xml'].get('Recognition', '')
            logger.info(recognition)

            if index_login:
                if recognition:
                    content = u'"%s" 如有误, 请再讲一遍' % recognition

                    user_id = index_login["entity_id"]
                    user = get_user(user_id)
                    community_id = user.get("community_id", "0")
                    tasks = conn.query("SELECT * FROM tasks WHERE user_id = %s AND status = 0", user_id)
                    if tasks:
                        task_id = tasks[0]["id"]
                        conn.execute("UPDATE tasks SET voice = %s WHERE id = %s", recognition, task_id)
                    else:
                        conn.execute("INSERT INTO tasks (license, content, voice, datetime, user_id, community_id) VALUES ('', %s, %s, '0000-01-01 00:00:00', %s, %s)", "", recognition, user_id, community_id)

                else:
                    content = u'对比起, 请再讲一遍'
            else:
                content = u'您还没有签约美天保养, 签约时请提供用户号 %s' % user_digital_id

        elif request['xml'].get('MsgType') == "text":


            http_client = tornado.httpclient.AsyncHTTPClient()

            data = {
                    "touser": request['xml']['FromUserName'],
                    "msgtype":"text",
                    "text":
                    {
                        "content":"Hello World"
                    }
                    }
            data_send = urllib.urlencode(data)

            yield WeixinJSSDK.get_value(self.request.full_url())
            access_token = WeixinJSSDK.access_token

            url = u"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" %  access_token

            logger.info(url)
            response = yield http_client.fetch(url, method='POST', body=data_send)

            logger.info(response.body)
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
            response = u"""<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>""" % (to_user_name, from_user_name, create_time, content)
        self.finish(response)

    def get(self):
        if self.check_message_signature():
            echostr = self.get_argument("echostr")
            self.finish(echostr)

