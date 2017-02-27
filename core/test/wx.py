import tornado.escape
import tornado.web

from wechat_sdk import WechatConf
conf = WechatConf(
    token='newtest',
    appid='wx7f638d2d85dc480f',
    appsecret='059a902c7b8a29ba36bff3dd20c224cd',
    encrypt_mode='safe',
)

from wechat_sdk import WechatBasic
wechat = WechatBasic(conf=conf)

class WX(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature', 'default')
        timestamp = self.get_argument('timestamp', 'default')
        nonce = self.get_argument('nonce', 'default')
        echostr = self.get_argument('echostr', 'default')
        if signature != 'default' and timestamp != 'default' and nonce != 'default' and echostr != 'default' \
                and wechat.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('Not Open')
