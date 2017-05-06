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

    "WeixinAppId": "wx7f638d2d85dc480f",
    "WeixinAppSecret": "059a902c7b8a29ba36bff3dd20c224cd",


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
