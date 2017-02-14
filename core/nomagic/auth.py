#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import datetime
import pickle
import uuid
import binascii

import zlib
import hashlib
import json
import random
import string

import __init__ as nomagic

from setting import conn

import connection
from cache import BIG_CACHE, get_user

def create_user(user):
    user["type"] = "user"
    user["name"] = user.get("name", "")
    user["salt"] = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
    user["password"] = hashlib.sha1(user.get("password", "") + user["salt"]).hexdigest()
    user["datetime"] = datetime.datetime.now().isoformat()

    new_id = nomagic._new_key()
    rowcount = nomagic._node(new_id).execute_rowcount("INSERT INTO entities (id, body) VALUES(%s, %s)", new_id, nomagic._pack(user))
    assert rowcount

    return (new_id, user)

def update_user(user_id, data):
    #valid name
    entity = nomagic._node(user_id).get("SELECT body FROM entities WHERE id = %s", nomagic._key(user_id))
    user = nomagic._unpack(entity["body"]) if entity else None
    user_json1 = entity["body"]
    result = {}

    if "password0" in data and "password1" in data and data["password0"] != data["password1"] and data["password1"] != "":
        #normal update password with old password0 and new password1
        if user["password"] == hashlib.sha1(data["password0"] + user.get("salt", "")).hexdigest():
            user["password"] = hashlib.sha1(data["password1"] + user.get("salt", "")).hexdigest()
            result["password_updated"] = True
        del data["password0"]
        del data["password1"]

    elif "password" in data and data["password"] != "":
        #force update password
        user["password"] = hashlib.sha1(data["password"] + user.get("salt", "")).hexdigest()
        result["password_updated"] = True
        del data["password"]

    if user:
        user.update(data)
        user_json2 = nomagic._pack(user)
        if user_json1 != user_json2:
            assert nomagic._node(user_id).execute_rowcount("UPDATE entities SET body = %s WHERE id = %s", user_json2, nomagic._key(user_id))
            BIG_CACHE.unset(user_id)
    return result

def check_user(login, password):
    index_login = conn.get("SELECT entity_id FROM index_login WHERE login = %s", login)
    if index_login:
        user_id = index_login["entity_id"]
        user = get_user(user_id)
        if user["password"] == hashlib.sha1(password + user.get("salt", "")).hexdigest():
            return (user_id, user)
    return (None, None)

def get_user_by_login(login):
    index_login = conn.get("SELECT * FROM index_login WHERE login = %s", login)
    if index_login:
        user_id = index_login["entity_id"]
        return user_id, get_user(user_id)
    else:
        return None, None

def get_user_id_by_login(login):
    index_login = conn.get("SELECT * FROM index_login WHERE login = %s", login)
    return index_login["entity_id"] if index_login else None

def check_invitecode(invitecode):
    index_invitecode = conn.get("SELECT * FROM index_invitecode WHERE invitecode = %s", invitecode)
    return index_invitecode["now"] if index_invitecode else None

def update_invitecode(invitecode, user_id):
    assert conn.execute_rowcount("UPDATE index_invitecode SET user_id = %s , now = 2 WHERE invitecode = %s",user_id,invitecode)
