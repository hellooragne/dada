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


import tornado
import tornado.web
import tornado.escape
import tornado.websocket
import tornado.httpclient
from tornado.escape import json_encode, json_decode, url_escape
from tornado import gen

from weixin_jssdk import WeixinJSSDK

from setting import settings
from setting import conn

from nomagic.cache import get_user, get_users, update_user#, get_doc, get_docs, update_doc

from base import WebRequest
from base import WebSocket

logger = logging.getLogger(__name__)



class NewTaskHandler(WebRequest):
    def get(self):
        if not self.current_user:
            self.redirect("/auth/simple_weixin?redirect=/new_task")
            return

        user_id = self.current_user["id"]
        self.tasks = conn.query("SELECT * FROM tasks WHERE user_id = %s AND status = 0", user_id)
        self.confirmed_tasks = conn.query("SELECT * FROM tasks WHERE user_id = %s AND status = 1", user_id)
        self.user = get_user(user_id)
        self.render("../template/new_task.html")

class NewTaskAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            self.finish({})
            return

        community_id = self.get_argument("community_id")
        license = self.get_argument("license")
        content = self.get_argument("content")
        datetime = self.get_argument("datetime")

        user_id = self.current_user["id"]
        self.user = get_user(user_id)
        tasks = conn.query("SELECT * FROM tasks WHERE user_id = %s AND status = 0", user_id)
        if license in [task["license"] for task in tasks]:
            index = [task["license"] for task in tasks].index(license)
            task_id = tasks[index]["id"]
            conn.execute("UPDATE tasks SET datetime = %s WHERE id = %s", datetime, task_id)
        else:
            conn.execute("INSERT INTO tasks (license, content, datetime, user_id, community_id) VALUES (%s, %s, %s, %s, %s)", license, content, datetime, user_id, community_id)

        self.finish({})


class ConfirmTaskAPIHandler(WebRequest):
    @gen.coroutine
    def post(self):
        if not self.current_user:
            self.finish({})
            return

        task_id = self.get_argument("task_id")
        license = self.get_argument("license")
        content = self.get_argument("content")
        datetime = self.get_argument("datetime")

        task = conn.get("SELECT * FROM tasks WHERE id = %s", task_id)
        if task:
            conn.execute("UPDATE tasks SET license = %s, content = %s, datetime = %s, status = 1 WHERE id = %s", license, content, datetime, task_id)

            user_id = task["user_id"]
            user = get_user(user_id)
            logger.info(user)
            if not user:
                self.finish({})
                return

            openid = user["open_id"]
            logger.info(openid)
            first = u"您的预约成功"
            keyword1 = str(task["datetime"])
            keyword2 = task["content"]
            remark = u"\n点击进入"
            if openid:
                yield WeixinJSSDK.get_value(self.request.full_url())
                access_token = WeixinJSSDK.access_token
                logger.info(access_token)
                http_client = tornado.httpclient.AsyncHTTPClient()
                url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+access_token
                json = {
                    "touser": openid,
                    "template_id": "oAYv3-frzMctfn0U7YlW-3guSWI46DrdfCxryRdlqNA",
                    "url": "http://meitian.meishizhibo.net/task?task_id=%s" % task_id,
                    "topcolor": "#000000",
                    "data":{
                        "first":{"value": first, "color": "#000000"},
                        "keyword1":{"value": keyword1, "color": "#000000"},
                        "keyword2":{"value": keyword2, "color": "#000000"},
                        # "keyword3":{"value": keyword3,"color": "#f15b29"},
                        "remark":{"value": remark, "color": "#000000"},
                    },
                }
                body = json_encode(json)
                request = tornado.httpclient.HTTPRequest(
                            url = url,
                            method = "POST",
                            body = body)
                response = yield http_client.fetch(request)
                logger.info(response.body)

        self.finish({})


class FinishTaskAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            self.finish({})
            return

        task_id = self.get_argument("task_id")

        task = conn.get("SELECT * FROM tasks WHERE id = %s", task_id)
        if task:
            conn.execute("UPDATE tasks SET status = 2 WHERE id = %s", task_id)

        self.finish({})

class UserHandler(WebRequest):
    def get(self):
        if not self.current_user:
            self.redirect("/auth?redirect=/user")
            return

        user_id = self.current_user.get('id')
        self.user_digital_id = self.get_argument('user_id', '0')
        manager = conn.get("SELECT * FROM managers WHERE user_id = %s", user_id)
        if not manager:
            self.finish("need manager")
            return

        self.user = {}
        if self.user_digital_id:
            index_login = conn.get("SELECT * FROM index_login WHERE id = %s", self.user_digital_id)
            if index_login:
                self.user_hex_id = index_login["entity_id"]
                self.user = get_user(self.user_hex_id)
                self.communities = conn.query("SELECT * FROM communities")

        self.render("../template/user.html")

