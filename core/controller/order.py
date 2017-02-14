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

# class UpdateAPIHandler(WebRequest):
#     def get(self):
#         self.post()
#
#     def post(self):
#         global users, orders, message_queue
#         if not self.current_user:
#             return
#
#         order_id = self.get_argument("order_id")
#
#         message = {"orders":[orders[order_id]], "timestamp": time.time()}
#         message_queue.append(message)
#         user_id = orders[order_id]["user_id"]
#         user = users.get(user_id, {})
#
#         for client in user.get("clients", set()):
#             client.finish(message)
#         user["clients"] = set()
#
#         self.finish()

class NewAPIHandler(WebRequest):
    def post(self):
        global users, orders, message_queue

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        user = users.get(user_id, {})
        order_ids = user.get("order_ids", [])

        print "add to db"
        """
        if len(order_ids) < 1:
            order_id = uuid.uuid4().hex
            orders[order_id] = {k:v[0] for k, v in self.request.body_arguments.iteritems()}
            orders[order_id]["order_id"] = order_id
            orders[order_id]["user_id"] = user_id

            order_ids.insert(0, order_id)
            user["order_ids"] = order_ids
            users[user_id] = user

        """

        #add to db
        order_model = order_m()
        data = json.loads(self.request.body)
        current_user_id = self.current_user.get("id")
        data['current_user_id'] = current_user_id;
        order_model.add_order(data)

        """
        message = {"orders": [orders[order_id]], "timestamp": time.time()}
        message_queue.append(message)

        for user in users.values():
            for client in user.get("clients", set()):
                client.finish(message)
            user["clients"] = set()

        pprint.pprint(users)
        """
        self.finish()



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


class GetOrderHandler(WebRequest):
    def post(self):
        global users, orders, message_queue

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #get from db
        print "get from db"
        order_model = order_m()
        data      = json.loads(self.request.body)
        order_res = order_model.get_order(data)

        print json.dumps(order_res, cls=DateEncoder)

        self.finish(json.dumps(order_res, cls=DateEncoder))


class GetOneOrderHandler(WebRequest):
    def post(self):
        global users, orders, message_queue

        if not self.current_user:
            return

        user_id = self.current_user.get("id")

        #get from db
        order_model = order_m()
        data      = json.loads(self.request.body)
        order_res = order_model.get_one_order(data)

        print json.dumps(order_res, cls=DateEncoder)

        self.finish(json.dumps(order_res, cls=DateEncoder))


class TestHandler(WebRequest):
    def get(self):
        self.finish('{"test":"ok"}')

    def post(self):
        #print self.request.body_arguments
        print self.request.body

	data = json.loads(self.request.body)
        print data['name']

        self.finish('{"test":"ok"}')


