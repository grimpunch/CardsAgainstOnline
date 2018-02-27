from flask_interface.app import CAH_lobby_server, socketio
from ipgetter import myip
import socket

LANIP = None

debug = True  # was this borken? Have added line below and log now shows exceptions, might be able to delete this
CAH_lobby_server.debug = True
# Important note about Debug!
#  If you run the server you will notice that the server is only accessible
#  from your own computer, not from any other in the network.
#  This is the default because in debugging mode a user of the application
#  can execute arbitrary Python code on your computer.
#  So to be externally accessible, you have to disable debug mode.


def externaladdress(port):
    """
    Should return a string of either way to get connected to the machine running the game for display on screen.
    Need to look in to making this detect if we are on wlan or ethernet.
    :param port:
    :return:
    """
    lan_ip_for_message = None
    global LANIP
    if LANIP:
        lan_ip_for_message = LANIP
    else:
        lan_ip_for_message = LANIP = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                                      for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    message = 'http://' + str(myip()) + ':' + str(port) + '/'
    if lan_ip_for_message:
        message += ' or ' + 'http://' + str(lan_ip_for_message) + ':' + str(port) + '/'
    return message


def main():
    port = 8888
    CAH_lobby_server.external_address = str(externaladdress(port))
    socketio.run(CAH_lobby_server, host=LANIP, port=port)

if __name__ == '__main__':
    main()
