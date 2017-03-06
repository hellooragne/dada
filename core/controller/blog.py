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
import tornado.gen

from setting import settings
from setting import conn

from datetime import datetime


from base import WebRequest
from base import WebSocket


from weixin_jssdk import WeixinJSSDK

logger = logging.getLogger(__name__)

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc


"""
data model
"""
from blog_m import blog_m


class DateEncoder(json.JSONEncoder ):  
    def default(self, obj):  
        if isinstance(obj, datetime):  
            return obj.__str__()  
        return json.JSONEncoder.default(self, obj)  

class NewAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user.get("id")



        #add to db
        blog_model = blog_m()
        data = json.loads(self.request.body)
        
        
        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;

        data['picture_list'] = json.loads(data['picture_list'])

        for index in range(len(data['picture_list'])):
            print data['picture_list'][index]
            

            str = u'curl -G "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" -o %s' % (WeixinJSSDK.access_token, data['picture_list'][index], '/home/cccloud/git/dada/soa/public/myapp/www/img/' + data['picture_list'][index] + '.jpg')

            print str
            os.system(str)

            data['picture_list'][index] = 'img/' + data['picture_list'][index] + '.jpg'

        data['picture_list'] = json.dumps(data['picture_list'])

        blog_model.add_blog(data)

        self.finish()


class CancelAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #add to db
        blog_model = blog_m()
        data = json.loads(self.request.body)
        data['current_user_id'] = current_user_id;
        data['user_id'] = user_id
        blog_model.disable_blog(data)

        self.finish({})


class GetHandler(WebRequest):
    def post(self):

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #get from db
        blog_model = blog_m()
        data      = json.loads(self.request.body)
        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;
        blog_res = blog_model.get_blog(data)

        self.finish(json.dumps(blog_res, cls=DateEncoder))


class GetOneHandler(WebRequest):
    def post(self):

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #get from db
        blog_model = blog_m()
        data      = json.loads(self.request.body)
        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;
        blog_res = blog_model.get_one_blog(data)

        self.finish(json.dumps(blog_res, cls=DateEncoder))

class GetMyHandler(WebRequest):
    def post(self):

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #get from db
        blog_model = blog_m()
        data      = json.loads(self.request.body)
        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;
        blog_res = blog_model.get_my_blog(data)

        print json.dumps(blog_res, cls=DateEncoder)

        self.finish(json.dumps(blog_res, cls=DateEncoder))

