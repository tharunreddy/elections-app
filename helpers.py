__author__ = 'Chitrang'
#__modificationsdoneby__ = 'Anupam'

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

extra_users = ["cpshah1507@gmail.com","srkotaru@mail.med.upenn.edu","div@mail.med.upenn.edu","chaitanya2537@gmail.com","anupamalur@gmail.com"]
EMAIL_RE = re.compile(r"([A-Za-z0-9_]+)@([A-Za-z0-9]+)(\.upenn\.edu)$")

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
    emailmsg = """
    
    Dear """ + user['name'] + """,
    
    You have requested to verify the following Facebook profile - """ + user['profile_url'] + """ - for Rangoli Elections 2017.
    Please confirm your email by copy pasting this link in your browser:
    
    """ + url + """
    
    If it isn't you, please ignore! If for some reason, you are unable to verify your account, please contact us. 
    Thank you! 
    
    """
    sg = sendgrid.SendGridAPIClient(apikey="SG.uE1I4nF7TZOu4VI41usSkw.wEOEUWMbEEzUPMdlSpVenHBeRFWsj9IrR2ekawr2MZE")
    to_email = mail.Email(email)
    from_email = mail.Email("rangolielections2017@gmail.com")
    subject = 'Your account has been verified'
    content = mail.Content('text/plain', emailmsg)
    message = mail.Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=message.get())

    return

class SendMessageHandler(webapp2.RequestHandler):
    def get(self):
        send_approved_mail('{}@appspot.gserviceaccount.com'.format(
            app_identity.get_application_id()))
        self.response.content_type = 'text/plain'
        self.response.write('Sent an email message to Albert.')


app = webapp2.WSGIApplication([
    ('/send_message', SendMessageHandler),
], debug=True)
