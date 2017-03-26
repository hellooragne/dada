# -*- coding: utf-8 -*-
import logging
import urllib
import hashlib
import time
import uuid

import tornado.web
import tornado.escape
import tornado.httpclient
from tornado.escape import json_encode, json_decode, url_escape
from tornado import gen

from base import WebRequest

import auth
import xmltodict
from weixin_jssdk import WeixinJSSDK

from setting import settings
from setting import conn

from urllib import urlencode
from urllib import quote 

import nomagic.auth
from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc

logger = logging.getLogger(__name__)

class MessageHandler(tornado.web.RequestHandler):
    MESSAGE_SIGNATURE_TOKEN = "mSSeitiSWH92"
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
        logger.info(self.request.body)
        request = xmltodict.parse(self.request.body)
        to_user_name = request['xml']['FromUserName']
        from_user_name = request['xml']['ToUserName']
        create_time = int(time.time())

        weixin_openid = to_user_name
        login_openid = "weixin:%s" % weixin_openid
        content = u'欢迎您关注"美天保养"'
        content_type = "text"
        if request['xml'].get('MsgType', "") in ["voice", "text"] or request['xml'].get('Event', "") in ["subscribe", "SCAN"]:
            yield WeixinJSSDK.get_value(self.request.full_url())
            access_token = WeixinJSSDK.access_token

            http_client = tornado.httpclient.AsyncHTTPClient()
            url = '%s?access_token=%s&openid=%s&lang=zh_CN' % (self.USER_INFO_URL, access_token, weixin_openid)
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
            message_table = {
                u'五环': u'你比四环多一环',
            }
            content = message_table.get(request['xml']['Content'], u'您还没有签约美天保养, 签约时请提供用户号 %s' % user_digital_id)

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


class AuthHandler(WebRequest):
    WEIXIN_AUTH_URL         = "https://open.weixin.qq.com/connect/oauth2/authorize"
    WEIXIN_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    REQUEST_CODE_URL        = "http://meitian.meishizhibo.net/auth/weixin"

    def get_authorization_code(self, scope):
        args = {
            'appid'            : settings['WeixinAppId'],
            'redirect_uri'     : self.REQUEST_CODE_URL+"?redirect="+url_escape(self.redirect_url),
            'response_type'    : 'code',
            'scope'            : scope,
            'state'            : 'STATE'
        }
        url = '%s?%s#wechat_redirect' % (self.WEIXIN_AUTH_URL, urllib.urlencode(sorted(args.items())))
        return url

    @gen.coroutine
    def get(self):
        code = self.get_argument('code', None)
        self.redirect_url = self.get_argument("redirect", "/")
        if not code:
            self.redirect(self.get_authorization_code('snsapi_userinfo'))
            return

        #Use code fetch weixin access_token
        http_client = tornado.httpclient.AsyncHTTPClient()
        args = {
            'appid'      : settings['WeixinAppId'],
            'secret'     : settings['WeixinAppSecret'],
            'code'       : code,
            'grant_type' : 'authorization_code'
        }
        url = '%s?%s' % (self.WEIXIN_ACCESS_TOKEN_URL, urllib.urlencode(sorted(args.items())))
        response = yield http_client.fetch(url)

        #Use openid&access_token get user_info
        data = json_decode(response.body)


        weixin_openid = data.get('openid')
        if not weixin_openid:
            self.redirect("/auth/weixin?redirect=%s" % url_escape(self.redirect_url))
            return

        args = {
            'access_token': data['access_token'],
            'openid'      : data['openid'],
            'lang'        : 'zh_CN'
        }

        url = 'https://api.weixin.qq.com/sns/userinfo?' + urllib.urlencode(sorted(args.items()))
        response = yield http_client.fetch(url)
        data = json_decode(response.body)
        weixin_unionid = data.get('unionid', '')
        login_openid = "weixin:%s" % weixin_openid
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

        self.set_secure_cookie("user", json_encode({"id": user_id}))
        self.redirect(self.redirect_url)

