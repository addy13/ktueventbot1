import StringIO
import json
import logging
import random
import urllib
import urllib2
import random
from json import loads
from time import strptime, localtime
import datetime

if __import__('sys').version_info[0] == 2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = 'ENTER TOKEN HERE'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)

# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg,
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/today':
                todayEvents = []
                req = urlopen("http ://adigov. stud.if .ktu.lt/wordpress/?json=1".replace(' ', '')+'?'+str(random.random()))
                content = req.read().decode("utf-8")
                jsonObj = loads(content)
                if jsonObj["status"] and jsonObj["status"] == "ok":
                    posts = jsonObj["posts"]
                    if posts:
                        for post in posts:
                            if post["categories"] and len(post["categories"]) > 0:
                                category = post["categories"][0]
                                parseTime = strptime(category["title"], "%m/%d/%Y")
                                today = localtime()
                                # Far shorter. :P
                                if parseTime[:3] == today[:3]:
                                    todayEvents.append(post["title"])
                def concateEvents(todayEventsarg):
                    if len(todayEventsarg) == 1:
                        return ("Today there is one event:\n {0}".format(todayEventsarg[0]))
                    elif len(todayEventsarg) > 1:
                        concatString = "Today there are the following events:"
                        for i in range(len(todayEventsarg)):
                            concatString = "{0}\n{1}. {2}".format(concatString, (i+1), todayEventsarg[i])
                        return concatString
                    else:
                        return "There are no Events today"
                reply(concateEvents(todayEvents))
            elif text == '/about':
                reply('KTUeventBot : A simple free chat messenger bot to keep you updated on all events at KTU.\n\nKTUeventbot Version : 1 Release : 2\n\nSource code is availabe and open source on Github, type "/source" as command.\n\nCredits :GAE,  Members of HF,  Yukuku(Telebot starter Kit),  StackOverFlow,  My dear friend Hilko.')
            elif text == '/time':
                reply(datetime.datetime.now())
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text == '/source':
                reply('www.goo.gl/O3wZtD')
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('telegrambot')
        elif 'what time' in text:
            reply('look at the top-right corner of your screen!')
        else:
            if getEnabled(chat_id):
                try:
                    resp1 = json.load(urllib2.urlopen('http://www.simsimi.com/requestChat?lc=en&ft=1.0&req=' + urllib.quote_plus(text.encode('utf-8'))))
                    back = resp1.get('res').get('msg')
                except urllib2.HTTPError, err:
                    logging.error(err)
                    back = str(err)
                if not back:
                    reply('okay...')
                elif 'I HAVE NO RESPONSE' in back:
                    reply('you said something with no meaning')
                else:
                    reply(back)
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
