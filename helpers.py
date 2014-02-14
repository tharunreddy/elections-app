__author__ = 'Tharun'

import re
import logging
import urllib
from google.appengine.api import mail

CONFIRMATION_URL = "http://elections-test.appspot.com/verify?%s"

def generate_verification_code():
    return "".join([string.ascii_letters[random.randint(0, 51)] for _ in range(10)])

def verify_penn_email(email):
    return re.search(r"(\.upenn\.edu)$", email)

def send_verification_email(email, id, code):
    """
    Function to send mail to the given email with id and verification code
    """

    params = urllib.urlencode({'id': id, 'verification_code': code})
    url = CONFIRMATION_URL % params

    ## sending mail
    logging.info("Mailing to %s, with link %s", email, url)
    message = mail.EmailMessage()
    message.sender = "tarunreddy.bethi@gmail.com"
    message.to = email
    message.body = """
    Please confirm your email by clicking %s""" % url
    message.send()
    return