#hmeng
class ApiWeixinRedirect(WebRequest):
    def get(self):
        code = self.get_argument('code', None)
        self.redirect(quote("/static/myapp/www/#/app/weixin_login/" + code))

#hmeng
class ApiWeixinLogin(WebRequest):
    WEIXIN_AUTH_URL         = "https://open.weixin.qq.com/connect/oauth2/authorize"
    WEIXIN_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    REQUEST_CODE_URL        = "http://meitian.meishizhibo.net/auth/weixin"

    def get_authorization_code(self, scope):
        args = {
            'appid'            : settings['WeixinAppId'],
            'redirect_uri'     : self.REQUEST_CODE_URL+"?redirect="+url_escape(self.redirect_url),
            'response_type'    : 'code',
            'scope'            : scope,
            'state'            : 'STATE'
        }
        url = '%s?%s#wechat_redirect' % (self.WEIXIN_AUTH_URL, urllib.urlencode(sorted(args.items())))
        return url

    @gen.coroutine
    def get(self):
        code = self.get_argument('code', None)
        logger.info("code: " + code)
        self.redirect_url = self.get_argument("redirect", "/")
        if not code:
            self.redirect(self.get_authorization_code('snsapi_userinfo'))
            return

        #Use code fetch weixin access_token
        http_client = tornado.httpclient.AsyncHTTPClient()
        args = {
            'appid'      : settings['WeixinAppId'],
            'secret'     : settings['WeixinAppSecret'],
            'code'       : code,
            'grant_type' : 'authorization_code'
        }
        url = '%s?%s' % (self.WEIXIN_ACCESS_TOKEN_URL, urllib.urlencode(sorted(args.items())))
        response = yield http_client.fetch(url)

        data = json_decode(response.body)
        weixin_openid = data.get('openid')
        logger.info(data)

        if not weixin_openid:
            return

        args = {
            'access_token': data['access_token'],
            'openid'      : data['openid'],
            'lang'        : 'zh_CN'
        }
        url = 'https://api.weixin.qq.com/sns/userinfo?' + urllib.urlencode(sorted(args.items()))
        response = yield http_client.fetch(url)
        data = json_decode(response.body)
        logger.info("user_data : " + str(data))

        weixin_unionid = data.get('unionid', '')
        login_openid = "weixin:%s" % weixin_openid
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

        self.set_secure_cookie("user", json_encode({"id": user_id}))
        data['user_id'] = user_id
        self.finish(data)


