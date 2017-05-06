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


import logging
logger = logging.getLogger(__name__)

class blog_m:

    def __init__(self):

        pass

    def __del__(self):
        pass

    def add_blog(self, data):

        user = get_user(data['current_user_id'])
        openid = user.get("weixin")
        weixin_name  = user.get("weixin_data").get("nickName")
        weixin_img   = user.get("weixin_data").get("avatarUrl")


        print data

        sql = "insert into blog_t (city, group_id, title, desc_t,\
                context, s_url, picture_list, user_id, phone_id,  create_time,  username,\
                picture, state) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s',  'enable'); commit" %\
                (data['city'], data['group_id'], data['title'], data['desc_t'], data['context'], data['s_url'], data['picture_list'], \
                data['current_user_id'], data['phone_id'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), weixin_name, weixin_img)

        logger.info(sql)
        assert conn.execute_rowcount(sql)
        return

        logger.info(data['desc_t'])

        assert conn.execute("insert into blog_t (city, group_id, title, desc_t,\
                context, s_url, picture_list, user_id, phone_id,  create_time,  username,\
                picture, state) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s',  '%s','enable')", \
                [data['city'], data['group_id'], data['title'], data['desc_t'], data['context'], data['s_url'], data['picture_list'], \
                data['current_user_id'], data['phone_id'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), weixin_name, weixin_img])
        
        #assert conn.execute_rowcount(sql)
        pass


    def disable_blog(self, data):

        conn.execute_rowcount("update blog_t set state = 'disable' where id = %s", data['id'])

        pass


    def enable_blog(self, data):

        assert conn.execute_rowcount("update blog_t set state = 'enable' where id = %s", data['id'])

        pass

    def get_blog(self, data):

        sql = "select * from blog_t where group_id = %s  order by create_time desc" %(data['group_id'])
        print sql

        result = conn.query(sql)

        return result 

    def get_one_blog(self, data):

        result = conn.query("select * from blog_t where id = %s", data['id'])

        return result

    def get_my_blog(self, data):

        result = conn.query("select * from blog_t where user_id = ? ", data['current_user_id'])

        return result

    def add_commit(self, data):
        
        user = get_user(data['current_user_id'])
        openid = user.get("weixin")
        weixin_name  = user.get("weixin_data").get("nickName")
        weixin_img   = user.get("weixin_data").get("avatarUrl")


        sql = "insert into  blog_commit_t (group_id, blog_id, group_type, commit_t, create_time, username , picture, state) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', 'enable')" % (data['group_id'], data['blog_id'], data['group_type'], data['commit_t'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), weixin_name, weixin_img)

        logger.info(sql)
        assert conn.execute_rowcount(sql)
        pass

    def get_commit(self, data):

        sql = "select * from blog_commit_t where blog_id = '%s'  order by create_time desc " %(data['blog_id'])

        result = conn.query(sql)

        return result


if __name__ == '__main__':

    order_test = order_m()
    order_data = {'group_id': '1', 'order_name': 'test', 's_from':'xx', 's_to':'yy', 'start_time':'2016-10-28 10:00:00', 'phone_id':'132', 'seat_number':'123', \
            's_type':'1', 'username':'mh', 'picture':'123', 'state':'enable'};
    order_test.add_order(order_data)

    order_data = {'group_id':'1'}
    order_result = order_test.get_order(order_data)
    print order_result

