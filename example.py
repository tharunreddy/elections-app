#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
A barebones AppEngine application that uses Facebook for login.

1.  Make sure you add a copy of facebook.py (from python-sdk/src/)
    into this directory so it can be imported.
2.  Don't forget to tick Login With Facebook on your facebook app's
    dashboard and place the app's url wherever it is hosted
3.  Place a random, unguessable string as a session secret below in
    config dict.
4.  Fill app id and app secret.
5.  Change the application name in app.yaml.

"""
FACEBOOK_APP_ID = "608511272550491"
FACEBOOK_APP_SECRET = "7cf6282934b900d77afe7c4ceed90669"
URL = "http://elections-test.appspot.com/verify?%s"

import facebook
import webapp2
import os
import jinja2
import re
import urllib
import logging
import datetime

from google.appengine.api import mail
from google.appengine.ext import db
from webapp2_extras import sessions

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='fart')


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    email_verified = db.BooleanProperty(required=True)
    verification_code = db.StringProperty(required=True)


class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                # Okay so user logged in.
                # Now, check to see if existing user
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    email_verified = False
                    verification_code = "bart"
                    user = User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"],
                        email_verified = email_verified,
                        verification_code = verification_code
                    )
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = dict(
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token,
                    email_verified = user.email_verified,
                    verification_code = user.verification_code
                )
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()

def verify_penn_email(email):
    return re.search(r"(\.upenn\.edu)$", email)

def send_verification_email(email, id, code):
    params = urllib.urlencode({'id': id, 'verification_code': code})
    url = URL % params
    logging.info("Mailing to %s, with link %s", email, url)
    message = mail.EmailMessage()
    message.sender = "tarunreddy.bethi@gmail.com"
    message.to = email
    message.body = """
    Please confirm your email by clicking %s""" % url
    message.send()



class HomeHandler(BaseHandler):
    def get(self):

        if self.current_user is not None:
            if self.current_user['email_verified']:
                self.redirect('/nominations')
                #self.response.out.write("Email verified")
                return

        template = jinja_environment.get_template('example.html')
        self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=self.current_user,
            error_msg=""
        )))

    def post(self):
        email = self.request.get('email')
        logging.info("Entered email "+email)
        if not verify_penn_email(email):
            template = jinja_environment.get_template('example.html')
            self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=self.current_user,
            error_msg="Invalid Email id")))
            return
        else:
            send_verification_email(email, self.current_user['id'], self.current_user['verification_code'])
            template = jinja_environment.get_template('verification_email_sent.html')
            self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=self.current_user,
            email=email)))


class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None
        self.redirect('/')

class VerifyHandler(BaseHandler):
    def get(self):
        verification_code = self.request.get('verification_code')
        id = self.request.get('id')
        user = User.get_by_key_name(id)

        if not user:
            self.response.out.write("Invalid user, may be something went wrong")
            return

        if user.email_verified:
            self.redirect('/nominations')
        else:
            if user.verification_code == verification_code:
                user.email_verified = True
                user.put()
                self.response.out.write("Email verified, redirecting you to elections page")
                self.redirect('/nominations')
        return

class NominationsHandler(BaseHandler):
    def get(self):
        self.response.out.write("Current time is %s. Check back when nominations start."%datetime.datetime.now())

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

app = webapp2.WSGIApplication(
    [('/', HomeHandler),
     ('/logout', LogoutHandler),
        ('/verify', VerifyHandler),
        ('/nominations', NominationsHandler)],
    debug=True,
    config=config
)