class SimpleAuthHandler(WebRequest):
    WEIXIN_AUTH_URL         = "https://open.weixin.qq.com/connect/oauth2/authorize"
    WEIXIN_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    USER_INFO_URL           = "https://api.weixin.qq.com/cgi-bin/user/info"
    REQUEST_CODE_URL        = "http://meitian.meishizhibo.net/auth/simple_weixin"

    def get_authorization_code(self, scope):
        args = {
            'appid'            : settings['WeixinAppId'],
            'redirect_uri'     : self.REQUEST_CODE_URL+"?redirect="+url_escape(self.redirect_url),
            'response_type'    : 'code',
            'scope'            : scope,
            'state'            : 'STATE'
        }
        url = '%s?%s#wechat_redirect' % (self.WEIXIN_AUTH_URL, urllib.urlencode(sorted(args.items())))
        return url

    @gen.coroutine
    def get(self):
        code = self.get_argument('code', None)
        self.redirect_url = self.get_argument("redirect", "/")

        
        if not code:
            self.redirect(self.get_authorization_code('snsapi_base'))
            return

        #Use code fetch weixin access_token
        http_client = tornado.httpclient.AsyncHTTPClient()
        args = {
            'appid'      : settings['WeixinAppId'],
            'secret'     : settings['WeixinAppSecret'],
            'code'       : code,
            'grant_type' : 'authorization_code'
        }
        url = '%s?%s' % (self.WEIXIN_ACCESS_TOKEN_URL, urllib.urlencode(sorted(args.items())))
        response = yield http_client.fetch(url)

        data = json_decode(response.body)
        logger.info(data)
        weixin_openid = data.get('openid')
        if not weixin_openid:
            self.redirect("/auth/simple_weixin?redirect=%s" % tornado.escape.url_escape(self.redirect_url))
            return

        yield WeixinJSSDK.get_value(self.request.full_url())
        access_token = WeixinJSSDK.access_token

        url = '%s?access_token=%s&openid=%s&lang=zh_CN' % (self.USER_INFO_URL, access_token, weixin_openid)
        response = yield http_client.fetch(url)
        data = json_decode(response.body)
        login_openid = "weixin:%s" % weixin_openid
        weixin_unionid = data.get('unionid')
        login_unionid = "unionid:%s" % weixin_unionid

        user_data = {'weixin': weixin_openid}
        if data.get("subscribe"):
            user_data["weixin_data"] = data

        user_id = nomagic.auth.get_user_id_by_login(login_unionid) if weixin_unionid else None
        if user_id:
            update_user(user_id, user_data)
            user_id_by_openid = nomagic.auth.get_user_id_by_login(login_openid)
            if not user_id_by_openid:
                assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_openid, user_id)

        else:
            user_id = nomagic.auth.get_user_id_by_login(login_openid)
            if user_id:
                update_user(user_id, user_data)
            else:
                user_id, user = nomagic.auth.create_user(user_data)
                assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_openid, user_id)

            if weixin_unionid:
                assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_unionid, user_id)

        self.set_secure_cookie("user", json_encode({"id": user_id, "v":2}), domain=settings.get("cookie_domain"))
        # current_logins = conn.query("SELECT * FROM index_login WHERE entity_id = %s ORDER BY id ASC", user_id)
        self.redirect(self.redirect_url)


class OAuth2APIHandler(tornado.web.RequestHandler):
    def get(self):
        self._auto_finish = False
        token = self.get_argument("token")

        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch("https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (self.settings.get("WeixinOpenAppId", ""), self.settings.get("WeixinOpenAppSecret", ""), token), callback=self._on_oauth2)

    def _on_oauth2(self, response):
        data = json_decode(response.body)
        access_token = data["access_token"]
        weixin_openid = data.get('openid')
        self.login_openid = "weixin:%s" % weixin_openid

        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch("https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s" % (access_token, weixin_openid), callback=self._on_userinfo)

    def _on_userinfo(self, response):
        #Save user_info
        data = json_decode(response.body)
        weixin_unionid = data.get('unionid')
        login_unionid = "unionid:%s" % weixin_unionid

        user_id = nomagic.auth.get_user_id_by_login(login_unionid)
        if user_id:
            nomagic.auth.update_user(user_id, {'weixin_data': data, 'name': data.get('nickname', '')})
        else:
            user_id = nomagic.auth.get_user_id_by_login(self.login_openid)
            if user_id:
                nomagic.auth.update_user(user_id, {'weixin_data': data, 'name': data.get('nickname', '')})
            else:
                user_id, user = nomagic.auth.create_user({'weixin_data': data, 'name': data.get('nickname', '')})
            assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_unionid, user_id)

        self.set_secure_cookie("user", json_encode({"id": user_id, "v":1}))
        self.finish({"unionid": weixin_unionid, "id": user_id})

        # current_logins = conn.query("SELECT * FROM index_login WHERE entity_id = %s ORDER BY id ASC", user_id)
        # if len(current_logins) <= 1:
        #     self.redirect("/bind_email_mobile?redirect=%s" % tornado.escape.url_escape(self.redirect_url))
        #     return
        # self.redirect(self.redirect_url)

