# -*- coding: utf-8 -*-
import sys
import os 

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

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

import datetime

from setting import conn

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc

class order_m:

    def __init__(self):

        pass

    def __del__(self):
        pass

    def add_order(self, data):

        user = get_user(data['current_user_id'])
        openid = user.get("weixin")
        weixin_name  = user.get("name")
        weixin_img   = user.get("weixin_data").get("headimgurl")

        sql = "insert into order_t (group_id, order_name, s_from,\
                s_to, start_time, phone_id, seat_number, s_type, create_time, user_id, username,\
                picture, state) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'enable')" %\
                (data['group_id'], data['order_name'], data['s_from'], data['s_to'], data['start_time'], data['phone_id'], \
                data['seat_number'], data['s_type'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['current_user_id'], weixin_name, weixin_img)

        print sql
        assert conn.execute_rowcount(sql)
        pass


    def disable_order(self, data):

        assert conn.execute_rowcount("update order_t set state = 'disable' where order_id = %s", data['order_id'])

        pass


    def enable_order(self, data):

        assert conn.execute_rowcount("update order_t set state = 'enable' where order_id = %s", data['order_id'])

        pass

    def get_order(self, data):

        sql = "select * from order_t where group_id = %s and to_days(start_time) >= to_days(now()) order by start_time" %(data['group_id'])
        print sql

        result = conn.query(sql)

        return result 

    def get_one_order(self, data):

        result = conn.query("select * from order_t where order_id = %s and to_days(start_time) >= to_days(now())", data['order_id'])

        return result

    def get_my_order(self):

        result = conn.query("select * from order_t where phone_id = ? and to_days(start_time) >= to_days(now())  order by order_id desc", data['order_id'])

        return result

if __name__ == '__main__':

    order_test = order_m()
    order_data = {'group_id': '1', 'order_name': 'test', 's_from':'xx', 's_to':'yy', 'start_time':'2016-10-28 10:00:00', 'phone_id':'132', 'seat_number':'123', \
            's_type':'1', 'username':'mh', 'picture':'123', 'state':'enable'};
    order_test.add_order(order_data)

    order_data = {'group_id':'1'}
    order_result = order_test.get_order(order_data)
    print order_result

