from Server import Room
import json
import uuid
import os

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.util
import tornado.template


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render("index.html")

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print("open", "WebSocketChatHandler")
        self.id = uuid.uuid4()
        clients[self.id] = self
        print('New Connection')

    def on_message(self, message):
        print(message)
        message_json = json.loads(message)

        if message_json.get('room'):
            if message_json['room'] not in rooms:
                rooms.append({str(message_json['room']): Room(room_name=str(message_json['room']))})

        for client in clients.values():
            client.get(self.id).write_message(message)
            # client_list_message = generate_client_list_message(clients_by_name)
            # print(client_list_message)
            # for client in clients:
            #     client.write_message(client_list_message)

    def on_close(self):
        clients.pop(self.id)

def generate_client_list_message(clients_by_name_list=None):
    clients_name_dict = {"type": "client_list_update",
                         'clients_list': (str(clients_by_name_list))}
    return json.dumps(clients_name_dict)



clients = {}
rooms = []

handlers = [(r'/chat', WebSocketChatHandler), (r'/', MainHandler)]
settings = dict(
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=True,
    )
app = tornado.web.Application(handlers, **settings)
app.listen(8888)
tornado.ioloop.IOLoop.instance().start()