# class LiveAppOAuth2APIHandler(tornado.web.RequestHandler):
#     def get(self):
#         self._auto_finish = False
#         token = self.get_argument("token")
#
#         client = tornado.httpclient.AsyncHTTPClient()
#         client.fetch("https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (self.settings.get("WeixinOpenLiveAppId", ""), self.settings.get("WeixinOpenLiveAppSecret", ""), token), callback=self._on_oauth2)
#
#     def _on_oauth2(self, response):
#         data = json_decode(response.body)
#         access_token = data["access_token"]
#         weixin_openid = data.get('openid')
#         self.login_openid = "weixin:%s" % weixin_openid
#
#         client = tornado.httpclient.AsyncHTTPClient()
#         client.fetch("https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s" % (access_token, weixin_openid), callback=self._on_userinfo)
#
#     def _on_userinfo(self, response):
#         #Save user_info
#         data = json_decode(response.body)
#         weixin_unionid = data.get('unionid')
#         login_unionid = "unionid:%s" % weixin_unionid
#
#         user_id = nomagic.auth.get_user_id_by_login(login_unionid)
#         if user_id:
#             nomagic.auth.update_user(user_id, {'weixin_data': data, 'name': data.get('nickname', '')})
#         else:
#             user_id = nomagic.auth.get_user_id_by_login(self.login_openid)
#             if user_id:
#                 nomagic.auth.update_user(user_id, {'weixin_data': data, 'name': data.get('nickname', '')})
#             else:
#                 user_id, user = nomagic.auth.create_user({'weixin_data': data, 'name': data.get('nickname', '')})
#             assert conn.execute_rowcount("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", login_unionid, user_id)
#
#         self.set_secure_cookie("user", json_encode({"id": user_id, "v":1}))
#         self.finish({"unionid": weixin_unionid, "id": user_id})


class DocPaymentHandler(WebRequest):
    @tornado.gen.coroutine
    def get(self):
        if not self.current_user:
            self.redirect("/auth?redirect=%s" % tornado.escape.url_escape(self.request.uri))
            return

        current_user_id = self.current_user.get("id")
        user = get_user(current_user_id)
        openid = user.get("weixin")
        if not openid:
            self.redirect("/auth/simple_weixin?redirect_url=%s" % tornado.escape.url_escape(self.request.uri))
            return

        self.doc_id = self.get_argument("doc_id")
        doc = get_doc(self.doc_id)

        restrict_users = doc.get("restrict_users", [])
        if current_user_id in restrict_users:
            self.redirect("/%s" % self.doc_id)
            return

        if doc and doc.get("restrict_mode", "") == "payment" and doc.get("restrict_price", "").isdigit():
            self.price = int(doc["restrict_price"])
        self.payment_body = doc.get("payment_body", doc.get("title", "Doc %s" % self.doc_id))

        other_info = json_encode({"ref_id": self.get_argument("ref_id", "")})
        remote_ip = self.request.headers.get("X-Forwarded-For", "").split(", ")[0] or self.request.remote_ip
        trade_no = conn.execute_lastrowid("INSERT INTO payment_weixin (user_id, doc_id, prepay_info, transaction_info, fee, transaction_id, other_info) VALUES (%s, '', '', '', 0, '', %s)", current_user_id, other_info)
        nonce = uuid.uuid4().hex

        output = u"""<xml>
    <appid>%s</appid>
    <attach>doc_%s_user_%s</attach>
    <body>%s</body>
    <mch_id>%s</mch_id>
    <nonce_str>%s</nonce_str>
    <notify_url>http://www.qishu.co/payment/doc_callback</notify_url>
    <openid>%s</openid>
    <out_trade_no>%s</out_trade_no>
    <spbill_create_ip>%s</spbill_create_ip>
    <total_fee>%s</total_fee>
    <trade_type>JSAPI</trade_type>
    <sign>%s</sign>
</xml>""" % (self.settings["WeixinAppId"],
             self.doc_id, current_user_id,
             self.payment_body,
             self.settings["WeixinMerchantId"],
             nonce,
             openid,
             trade_no,
             remote_ip,
             self.price,
             "%s")

        data = xmltodict.parse(output)["xml"]
        del data["sign"]

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        sign = hashlib.md5(temp_str).hexdigest().upper()

        xml = output % sign
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                    url = "https://api.mch.weixin.qq.com/pay/unifiedorder",
                    method = "POST",
                    body = xml)
        response = yield http_client.fetch(request)
        # logger.info(response.body)
        conn.execute("UPDATE payment_weixin SET prepay_info = %s WHERE id = %s", response.body, trade_no)
        result = xmltodict.parse(response.body)["xml"]

        self.prepay_id = result["prepay_id"]
        self.timestamp = str(int(time.time()))
        self.nonce = uuid.uuid4().hex

        data = {
            "appId": self.settings.get("WeixinAppId", ""),
            "nonceStr": self.nonce,
            "timeStamp": self.timestamp,
            "package": "prepay_id=%s" % self.prepay_id,
            "signType": "MD5",
        }

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        self.pay_sign = hashlib.md5(temp_str).hexdigest().upper()

        if doc and doc.get("payment_template"):
            payment_template = doc.get("payment_template")
            self.payment_html = doc.get("payment_html", "")
            self.render("../template/payment_doc_%s.html" % payment_template)
            return

        self.render("../template/payment_doc.htm")

