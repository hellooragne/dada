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


from setting import conn

from nomagic.cache import get_user, get_users, update_user, get_doc, get_docs, update_doc

class order_join_m:

    def __init__(self):

        pass

    def __del__(self):
        pass

    def add_order_join(self, data):

        user = get_user(data['current_user_id'])
        print user
        openid = user.get("weixin")
        weixin_name = user.get("name")
        phone_id    = user.get("phone")
        weixin_img  = user.get("weixin_data").get("headimgurl")


        sql = "insert into order_join_t (order_id, phone_id, username, picture,\
        create_time, state) values ('%s', '%s', '%s', '%s',  now(), 'enable')" %\
        (data['bill_id'], phone_id, weixin_name, weixin_img)

        print sql
        assert conn.execute_rowcount(sql)
	pass

        
    def disable_order_join(self, data):

        assert conn.execute_rowcount("update order_join_t set state = 'disable' where id = %s", data['order_join_id'])
        pass


    def enable_order_join(self, data):
        assert conn.execute_rowcount("update order_join_t set state = 'disable' where id = %s", data['order_join_id'])
        pass


    def get_order_join(self, data):
        
        print data['order_id']

        result = conn.query("select * from order_join_t where order_id = %s", data['order_id'])
        return result


if __name__ == '__main__':

	pass
