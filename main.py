import StringIO
import json
import logging
import random
import urllib
import urllib2
import datetime

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '524516331:AAHr5V6jh34QVUTLB09jWtyN7pj8Tt8qAuk'

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
        try:
            message = body['message']
        except:
            message = body['edited_message']
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
                    'text': msg.encode('utf-8'),
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
                reply('juguemos a un juego')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Adios GILIPOLLAS')
                setEnabled(chat_id, False)
            if text ==  "/euromillones":
                numeros = range(1,50)
                estrellas = range(1,12)
                billete = ""
                for 1 in range(5):
                    numeroArray = random.randint(1, len(numeros))
                    billete += numeros[numeroArray] + " "
                    numeros.pop(numeroArray)
                billete += "/ "
                for 1 in range(2):
                    numeroArray = random.randint(1, len(estrellas))
                    billete += estrellas[numeroArray] + " "
                    estrellas.pop(numeroArray)
                reply(billete+" Mucha suerte Wapos.")
            # elif text == '/timetable':
            #     horario = ['Lunes:\n\n>>> 10:30/12:30 > TE (0.5.w)\n>>> 12:30/13:30 > EST (2.0.a)\n>>> 13:30/14:30 > FC (2.0.a)', 'Martes:\n\n>>> 10:30/12:30 > EST (0.5.w)\n>>> 12:30/13:30 > TE (2.0.a)\n>>> 13:30/14:30 > ALX (2.0.a)', 'Miercoles:\n\n>>> 10:30/12:30 > ALX (2.2.b)\n>>> 12:30/13:30 > PRO2 (2.0.a)\n>>> 13:30/14:30 > FC (2.0.a)', 'Jueves:\n\n>>> 10:30/12:30 > PRO2 (0.5.w)\n>>> 12:30/13:30 > EST (2.0.a)\n>>> 13:30/14:30 > TE (2.0.a)', 'Viernes:\n\n>>> 10:30/12:30 > FC (0.5.w)\n>>> 12:30/13:30 > PRO2 (2.0.a)\n>>> 13:30/14:30 > ALX (2.0.a)', 'Sabado:\n\n>>> NADA', 'Domingo:\n\n>>> NADA']
            #     reply(horario[datetime.date.today().weekday()])
            # elif text == '/timetable_tomorrow':
            #     horario = ['Lunes:\n\n>>> 10:30/12:30 > TE (0.5.w)\n>>> 12:30/13:30 > EST (2.0.a)\n>>> 13:30/14:30 > FC (2.0.a)', 'Martes:\n\n>>> 10:30/12:30 > EST (0.5.w)\n>>> 12:30/13:30 > TE (2.0.a)\n>>> 13:30/14:30 > ALX (2.0.a)', 'Miercoles:\n\n>>> 10:30/12:30 > ALX (2.2.b)\n>>> 12:30/13:30 > PRO2 (2.0.a)\n>>> 13:30/14:30 > FC (2.0.a)', 'Jueves:\n\n>>> 10:30/12:30 > PRO2 (0.5.w)\n>>> 12:30/13:30 > EST (2.0.a)\n>>> 13:30/14:30 > TE (2.0.a)', 'Viernes:\n\n>>> 10:30/12:30 > FC (0.5.w)\n>>> 12:30/13:30 > PRO2 (2.0.a)\n>>> 13:30/14:30 > ALX (2.0.a)', 'Sabado:\n\n>>> NADA', 'Domingo:\n\n>>> NADA']
            #     reply(horario[datetime.date.today().weekday() + 1])
            # elif text == '/help':
            #     reply('Commands:\n\n>>> /start > enables the bot\n>>> /stop > disables the bot\n>>> /timetable > returns the timetable for today\n>>> /timetable_tomorrow > returns the timetable for tomorrow')
            # else:
            #     reply('Commands:\n\n>>> /start > enables the bot\n>>> /stop > disables the bot\n>>> /timetable > returns the timetable for today\n>>> /timetable_tomorrow > returns the timetable for tomorrow')
        elif getEnabled(chat_id):
            # if 'paulo' in text.lower():
            #     respuestas = ['burro me cago en dios', 'puto vurro de mierda', 'vale burro', 'que te rente vurro', 'joputabastardocabronmaricon']
            #     reply(respuestas[random.randint(1, len(respuestas))])
            # elif 'republica' in text.lower():
            #     respuestas = ['VIVA ESPANHA!!!!! ROJO PIOJOSO', 'VIVA EL REY Y VIVA ESPANHA HOSTIA']
            #     reply(img=urllib2.urlopen('http://zetaestaticos.com/extremadura/img/noticias/1/041/1041224_1.jpg').read())
            #     reply(respuestas[random.randint(1, len(respuestas))])
            # elif 'comunista' in text.lower():
            #     respuestas = ['ROJOS NO, ESPANHA NO ES UN ZOO', 'SI FRANCO LEVANTASE LA CABEZA', 'Y PARA ESTO MURIO FRANCO? HIJO DE PUTA']
            #     reply(respuestas[random.randint(1, len(respuestas))])
            # elif 'comunismo' in text.lower():
            #     reply('TIEMPO DE ROJOS HAMBRE Y PIOJOS')
            # elif 'burro' in text.lower():
            #     respuestas = ['paulo <- +Inf', 'Alguien ha dicho Paulo?']
            #     reply(respuestas[random.randint(1, len(respuestas))])
            # else:
            #     if random.randint(1, 100) <= 8:
            #         respuestas = ['valetio', 'no me cuentes tu vida', 'pareces el paulo']
            #         reply(respuestas[random.randint(1, len(respuestas))])
            #     elif random.randint(1, 1000) == 1:
            #         reply('no me cuentes tu puta vida imbecil')

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