class DocPaymentCallbackHandler(WebRequest):
    def post(self):
        data = xmltodict.parse(self.request.body)["xml"]
        sign = data["sign"]
        del data["sign"]

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        if sign != hashlib.md5(temp_str).hexdigest().upper():
            raise tornado.web.HTTPError(403)
            return

        fee = data["total_fee"]
        transaction_id = data["transaction_id"]
        out_trade_no = data["out_trade_no"]
        _, doc_id, _, user_id = data["attach"].split("_")
        conn.execute("UPDATE payment_weixin SET doc_id = %s, transaction_info = %s, fee = %s, transaction_id = %s WHERE id = %s", doc_id, self.request.body, fee, transaction_id, out_trade_no)

        doc = get_doc(doc_id)
        assert doc and doc["type"] == "doc"
        restrict_users = doc.get("restrict_users", [])
        if user_id not in restrict_users:
            restrict_users.append(user_id)
            doc["restrict_users"] = restrict_users
            update_doc(doc_id, doc)


class PaymentTestHandler(WebRequest):
    @tornado.gen.coroutine
    def get(self):
        if not self.current_user:
            self.redirect("/auth?redirect=%s" % tornado.escape.url_escape(self.request.uri))
            return

        current_user_id = self.current_user.get("id")
        user = get_user(current_user_id)
        openid = user.get("weixin")
        if not openid:
            self.redirect("/auth/simple_weixin?redirect_url=%s" % tornado.escape.url_escape(self.request.uri))
            return

        self.doc_id = self.get_argument("doc_id")
        doc = get_doc(self.doc_id)

        restrict_users = doc.get("restrict_users", [])
        if current_user_id in restrict_users:
            self.redirect("/%s" % self.doc_id)
            return

        if doc and doc.get("restrict_mode", "") == "payment" and doc.get("restrict_price", "").isdigit():
            self.price = int(doc["restrict_price"])

        other_info = json_encode({"ref_id": self.get_argument("ref_id", "")})
        remote_ip = self.request.headers.get("X-Forwarded-For", "").split(", ")[0] or self.request.remote_ip
        trade_no = conn.execute_lastrowid("INSERT INTO payment_weixin (user_id, doc_id, prepay_info, transaction_info, fee, transaction_id, other_info) VALUES (%s, '', '', '', 0, '', %s)", current_user_id, other_info)
        nonce = uuid.uuid4().hex

        output = u"""<xml>
    <appid>%s</appid>
    <attach>doc_%s_user_%s</attach>
    <body>JSAPI支付测试</body>
    <mch_id>%s</mch_id>
    <nonce_str>%s</nonce_str>
    <notify_url>http://beta.qishu.co/payment_test/doc_callback</notify_url>
    <openid>%s</openid>
    <out_trade_no>%s</out_trade_no>
    <spbill_create_ip>%s</spbill_create_ip>
    <total_fee>%s</total_fee>
    <trade_type>JSAPI</trade_type>
    <sign>%s</sign>
</xml>""" % (self.settings["WeixinAppId"],
             self.doc_id, current_user_id,
             self.settings["WeixinMerchantId"],
             nonce,
             openid,
             trade_no,
             remote_ip,
             self.price,
             "%s")

        data = xmltodict.parse(output)["xml"]
        del data["sign"]

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        sign = hashlib.md5(temp_str).hexdigest().upper()

        xml = output % sign
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                    url = "https://api.mch.weixin.qq.com/pay/unifiedorder",
                    method = "POST",
                    body = xml)
        response = yield http_client.fetch(request)
        conn.execute("UPDATE payment_weixin SET prepay_info = %s WHERE id = %s", response.body, trade_no)
        result = xmltodict.parse(response.body)["xml"]

        self.prepay_id = result["prepay_id"]
        self.timestamp = str(int(time.time()))
        self.nonce = uuid.uuid4().hex

        data = {
            "appId": self.settings.get("WeixinAppId", ""),
            "nonceStr": self.nonce,
            "timeStamp": self.timestamp,
            "package": "prepay_id=%s" % self.prepay_id,
            "signType": "MD5",
        }

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        self.pay_sign = hashlib.md5(temp_str).hexdigest().upper()

        if doc and doc.get("payment_template"):
            payment_template = doc.get("payment_template")
            self.payment_html = doc.get("payment_html", "")
            self.render("../template/payment_doc_%s.html" % payment_template)
            return

        self.render("../template/payment_test.htm")

