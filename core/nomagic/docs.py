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
import utils

from setting import conn

import connection


def email_invite(doc_id, email):
    index_email_invited = conn.get("SELECT * FROM index_email_invited WHERE email = %s", email)
    if index_email_invited:
        data = nomagic._unpack(index_email_invited["data"] or "{}")
        if utils.append_list_in_key_of_dict(data, "doc_ids", doc_id):
            conn.execute("UPDATE index_email_invited SET data = %s WHERE email = %s", nomagic._pack(data), email)
    else:
        data = {"doc_ids": [doc_id]}
        conn.execute("INSERT INTO index_email_invited (email, data) VALUES(%s, %s)", email, nomagic._pack(data))


def remove_email_invite(doc_id, email):
    index_email_invited = conn.get("SELECT * FROM index_email_invited WHERE email = %s", email)
    if index_email_invited:
        data = nomagic._unpack(index_email_invited["data"] or "{}")
        if utils.remove_list_in_key_of_dict(data, "doc_ids", doc_id):
            conn.execute("UPDATE index_email_invited SET data = %s WHERE email = %s", nomagic._pack(data), email)
    else:
        data = {"doc_ids": []}
        conn.execute("INSERT INTO index_email_invited (email, data) VALUES(%s, %s)", email, nomagic._pack(data))


def apply_invite(user_id, email):
    index_email_invited = conn.get("SELECT * FROM index_email_invited WHERE email = %s", email)
    if index_email_invited:
        data = nomagic._unpack(index_email_invited["data"] or "{}")
        docs = nomagic._get_entities_by_ids(data.get("doc_ids", []))

        for doc_id, doc in docs:
            if email in doc["inviting"]:
                doc["inviting"].remove(email)
            if user_id not in doc["editors"]:
                doc["editors"].append(user_id)
            nomagic._update_entity_by_id(doc_id, doc)

        user = nomagic._get_entity_by_id(user_id)
        user["docs"] = data.get("doc_ids", [])
        nomagic._update_entity_by_id(user_id, user)


def accept_invite(doc_id, email):
    pass

