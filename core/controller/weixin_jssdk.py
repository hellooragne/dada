# -*- coding: utf-8 -*-
import urllib
import hashlib
import time
import random
import string
import logging

import tornado
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.websocket
import tornado.httpclient
import tornado.gen
from tornado.escape import json_encode, json_decode

from setting import settings

logger = logging.getLogger(__name__)

class WeixinJSSDK(object):
    access_token = ''
    timestamp = 0
    jsapi_ticket = ''
    nonceStr = ''
    signature = ''

    @classmethod
    @tornado.gen.coroutine
    def get_value(cls, full_url):
        sign = WeixinJSSDKSign(cls.jsapi_ticket, cls.timestamp, full_url)
        cls.wx_ret = sign.sign()
        cls.nonceStr         = cls.wx_ret['nonceStr']
        cls.signature        = cls.wx_ret['signature']
        signature = cls.signature
        timestamp = cls.timestamp
        nonceStr  = cls.nonceStr

        print "full url:" + full_url 
        print "jsapi_ticket :" + cls.jsapi_ticket 
        print "signature:" + cls.signature
        print "timestamp:" + str(cls.timestamp)
        print "nonce:" + cls.nonceStr
        


class WeixinJSSDKSign(object):
    def __init__(self, jsapi_ticket, timestamp, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': timestamp,
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

@tornado.gen.coroutine
def update_access_token():
    if settings["debug"]:
        return

    # from data import DataWebSocket
    WeixinJSSDK.timestamp = int(time.time())
    http_client = tornado.httpclient.AsyncHTTPClient()

    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+settings.get("WeixinAppId", "")+"&secret="+settings.get("WeixinAppSecret", "")
    response = yield http_client.fetch(url)
    print response.body
    data = tornado.escape.json_decode(response.body)
    WeixinJSSDK.access_token = data.get('access_token')

    url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token="+WeixinJSSDK.access_token+"&type=jsapi"
    response = yield http_client.fetch(url)
    data = tornado.escape.json_decode(response.body)
    print data
    WeixinJSSDK.jsapi_ticket = data.get('ticket')

    # for client in DataWebSocket.subscribers:
    #     client.write_message(json_encode(["WEIXIN_ACCESS_TOKEN", WeixinJSSDK.access_token, WeixinJSSDK.timestamp, WeixinJSSDK.jsapi_ticket]))
    #print "timestamp" + str(WeixinJSSDK.timestamp)
    #print "nonceStr" + WeixinJSSDK.nonceStr
    #print "signature" + WeixinJSSDK.signature


tornado.ioloop.PeriodicCallback(update_access_token, 3600*2000).start()
tornado.ioloop.IOLoop.instance().add_callback(update_access_token)