class PaymentCallbackTestHandler(WebRequest):
    def post(self):
        data = xmltodict.parse(self.request.body)["xml"]
        sign = data["sign"]
        del data["sign"]

        temp_str = "&".join(["%s=%s" % (k.encode("utf8"), data[k].encode('utf8')) for k in sorted(data.keys())])
        temp_str += "&key=%s" % self.settings.get("WeixinMerchantKey", "")
        if sign != hashlib.md5(temp_str).hexdigest().upper():
            raise tornado.web.HTTPError(403)
            return

        fee = data["total_fee"]
        transaction_id = data["transaction_id"]
        out_trade_no = data["out_trade_no"]
        _, doc_id, _, user_id = data["attach"].split("_")
        conn.execute("UPDATE payment_weixin SET doc_id = %s, transaction_info = %s, fee = %s, transaction_id = %s WHERE id = %s", doc_id, self.request.body, fee, transaction_id, out_trade_no)

        doc = get_doc(doc_id)
        assert doc and doc["type"] == "doc"
        restrict_users = doc.get("restrict_users", [])
        if user_id not in restrict_users:
            restrict_users.append(user_id)
            doc["restrict_users"] = restrict_users
            update_doc(doc_id, doc)

class ReportPaymentDocRefHandler(WebRequest):
    def get(self):
        if not self.current_user:
            return

        user_id = self.current_user.get("id")
        doc_id = self.get_argument("doc_id")
        doc = get_doc(doc_id)
        if not (user_id in settings.get("admin_user_ids", []) or user_id == doc["owner"]):
            return

        self.successful_payment = conn.query("SELECT * FROM payment_weixin WHERE doc_id = %s AND fee > 0", doc_id)
        for payment in self.successful_payment:
            payment.other_info = json_decode(payment["other_info"]) if payment["other_info"] else {}
            payment.ref_user_id = payment.other_info.get("ref_id", "")
            payment.openid = ""
            if payment.ref_user_id:
                payment.ref_user = get_user(payment.ref_user_id)
                payment.openid = payment.ref_user.get("weixin", "")

        self.render("../template/report_payment_doc_ref.htm")
