from flask_interface.app import APP

def main():
    APP.run(host='0.0.0.0', port=8888, debug=True)

if __name__ == '__main__':
    main()
