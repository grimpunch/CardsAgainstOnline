__author__ = 'christian'

class Room():
    """
        Handles individual rooms for playing and chatting
    """
    def __init__(self, room_name):
        self.room_name = room_name
        self.clients = {}

    def get_clients(self):
        return str(self.clients.keys())