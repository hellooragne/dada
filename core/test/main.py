import tornado.web
import tornado.httpserver
import os
import wx
from tornado.options import define, options

settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'view'),
            'cookie_secret': 'e440769943b4e8442f09de341f3fea28462d2341f483a0ed9a3d5d3859f==78d',
            'login_url': '/',
            'session_secret': "3cdcb1f07693b6e75ab50b466a40b9977db123440c28307f428b25e2231f1bcc",
            'session_timeout': 3600,

            'port': 80,
            'wx_token': 'weixin',
            }

web_handlers = [
        (r'/api/weixin_msg', wx.WX),
        ]

define("port", default=settings['port'], help="run on the given port", type=int)

if __name__ == '__main__':
    app = tornado.web.Application(web_handlers, **settings)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
