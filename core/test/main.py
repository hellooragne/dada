import tornado.web
import tornado.httpserver
import os
import wx
from tornado.options import define, options

settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'view'),
            'cookie_secret': 'Q1POPHCWTPr9kCclw4VL2oJUMiCrXR0ea8eaXLhCyRd',
            'login_url': '/',
            'session_secret': "Q1POPHCWTPr9kCclw4VL2oJUMiCrXR0ea8eaXLhCyRd",
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