class ListTasksHandler(WebRequest):
    def get(self):
        if not self.current_user:
            self.redirect("/auth?redirect=/user")
            return

        user_id = self.current_user.get('id')
        manager = conn.get("SELECT * FROM managers WHERE user_id = %s", user_id)
        if not manager:
            self.finish("need manager")
            return

        community_id = manager["community_id"]
        if manager["level"] == 100:
            self.tasks = conn.query("SELECT * FROM tasks WHERE status = 0 ORDER BY datetime ASC")
            self.confirmed_tasks = conn.query("SELECT * FROM tasks WHERE status = 1 ORDER BY datetime ASC")
            self.finished_tasks = conn.query("SELECT * FROM tasks WHERE status = 2 ORDER BY datetime ASC")
        else:
            self.tasks = conn.query("SELECT * FROM tasks WHERE status = 0 AND community_id = %s ORDER BY datetime ASC", community_id)
            self.confirmed_tasks = conn.query("SELECT * FROM tasks WHERE status = 1 AND community_id = %s ORDER BY datetime ASC", community_id)
            self.finished_tasks = conn.query("SELECT * FROM tasks WHERE status = 2 AND community_id = %s ORDER BY datetime ASC", community_id)

        user_ids = tuple(set([task["user_id"] for task in self.tasks]+[task["user_id"] for task in self.confirmed_tasks]+[task["user_id"] for task in self.finished_tasks]))
        users = get_users(user_ids)
        self.users_dict = {user["id"]: user for user in users}

        self.render("../template/list_tasks.html")

class UpdateUserAPIHandler(WebRequest):
    def post(self):
        if not self.current_user:
            self.finish({})
            return

        user_id = self.current_user.get("id")
        name = self.get_argument("name")
        mobile = self.get_argument("mobile")
        address = self.get_argument("address")
        community_id = self.get_argument("community_id")
        cars = self.get_argument("cars", "[]")

        user = get_user(user_id)
        if user:
            user["name"] = name
            user["mobile"] = mobile
            user["address"] = address
            user["community_id"] = community_id
            user["cars"] = json_decode(cars)
            update_user(user_id, user)


class DashboardHandler(WebRequest):
    def get(self):
        if not self.current_user:
            return
        self.render("../template/order/dashboard.htm")

# class DashboardStatusAPIHandler(WebRequest):
#     def post(self):
#         global message_queue, users, orders, dashboard_clients
#         # if not self.current_user:
#         #     return

#         timestamp = self.get_argument("timestamp", "")
#         if timestamp:
#             new_messages = [message for message in message_queue if message["timestamp"] > float(timestamp)]
#             if new_messages:
#                 self.finish(new_messages[0])
#             else:
#                 self._auto_finish = False
#                 dashboard_clients.add(self)
#         else:
#             list_orders = []
#             for user_id, user in users.iteritems():
#                 order_ids = user.get("order_ids", [])
#                 list_orders.extend([orders[order_id] for order_id in order_ids])
#             self.finish({"orders": list_orders, "timestamp": time.time()})


# class DashboardChangeAPIHandler(WebRequest):
#     def get(self):
#         self.post()

#     def post(self):
#         global users, orders, dashboard_clients
#         # if not self.current_user:
#         #     return

#         order_id = self.get_argument("order_id")
#         status = self.get_argument("status")
#         orders[order_id]["status"] = {
#                 "0": NEW_ORDER,
#                 "1": SUBMITED,
#                 "2": IN_PROCESS,
#                 "3": DELIVERY,
#                 "4": COMPLETE,
#                 "5": CANCELLED
#             }[status]

#         message = {"orders":[orders[order_id]], "timestamp": time.time()}
#         message_queue.append(message)
#         user_id = orders[order_id]["user_id"]
#         user = users.get(user_id, {})

#         for client in user.get("clients", []):
#             client.finish(message)
#         user["clients"] = set()

#         for client in dashboard_clients:
#             client.finish(message)
#         dashboard_clients = set()

#         self.finish()

# class NewAPIHandler(WebRequest):
#     def post(self):
#         global users, orders, dashboard_clients, message_queue
#         # if not self.current_user:
#         #     return

#         user_id = self.current_user.get("id")
#         user_id = "1"

#         user = users.get(user_id, {})
#         order_ids = user.get("order_ids", [])
#         if len(order_ids) < 2:
#             order_id = uuid.uuid4().hex
#             orders[order_id] = {k:v[0] for k, v in self.request.body_arguments.iteritems()}
#             orders[order_id]["order_id"] = order_id
#             orders[order_id]["user_id"] = user_id
#             orders[order_id]["status"] = NEW_ORDER

#             message = {"orders": [orders[order_id]], "timestamp": time.time()}
#             message_queue.append(message)
#             for client in dashboard_clients:
#                 client.finish(message)
#             dashboard_clients = set()

#             order_ids.insert(0, order_id)
#             user["order_ids"] = order_ids
#             users[user_id] = user
#             self.finish(orders[order_id])
