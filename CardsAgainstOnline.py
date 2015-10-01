from flask_interface.app import APP
from ipgetter import myip
import socket

debug = False
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
    return 'http://' + str(myip()) + ':' + str(port) + '/' + ' or ' + 'http://' + str(socket.gethostbyname(socket.gethostname())) + ':' + str(port) + '/'


def main():
    port = 8888
    APP.external_address = str(externaladdress(port))
    APP.game_thread.start()
    APP.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()
