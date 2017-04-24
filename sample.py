import re
import logging
import urllib
import string
import random
from google.appengine.api import mail
from google.appengine.api import app_identity
import webapp2
import sendgrid
from sendgrid.helpers import mail


def generate_verification_code():
    code = ""
    for _ in range(12):
        code += string.ascii_letters[random.randint(0, 51)]
    return code