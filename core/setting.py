import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor/')

import logging
import uuid


settings = {
    #"xsrf_cookies": True,
    # "QiniuAccessKey": "38j1iFOxxpAlZiIBPZGhA-DQAIKKgPNWjlrFCyYN",
    # "QiniuSecretKey": "ZxHd6By4L3lt4ZOyYsz306cOiSOd6cgYZZJBTpJ9",
    "WeixinAppId": "wx2bed1fab33851e41",
    "WeixinAppSecret": "bca8be10d8b03030b32333cc50e6b538",
    "static_path": os.path.join(os.path.dirname(__file__), "./static/"),
    "cookie_secret": "u890Tz7Xbbccck85n3edc7782dp9fnmYFvRhx7skpVx",
    "login_url": "/",
    "debug": False,
    "invitecode": False,
}

try:
    print "init"
    import torndb as database
    conn = database.Connection("127.0.0.1", "dada", "root", "123456")
    
    ring = [conn] # I love the name Ring
except Exception, e:
    print e
    pass
