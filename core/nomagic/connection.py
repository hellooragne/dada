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
from cache import get_entity, get_entities, update_entity
from cache import BIG_CACHE
import utils

from setting import conn


def connect_index_and_entity(table_index, index_name, index_connection_name, entity_id, entity_connection_name):
    index = conn.get("SELECT * FROM %s WHERE name = %s" % (table_index, "%s"), index_name)
    index_data = nomagic._unpack(index["data"] or "{}")
    if utils.prepend_list_in_key_of_dict(index_data, index_connection_name, entity_id):
        index_data_updated = nomagic._pack(index_data)
        conn.execute("UPDATE %s SET data = %s WHERE name = %s" % (table_index, "%s", "%s"), index_data_updated, index_name)

    entity = get_entity(BIG_CACHE, entity_id)
    if utils.prepend_list_in_key_of_dict(entity, entity_connection_name, index_name):
        update_entity(BIG_CACHE, entity_id, entity)

def disconnect_index_and_entity(table_index, index_name, index_connection_name, entity_id, entity_connection_name):
    index = conn.get("SELECT * FROM %s WHERE name = %s" % (table_index, "%s"), index_name)
    index_data = nomagic._unpack(index["data"] or "{}")
    if utils.remove_list_in_key_of_dict(index_data, index_connection_name, entity_id):
        index_data_updated = nomagic._pack(index_data)
        conn.execute("UPDATE %s SET data = %s WHERE name = %s" % (table_index, "%s", "%s"), index_data_updated, index_name)

    entity = get_entity(BIG_CACHE, entity_id)
    if utils.remove_list_in_key_of_dict(entity, entity_connection_name, index_name):
        update_entity(BIG_CACHE, entity_id, entity)


def connect_entities(entity_id1, entity_connection_name1, entity_id2, entity_connection_name2):
    entity1, entity2 = get_entities(BIG_CACHE, [entity_id1, entity_id2])
    entity_data1, entity_data2 = entity1[1], entity2[1]

    if utils.prepend_list_in_key_of_dict(entity_data1, entity_connection_name1, entity_id2):
        update_entity(BIG_CACHE, entity_id1, entity_data1)

    if utils.prepend_list_in_key_of_dict(entity_data2, entity_connection_name2, entity_id1):
        update_entity(BIG_CACHE, entity_id2, entity_data2)


def disconnect_entities(entity_id1, entity_connection_name1, entity_id2, entity_connection_name2):
    entity1, entity2 = get_entities(BIG_CACHE, [entity_id1, entity_id2])
    entity_data1, entity_data2 = entity1[1], entity2[1]

    if utils.remove_list_in_key_of_dict(entity_data1, entity_connection_name1, entity_id2):
        update_entity(BIG_CACHE, entity_id1, entity_data1)

    if utils.remove_list_in_key_of_dict(entity_data2, entity_connection_name2, entity_id1):
        update_entity(BIG_CACHE, entity_id2, entity_data2)

if __name__ == '__main__':
    disconnect_entities("12345678901234567890123456789012", "startup", "12345678901234567890123456789013", "founder")
    #connect_index_and_entity("index_industry", "hardware", "startup", "12345678901234567890123456789013", "industry")
