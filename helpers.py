__author__ = 'Chitrang'

import re
import logging
import urllib
import string
import random
from google.appengine.api import mail

extra_users = ["cpshah1507@gmail.com","srkotaru@mail.med.upenn.edu","div@mail.med.upenn.edu"]
EMAIL_RE = re.compile(r"([A-Za-z0-9_]+)@([A-Za-z0-9]+)(\.upenn\.edu)$")
email_message = """

Dear %s,

You have requested to verify the following Facebook profile - %s - for Rangoli Elections 2015.
Please confirm your email by clicking on the following link:

%s

If it isn't you, please ignore!

"""

def generate_verification_code():
    return "".join([string.ascii_letters[random.randint(0, 51)] for _ in range(10)])

def verify_email(email):
    return EMAIL_RE.match(email) or email in extra_users

def send_verification_email(email, user, verify_url):
    """
    Function to send mail to the given email with id and verification code
    """

    params = urllib.urlencode({'id': user['id'], 'verification_code': user['verification_code']})
    url = verify_url+"?"+ params

    ## sending mail
    logging.info("Mailing to %s, with link %s", email, url)
    message = mail.EmailMessage()
    message.sender = "rangolielections2015@gmail.com"
    message.subject = "Rangoli Elections 2015"
    message.to = email
    message.body = email_message % (user['name'], user['profile_url'], url)
    message.send()
    return
