__author__ = 'Tharun'

import os

from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key=os.urandom(64))
    return app