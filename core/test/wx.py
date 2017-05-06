import tornado.escape
import tornado.web

from wechat_sdk import WechatConf
conf = WechatConf(
    token='newtest',
    appid='wx072da43896fd6fbd',
    appsecret='e00c06c1c843e14e2cb649bab9dc4194',
    encrypt_mode='safe',
)

from wechat_sdk import WechatBasic
wechat = WechatBasic(conf=conf)

class WX(tornado.web.RequestHandler):
    def get(self):
        print "wx"
        signature = self.get_argument('signature', 'default')
        timestamp = self.get_argument('timestamp', 'default')
        nonce = self.get_argument('nonce', 'default')
        echostr = self.get_argument('echostr', 'default')
        if signature != 'default' and timestamp != 'default' and nonce != 'default' and echostr != 'default' \
                and wechat.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('Not Open')
