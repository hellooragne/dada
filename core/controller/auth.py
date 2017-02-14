# -*- coding: utf-8 -*-
import os
import time
import random
import string
import urlparse
import urllib
import hashlib
import json
import logging
import re
import cStringIO

# import qrcode

import tornado.web
import tornado.template
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpclient
# from tornado.log import gen_log
from tornado.httputil import url_concat

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from setting import settings
from setting import conn

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc

from base import WebRequest

logger = logging.getLogger(__name__)

regex_collect = dict(
    email=re.compile(r"([\w.-]+)@([\w.-]+)"),
    phone=re.compile(r"^1(?:3|4|5|7|8)\d{9}")
)

class QQMixin(tornado.auth.OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://graph.qq.com/oauth2.0/token"
    _OAUTH_AUTHORIZE_URL = "https://graph.qq.com/oauth2.0/authorize"

    @tornado.web.asynchronous
    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        http = tornado.httpclient.AsyncHTTPClient()

        fields = set()
        if extra_fields:
            fields.update(extra_fields)

        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code"
        }

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
            self.async_callback(self._on_access_token, redirect_uri, client_id, client_secret, callback, fields),
            method="POST", body=urllib.urlencode(args))

    def _on_access_token(self, redirect_uri, client_id, client_secret,
                         callback, fields, response):
        args = tornado.escape.parse_qs_bytes(tornado.escape.native_str(response.body))

        #self.finish({"body":response.body, "args":args})
        session = {
            "access_token": args["access_token"][-1],
            "refresh_token": args["refresh_token"][-1],
            "expires_in": args["expires_in"][-1]
        }

        callback(session)


class WeiboMixin(tornado.auth.OAuth2Mixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"

    @tornado.web.asynchronous
    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        http = tornado.httpclient.AsyncHTTPClient()

        fields = set()
        if extra_fields:
            fields.update(extra_fields)

        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code"
        }

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
            self.async_callback(self._on_access_token, redirect_uri, client_id, client_secret, callback, fields),
            method="POST", body=urllib.urlencode(args))

    def _on_access_token(self, redirect_uri, client_id, client_secret,
                         callback, fields, response):
        session = tornado.escape.json_decode(response.body)
        callback(session)


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        redirect_url = self.get_argument("next", "/")

        self.clear_cookie("user")
        self.clear_cookie('weibo_auth')
        self.clear_cookie('tab')
        self.redirect(redirect_url)


class SettingHandler(WebRequest):
    def get(self):
        # print self.current_user
        doc_id = self.get_argument('doc_id', '')
        user_id = self.current_user.get('id', None)
        if user_id:
            self.doc_id = doc_id
            entity_info = get_user(user_id)
            self.login_name = entity_info.get('name')
            # self.login_email = entity_info.get('email')
            # self.login_phone = entity_info.get('mobile')
            # self.login_weixin = entity_info.get('weixin')
            self.login_email = None
            self.login_phone = None
            self.login_weixin = None
            all_current_logins = conn.query("SELECT * FROM index_login WHERE entity_id = %s ORDER BY id ASC", user_id)
            for i in all_current_logins:
                if "@" in i["login"]:
                    self.login_email = i["login"]
                elif "mobile:" in i["login"]:
                    self.login_phone = i["login"]
                    self.login_phone = self.login_phone[10:]
                elif "weixin:" in i["login"]:
                    self.login_weixin = i["login"]
            self.current_headimgurl = entity_info.get('headimgurl',"")
            if self.current_headimgurl:
                self.current_headimgurl = "http://7i7jnw.com1.z0.glb.clouddn.com/%s_%s?imageView2/1/w/200/h/200" % (user_id,self.current_headimgurl)
            else:
                self.current_headimgurl = entity_info.get('weixin_data',{}).get('headimgurl',"")
            self.user_id = user_id

            self.render('../template/setting.html')
        else:
            self.redirect('/')
        return

class SettingNewPasswordAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user.get('id')
        old_password = self.get_argument('old_password')
        new_password = self.get_argument('new_password')
        check_password_update = nomagic.auth.update_user(user_id, {"password0":old_password, "password1":new_password})
        if check_password_update.get('password_updated',False):
            self.clear_cookie("user")
            self.clear_cookie('tab')
            self.finish({})
        else:
            self.finish({'error':'0'})
        return

class SettingNameAPIHandler(WebRequest):
    def get(self):
        self.post()

    def post(self):
        from writing import DocumentData
        if not self.current_user:
            return

        user_id = self.current_user.get('id')
        name = self.get_argument('name')
        check_name_update = nomagic.auth.update_user(user_id, {"name": name})
        return


