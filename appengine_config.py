__author__ = 'Chitrang'

import os
from google.appengine.ext import vendor

#Add any libraries install in the "lib" folder.
vendor.add('lib')

from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key=os.urandom(64))
    return app
