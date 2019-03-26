import cherrypy
import telebot
from config import bot
import bot_token
import logging
import datetime

WEBHOOK_HOST = '195.201.138.7'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '195.201.138.7'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (bot_token.token)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


def start():
    logging.basicConfig(filename="log.log", level=logging.INFO)
    try:
        now_date = datetime.datetime.today()
        now_date = now_date.strftime("%d/%m/%y %H:%M")
        logging.info('['+now_date+'] Bot started')
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,certificate=open(WEBHOOK_SSL_CERT, 'r'))
        cherrypy.config.update({
                'server.socket_host': WEBHOOK_LISTEN,
                'server.socket_port': WEBHOOK_PORT,
                'server.ssl_module': 'builtin',
                'server.ssl_certificate': WEBHOOK_SSL_CERT,
                'server.ssl_private_key': WEBHOOK_SSL_PRIV
            })
        cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
    except:
        now_date = datetime.datetime.today()
        now_date = now_date.strftime("%d/%m/%y %H:%M")
        logging.debug('[' + now_date + '] Bot dropped')
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%y %H:%M")
    logging.info('['+now_date+'] Bot finished')