class LoginAPIHandler(tornado.web.RequestHandler):
    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")

        if "@" in login:
            pass
        elif len(login) == 11:
            login = "mobile:+86%s" % login

        user_id, user = nomagic.auth.get_user_by_login(login)
        if user_id and user and password:
            if user["password"] == hashlib.sha1(password + user.get("salt", "")).hexdigest():
                # more_ids_list=self.current_user.get('more_ids',[])
                more_ids_list=[]
                if not user_id in more_ids_list:
                    more_ids_list.append(user_id)

                self.set_secure_cookie("user", tornado.escape.json_encode({"id": user_id,"more_ids":more_ids_list, "v":1}))
                self.finish({"id": user_id})
                return
            elif user["password"] == hashlib.sha1(user.get("salt", "")).hexdigest() and user.get("mobile_verify_secret", "") == password: #empty password
                more_ids_list=[]
                if not user_id in more_ids_list:
                    more_ids_list.append(user_id)

                self.set_secure_cookie("user", tornado.escape.json_encode({"id": user_id,"more_ids":more_ids_list, "v":1}))
                self.finish({"id": user_id})
                return

        self.finish({'error': 'no such user or wrong password'})
        return
        #raise tornado.web.HTTPError(401, "Auth failed")


class SignupAPIHandler(tornado.web.RequestHandler):
    def post(self):
        if settings.get("invitecode", False):
            invitecode = self.get_argument("invitecode").upper()
            user_invitecode = nomagic.auth.check_invitecode(invitecode)

            if user_invitecode == 0:
                self.finish({'error': 'invitecode not right'}) #invitecode isn\'t right
                return
            elif user_invitecode == 2:
                self.finish({'error': 'invitecode used'}) #invitecode is used
                return
            else:
                self.finish({'error': 'empty'})
                return

        login = self.get_argument("login")
        password = self.get_argument("password")

        user = {}
        user_id = ""
        if "@" in login:
            user = {"email": login, "password": password}
            user["email_verify_secret"] = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
            user_id = nomagic.auth.get_user_id_by_login(login)

        elif len(login) == 11 and login.isdigit():
            user = {"mobile": "+86%s" % login, "password": password}
            user["mobile_verify_secret"] = "".join(random.choice(string.digits) for x in range(6))
            user_id = nomagic.auth.get_user_id_by_login("mobile:+86%s" % login)

        else:
            self.finish({'error': 'bad login'})
            return

        if user_id:
            self.finish({'error': 'duplicated login'})
            return

        user_id, user = nomagic.auth.create_user(user)
        self.set_secure_cookie("user", tornado.escape.json_encode({"id": user_id, "v":1}))

        if settings.get("invitecode", False):
            nomagic.auth.update_invitecode(invitecode, user_id)

        if "@" in login:
            nomagic.docs.apply_invite(user_id, login)

            #send email
            msg = EmailMessage()
            msg.subject = u"齐书邮件验证".encode("utf8")
            email_verify_url = "http://%s/email_verify?user_id=%s&secret=%s" % (self.request.host, user_id, user["email_verify_secret"])
            msg.bodyHtml = self.render_string("../template/validate_sign_up_email.html", email_verify_url = email_verify_url, login = login)
            self.send("info@qishu.co", str(login), msg)


        elif len(login) == 11 and login.isdigit():
            sms_mobile = login
            sms_content = u"齐书云协作 临时密码 %s Qishu.co【齐书】" % user["mobile_verify_secret"]
            sms_dstime = ''                          #为空代表立即发送  如果加了时间代表定时发送  精确到秒
            sms_username = settings["SmsUsername"]   #短信帐号用户名
            sms_password = settings["SmsPassword"]   #短信帐号密码
            sms_productid = settings["SmsProductId"] #内容 676766
            sms_xh = ''                              #留空

            # $url='http://www.ztsms.cn:8800/sendXSms.do?username=用户名&password=密码&mobile=手机号码&content=内容&dstime=&productid=产品ID&xh=';
            sms_url="http://www.ztsms.cn:8800/sendSms.do?username=%s&password=%s&mobile=%s&content=%s&dstime=%s&productid=%s&xh=%s" % (sms_username, sms_password, sms_mobile, urllib.quote(sms_content.encode("utf8")), sms_dstime, sms_productid, sms_xh)
            # print len(sms_url)
            # client = tornado.httpclient.AsyncHTTPClient()
            # client.fetch(sms_url, callback=self.on_response)
            conn.execute("INSERT INTO index_login (login, entity_id) VALUES(%s, %s)", "mobile:+86%s" % login, user_id)

        self.finish({})

    def on_response(self, response):
        if response.error:
            print(response.error)


