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


from base import WebRequest
from base import WebSocket




logger = logging.getLogger(__name__)

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc

from order_join_m import order_join_m

from datetime import datetime

class DateEncoder(json.JSONEncoder ):  
    def default(self, obj):  
        if isinstance(obj, datetime):  
            return obj.__str__()  
        return json.JSONEncoder.default(self, obj)  


class NewOrderJoin(WebRequest):
    def post(self):
        global users, orders

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        order_join_model = order_join_m()
        data = json.loads(self.request.body)

        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;

        order_join_model.add_order_join(data)

	


class CancelOrderJoin(WebRequest):
    def post(self):
        global users, orders, message_queue
        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        order_join_model = order_join_m()
        data = json.loads(self.request.body)

        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;


        order_join_model.disable_order_join(data)



class GetOrderJoin(WebRequest):
    def post(self):
        global users, orders, message_queue

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        order_join_model = order_join_m()
        data = json.loads(self.request.body)
        res  = order_join_model.get_order_join(data)

        self.finish(json.dumps(res, cls=DateEncoder))
