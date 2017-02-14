# -*- coding: utf-8 -*-
import logging
import urllib
import hashlib
import time
import uuid

import tornado.web
import tornado.escape
import tornado.httpclient
from tornado.escape import json_encode, json_decode
from tornado import gen

from base import WebRequest

import auth
import xmltodict

from setting import settings
from setting import conn

from nomagic.cache import get_user, get_users, update_user#, get_doc, get_docs, update_doc

logger = logging.getLogger(__name__)

class ManagerHandler(WebRequest):
    def get(self):
        if not self.current_user:
            return

        user_id = self.current_user.get('id')
        manager = conn.get("SELECT * FROM managers WHERE user_id = %s", user_id)
        if not manager:
            self.finish("need manager")
            return

        if manager["level"] == 0:
            self.finish("need manager")
            return

        elif manager["level"] == 50:
            managers = conn.query("SELECT * FROM managers WHERE user_id != %s", user_id)
            self.managers = get_users([u["user_id"] for u in managers])
            self.communities = conn.query("SELECT * FROM communities")
            self.invitations = conn.query("SELECT * FROM managers WHERE user_id = 0 AND invitation_deadline > %s", time.time())
            self.render("../template/manager.html")

        elif manager["level"] == 100:
            managers = conn.query("SELECT * FROM managers WHERE user_id != %s", user_id)
            self.managers = get_users([u["user_id"] for u in managers])
            self.communities = conn.query("SELECT * FROM communities")
            self.invitations = conn.query("SELECT * FROM managers WHERE user_id = 0 AND invitation_deadline > %s", time.time())
            self.render("../template/manager.html")

class InviteAPIHandler(WebRequest):
    def get(self):
        self.post()

    def post(self):
        if not self.current_user:
            return

        user_id = self.current_user.get('id')
        community_id = self.get_argument("community_id")

        manager = conn.get("SELECT * FROM managers WHERE user_id = %s", user_id)
        if not manager:
            self.finish({"msg":"need manager"})
            return

        if manager["level"] == 0:
            self.finish({"msg":"need manager"})
            return

        elif manager["level"] == 50:
            conn.execute("INSERT INTO managers (user_id, community_id, level, invitation_deadline) VALUES (0, %s, 0, %s)", community_id, time.time()+1800)
            self.finish({"msg":"success"})

        elif manager["level"] == 100:
            level = self.get_argument("level")
            assert level in ["0", "50"]
            manager_id = conn.execute("INSERT INTO managers (user_id, community_id, level, invitation_deadline) VALUES (0, %s, %s, %s)", community_id, level, time.time()+1800)
            self.finish({"msg":"success", "url":"%s://%s/invitation_accept?manager_id=%s" % (self.request.protocol, self.request.host, manager_id)})


class InvitationAcceptHandler(WebRequest):
    def get(self):
        if not self.current_user:
            return

        user_id = self.current_user.get('id')
        manager_id = self.get_argument("manager_id")
        manager = conn.get("SELECT * FROM managers WHERE id = %s", manager_id)
        if not manager:
            self.finish("not exists")
            return
        elif manager["user_id"] > 0:
            self.finish("not available")
            return
        elif manager["invitation_deadline"] < time.time():
            self.finish("expired")
            return

        if conn.get("SELECT * FROM managers WHERE user_id = %s", user_id):
            self.finish("manager already")
        else:
            conn.execute("UPDATE managers SET user_id = %s WHERE id = %s", user_id, manager_id)
            self.finish("success")