# class SignupAnonymousAPIHandler(WebRequest):
#     def post(self):
#         if self.current_user:
#             print "user_id", self.current_user["id"]
#             self.finish({"user_id": self.current_user["id"]})
#             return
#         print "new user"
#         user_id, user = nomagic.auth.create_user({"password":""})
#         self.set_secure_cookie("user", tornado.escape.json_encode({"id": user_id, "v":1}))
#
#         self.finish({'user_id': user_id})
#         return


class AuthHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect_url = self.get_argument("redirect", "/")
        # if "Mobile" in self.request.headers.get("User-Agent", "") or \
        #     "Android" in self.request.headers.get("User-Agent", ""):
        #     self.weixin_login = True if "MicroMessenger" in self.request.headers.get("User-Agent", "") else False
        #     self.render("../template/mobile_index.html")
        #     return
        self.render("../template/auth.html")


class SaveCommunityAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user["id"]
        community_id = self.get_argument("community_id")
        user = get_user(user_id)
        assert user.get("type") == "user"

        user["community_id"] = community_id
        update_user(user_id, user)

        self.finish({})


class SaveMobileAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user["id"]
        mobile = self.get_argument("mobile")
        user = get_user(user_id)
        assert user.get("type") == "user"

        user["mobile"] = mobile
        update_user(user_id, user)

        self.finish({})


class LoginWithQRCodeHandler(WebRequest):
    def get(self):
        self.secret = self.get_argument("secret", "")
        if not self.current_user:
            self.redirect("/auth/simple_weixin?redirect=%s" % tornado.escape.url_escape("/login_qrcode?secret=%s" % self.secret))
            return

        if self.secret in LoginWithQRCodeWaitingAPIHandler.login_secrets:
            this = LoginWithQRCodeWaitingAPIHandler.login_secrets[self.secret]
            this.set_secure_cookie("user", tornado.escape.json_encode(self.current_user))
            this.finish({"status": "scanned"})
            del LoginWithQRCodeWaitingAPIHandler.login_secrets[self.secret]

        self.render("../template/qrcode_login.html")

    # def post(self):
    #     if not self.current_user:
    #         return

    #     secret = self.get_argument("secret")
    #     if secret in LoginWithQRCodeWaitingAPIHandler.login_secrets:
    #         this = LoginWithQRCodeWaitingAPIHandler.login_secrets[secret]
    #         this.set_secure_cookie("user", tornado.escape.json_encode(self.current_user))
    #         this.finish({"status": "login"})
    #         del LoginWithQRCodeWaitingAPIHandler.login_secrets[secret]

    #     self.finish()


class LoginWithQRCodeWaitingAPIHandler(WebRequest):
    login_secrets = {}

    @tornado.web.asynchronous
    def post(self):
        self.secret = self.get_argument("secret")
        self.login_secrets[self.secret] = self

    def on_connection_close(self):
        if self.secret in self.login_secrets:
            del self.login_secrets[self.secret]


class LoginQRCodeAPIHandler(WebRequest):
    def get(self):
        secret = self.get_argument("secret")
        img = qrcode.make("http://%s/login_qrcode?secret=%s" % (self.request.host, secret), box_size=6)
        mem = cStringIO.StringIO()
        img.save(mem)
        mem.seek(0)
        self.set_header("Content-Type", "image/png")
        self.finish(mem.read())


class BindCommunityMobileHandler(WebRequest):
    def get(self):
        self.redirect_url = self.get_argument("redirect", "/")
        if not self.current_user:
            self.redirect(self.redirect_url)
            return

        self.user_id = self.current_user.get("id")
        self.user = get_user(self.user_id)
        self.communities = conn.query("SELECT * FROM communities")

        # current_logins = conn.query("SELECT * FROM index_login WHERE entity_id = %s ORDER BY id ASC", self.user_id)
        #
        # self.popup = ["email", "mobile", "password"]
        # for i in current_logins:
        #     if "@" in i["login"]:
        #         self.popup.remove("email")
        #     elif i["login"].startswith("mobile:"):
        #         self.popup.remove("mobile")

        self.render('../template/bind_community_mobile.html')


