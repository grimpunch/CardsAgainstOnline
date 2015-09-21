import base64
import uuid
import os
import bcrypt
import hashlib
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpserver
import logging
import json
from urllib.parse import urlparse
import time
import threading
import functools
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient


class BaseHandler(RequestHandler):
    def get_login_url(self):
        return u"/login"

    def get_current_user(self):
        user_json = self.get_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

    # Allows us to get the previous URL
    def get_referring_url(self):
        try:
            _, _, referrer, _, _, _ = urlparse(self.request.headers.get('Referrer'))
            if referrer:
                return referrer
        # Test code will throw this if there was no 'previous' page
        except AttributeError:
            pass
        return '/'

    def get_flash(self):
        flash = self.get_secure_cookie('flash')
        self.clear_cookie('flash')
        return flash

    def get_essentials(self):
        mp = {k: ''.join(v) for k, v in self.request.arguments.iteritems()}
        print(mp)


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", notification=self.get_flash())

    def post(self):
        username = self.get_argument("username", "")
        self.set_current_user(username)
        self.redirect("play")

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

#
# class NoneBlockingLogin(BaseHandler):
#     """ Runs Bcrypt in a thread - Allows tornado to server up other handlers but can not process multiple logins simultaneously"""
#     def get(self):
#         self.render("login.html", notification=self.get_flash())
#
#     def initialize(self):
#         self.thread = None
#
#     @tornado.web.asynchronous
#     def post(self):
#         username = self.get_argument("username", "")
#         password = self.get_argument('password', '')
#         password = password.encode('utf-8')
#         user = self.application.syncdb['users'].find_one({'user': username})
#
#         self.thread = threading.Thread(target=self.compute_password, args=(password, user,))
#         self.thread.start()
#
#     def compute_password(self, password, user):
#         if user and 'password' in user:
#             if bcrypt.hashpw(password, user['password']) == user['password']:
#                 tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self._password_correct_callback, user['user']))
#                 return
#         tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self._password_fail_callback))
#
#     def _password_correct_callback(self, username):
#         self.set_current_user(username)
#         self.redirect(self.get_argument('next', '/'))
#
#     def _password_fail_callback(self):
#         self.set_flash('Error Login incorrect')
#         self.redirect('/login')
#
#
# class RegisterHandler(LoginHandler):
#     def get(self):
#         self.render("play.html", next=self.get_argument("next", "/"))
#
#     def post(self):
#         username = self.get_argument("username", "")
#
#         already_taken = self.application.syncdb['users'].find_one({'user': username})
#         if already_taken:
#             error_msg = u"?error=" + tornado.escape.url_escape("Login name already taken")
#             self.redirect(u"/login" + error_msg)
#
#         Warning bcrypt will block IO loop:
        # password = self.get_argument("password", "")
        # password = password.encode('utf-8')
        # hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt(8))
        #
        # user = {'user': username,
        #         'password': hashed_pass}
        #
        # auth = self.application.syncdb['users'].save(user)
        # self.set_current_user(username)
        # self.redirect("hello")
#
# class LogoutHandler(BaseHandler):
#     def get(self):
#         self.clear_cookie("user")
#         self.redirect(u"/login")


class ThreadHandler(tornado.web.RequestHandler):
    def perform(self, callback):
        #do something cuz hey, we're in a thread!
        time.sleep(5)
        output = 'foo'
        tornado.ioloop.IOLoop.instance().add_callback(functools.partial(callback, output))

    def initialize(self):
        self.thread = None

    @tornado.web.asynchronous
    def get(self):
        self.thread = threading.Thread(target=self.perform, args=(self.on_callback,))
        self.thread.start()

        self.write('In the request')
        self.flush()

    def on_callback(self, output):
        logging.info('In on_callback()')
        self.write("Thread output: %s" % output)
        self.finish()


class HelloHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        messages = self.get_messages()
        if self.get_current_user() is None:
            self.redirect('/login')

        self.render("index.html", user=self.get_current_user(), messages=messages, notification=self.get_flash())

    def get_messages(self):
        return self.application.syncdb.messages.find()

    def post(self):
        return self.get()


# class EmailMeHandler(BaseHandler):
#     @tornado.web.asynchronous
#     @tornado.gen.engine
#     def get(self):
#         http_client = AsyncHTTPClient()
#         mail_url = self.settings["mandrill_url"] + "/messages/send.json"
#         mail_data = {
#             "key": self.settings["mandrill_key"],
#             "message": {
#                 "html": "html email from tornado sample app <b>bold</b>",
#                 "text": "plain text email from tornado sample app",
#                 "subject": "from tornado sample app",
#                 "from_email": "hello@retechnica.com",
#                 "from_name": "Hello Team",
#                 "to": [{"email": "sample@retechnica.com"}]
#             }
#         }
#
#         body = tornado.escape.json_encode(mail_data)
#         response = yield tornado.gen.Task(http_client.fetch, mail_url, method='POST', body=body)
#         logging.info(response)
#         logging.info(response.body)
#
#         if response.code == 200:
#             self.set_secure_cookie('flash', "sent")
#             self.redirect('/')
#         else:
#             self.set_secure_cookie('flash', "FAIL")
#             self.redirect('/')


# class MessageHandler(BaseHandler):
#     def get(self):
#         users = self.application.syncdb['users'].find()
#         self.render("message.html", user=self.get_current_user(), users=users, notification=self.get_flash())
#
#     def post(self):
#         sent_to = self.get_argument('to')
#         sent_from = self.get_current_user()
#         message = self.get_argument("message")
#         msg = {}
#         msg['from'] = sent_from
#         msg['to'] = sent_to
#         msg['message'] = message
#
#         if self.save_message(msg):
#             self.set_secure_cookie('flash', "Message Sent")
#             self.redirect(u"/hello")
#         else:
#             print("error_msg")
#
#     def save_message(self, msg):
#         return self.application.syncdb['messages'].insert(msg)


class GameScreenHandler(BaseHandler):
    def get(self):
        users = self.application.clients
        user = self.get_current_user()
        if user not in self.application.game.players:
            self.application.game.add_player(user)

        self.render("game_screen.html", user=user, users=users)

    def post(self, *args, **kwargs):
        users = self.application.clients
        self.render("game_screen.html", users=users)

class HandHandler(BaseHandler):
    def get(self):
        print('Showing %s their hand' % self.get_current_user())
        self.render("hand.html", hand=self.application.game.get_player_by_name(self.get_current_user()).hand)


class UserHandler(BaseHandler):
    def get(self):
        return self.get_current_user()


class PreGameHandler(BaseHandler):
    def get(self):
        return self.application.game.pre_game


#
# class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
#     def initialize(self, clients):
#         self.clients = clients
#
#     def open(self, *args):
#         print("open", "WebSocketChatHandler")
#         self.id = uuid.uuid4()
#         self.clients[self.id] = self
#         print('New Connection')
#
#     def on_message(self, message):
#         print(message)
#         message_json = json.loads(message)
#
#         # if message_json.get('room'):
#         #     if message_json['room'] not in rooms:
#         #         rooms.append({str(message_json['room']): Room(room_name=str(message_json['room']))})
#
#         for client in self.clients.values():
#             client.get(self.id).write_message(message)
#             client_list_message = generate_client_list_message(self.clients.values())
#             print(client_list_message)
#             for client in self.clients:
#                 client.write_message(client_list_message)
#
#     def on_close(self):
#         self.clients.pop(self.id)

#
#
# def generate_client_list_message(clients_by_name_list=None):
#     clients_name_dict = {"type": "client_list_update",
#                          'clients_list': (str(clients_by_name_list))}
#     return json.dumps(clients_name_dict)
# #