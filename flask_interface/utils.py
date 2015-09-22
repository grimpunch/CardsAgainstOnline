from datetime import datetime, timedelta

def create_expiration_cookie_time():
    tomorrow = datetime.now() + timedelta(days=2)
    tomorrow = datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = tomorrow.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
    return expires