class BrowserSuggestionHandler(tornado.web.RequestHandler):
    def get(self):
        if "AppleWebKit" in self.request.headers.get("User-Agent", ""):
            self.redirect("/")
            return
        self.render('../template/browser_suggestion.html')


class ForgotPasswordHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('../template/forgot_password.html')

    def post(self):
        #set secret in database
        login = self.get_argument("login")
        if "@" in login:
            email = login
        elif len(login) == 11:
            mobile = login
            login = "mobile:+86%s" % login
        else:
            return

        user_id, user = nomagic.auth.get_user_by_login(login)

        reset_password_secret = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        user["reset_password_secret"] = reset_password_secret
        update_user(user_id, user)

        if "@" in login:
            #send email
            msg = EmailMessage()
            msg.subject = u"齐书忘记密码".encode("utf8")
            msg.bodyText = "http://%s/reset_password?user_id=%s&secret=%s" % (self.request.host, user_id, reset_password_secret)
            print msg.bodyText
            # self.send("info@qishu.co", str(email), msg)
        elif len(login) == 11:
            pass
        self.render('../template/forgot_password_sent.html')

class ResetPasswordHandler(tornado.web.RequestHandler):
    def get(self):
        reset_password_secret = self.get_argument("secret")
        user_id = self.get_argument("user_id")

        user = get_user(user_id)
        if user.get("reset_password_secret") and user["reset_password_secret"] == reset_password_secret:
            # render
            self.render('../template/reset_password.html')

    def post(self):
        reset_password_secret = self.get_argument("secret")
        user_id = self.get_argument("user_id")
        user = get_user(user_id)

        if user.get("reset_password_secret") and user["reset_password_secret"] == reset_password_secret:
            new_password = self.get_argument('password1')
            check_password_update = nomagic.auth.update_user(user_id, {"password":new_password, "reset_password_secret": ""})

            self.render('../template/reset_password_success.html')

class FakeLoginHandler(tornado.web.RequestHandler):
    def get(self):
        user_id = self.get_argument("id")
        user = {"id": user_id, "v":1}
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.finish(user)


# class ReChaptchaAPIHandler(tornado.web.RequestHandler):
#     fixed_width_font = ImageFont.truetype(os.path.dirname(os.path.abspath(__file__))+"/../template/DroidSansMono.ttf", 25)
#     def get(self):
#         rand_str = "".join(random.choice(list(set(string.ascii_lowercase + string.digits) - set(["0", "o", "1", "l", "q"]))) for x in range(6))
#         width = 100
#         height = 35
#         im = Image.new('RGB',(width,height),'#%s'% "".join(random.choice('abcdef' + string.digits) for x in range(6)))
#         draw = ImageDraw.Draw(im)
#         for i in range(6):
#             draw.line((random.randint(0,width),random.randint(0,height),random.randint(0,width),random.randint(0,height)))
#         draw.text((5,6), rand_str, font=ReChaptchaAPIHandler.fixed_width_font)
#         # del draw
#         buffer = cStringIO.StringIO()
#         im.save(buffer,'jpeg')
#         # print rand_str
#         self.set_header("Content-Type", 'image/jpeg')
#         self.finish(buffer.getvalue())

# class RedeemUnionIDHandler(WebRequest):
#     def get(self):
#         if not self.current_user:
#             self.redirect("/auth/weixin?redirect=%s" % tornado.escape.url_escape(self.request.uri))
#             return
#
#         doc_id = self.get_argument("doc_id")
#         user_id = self.current_user.get("id")
#         user = get_user(user_id)
#         unionid = user.get("weixin_data", {}).get("unionid")
#
#         redeem_unionid = conn.get("SELECT * FROM redeem_unionid WHERE unionid = %s AND doc_id = %s", unionid, doc_id)
#         if redeem_unionid:
#             if not redeem_unionid["user_id"]:
#                 doc = get_doc(doc_id)
#                 assert doc and doc["type"] == "doc"
#                 restrict_users = doc.get("restrict_users", [])
#                 if user_id not in restrict_users:
#                     restrict_users.append(user_id)
#                     doc["restrict_users"] = restrict_users
#                     update_doc(doc_id, doc)
#                 conn.execute("UPDATE redeem_unionid SET user_id = %s WHERE unionid = %s AND doc_id = %s", user_id, unionid, doc_id)
#             self.redirect("/%s" % doc_id)
#             return
#
#         self.finish("error")


def get_verification_code(digit, ascii=False):
    libs = string.ascii_lowercase+string.digits if ascii else string.digits
    return "".join(random.choice(libs) for _ in xrange(digit))
