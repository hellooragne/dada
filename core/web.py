# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor/')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/model/')
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

import ssl

import tornado.options
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.auth
import tornado.locale
import tornado.httpclient
import tornado.httpserver

from setting import settings
from controller import weixin
from controller import task
from controller import manager
from controller import auth
from controller import order
from controller import blog
from controller import order_join
from controller import msg_process

application = tornado.web.Application([

    #hmeng
    (r"/api/weixinlogin", weixin.ApiWeixinLogin),
    (r"/api/weixinredirect", weixin.ApiWeixinRedirect),

    #hmeng
    (r"/api/fake_login", auth.FakeLoginHandler),

    #hmeng
    (r"/order", order.OrderHandler),
    (r"/api/order/new", order.NewAPIHandler),
    (r"/api/order/cancel", order.CancelAPIHandler),
    (r"/api/order/status", order.StatusAPIHandler),
    (r"/api/order/get", order.GetOrderHandler),
    (r"/api/order/getone", order.GetOneOrderHandler),
    
    #hmeng
    (r"/api/order_join/new", order_join.NewOrderJoin),
    (r"/api/order_join/cancel", order_join.CancelOrderJoin),
    (r"/api/order_join/get", order_join.GetOrderJoin),

    (r"/api/blog/new", blog.NewAPIHandler),
    (r"/api/blog/cancel", blog.CancelAPIHandler),
    (r"/api/blog/get", blog.GetHandler),
    (r"/api/blog/getone", blog.GetOneHandler),
    (r"/api/blog/getmy", blog.GetMyHandler),

    #hmeng
    (r"/api/weixin_msg", msg_process.MessageHandler),
    (r"/api/weixin_config", msg_process.WeixinConfigHandler),

    
    
    (r"/api/upload", msg_process.UploadHandler),



    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'], default_filename='index.html')),
], **settings)

if __name__ == "__main__":
    # tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "csv_translations"))
    tornado.options.define("port", default=8027, help="Run server on a specific port", type=int)
    tornado.options.parse_command_line()
    application.listen(tornado.options.options.port)

    # if not settings["debug"]:
    #     secure_server = tornado.httpserver.HTTPServer(application,
    #         ssl_options={"certfile": os.path.join("/etc/ssl/", "qishu.crt"),
    #                      "keyfile": os.path.join("/etc/ssl/", "qishu.key")})
    #     secure_server.listen(8027)
    tornado.ioloop.IOLoop.instance().start()
