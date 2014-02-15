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


import facebook
import webapp2
import os
import jinja2
import logging
import datetime

#from gaesessions import get_current_session
from webapp2_extras import sessions

from helpers import verify_email,\
                    send_verification_email, \
                    generate_verification_code


from models import User

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='fart')

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
                    verification_code = generate_verification_code()
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

class WriteHandler(BaseHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['facebook_app_id']=FACEBOOK_APP_ID
        params['current_user']=self.current_user
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class HomeHandler(WriteHandler):
    def get(self):
        self.render("main.html", error_msg="")

class LogoutHandler(WriteHandler):
    def get(self):
        if self.current_user is not None:
            self.session["user"] = None
        self.redirect('/')

class VerifyHandler(WriteHandler):
    def get(self):
        verification_code = self.request.get('verification_code')
        id = self.request.get('id')

        # fetch user from database
        user = User.get_by_key_name(id)

        # below should not happen
        if not user:
            self.response.out.write("Invalid user, may be something went wrong")
            return

        #user has already been verified, so redirect him to elections page
        if user.email_verified:
            self.write("You are already verified")
            #self.redirect('/nominations')
        else:
            if user.verification_code == verification_code:
                user.email_verified = True
                logging.info("email verified set to true")
                user.put()
                User.update_cache()
                self.render("verified_email.html")
                self.redirect('/logout')

class EmailHandler(WriteHandler):
    def get(self):
        # if user is not verified, send him a confirmation page
        logging.info("I'm in email handler and "+str(self.current_user))
        if self.current_user is None:
            self.redirect('/')
            return
        if not self.current_user['email_verified']:
            self.render("email_form.html", error_msg="")
        else:
            self.redirect('/vote')

    def post(self):
        logging.info(self.request.cookies)
        email = self.request.get('email')
        logging.info("Entered email "+email)

        if not verify_email(email):
            self.render("email_form.html", error_msg="Invalid Email")
            return

        if User.is_email_verified(email):
            self.render("email_form.html", error_msg="User already Verified")
            return
        # if email is not verified
        #logging.info("current user is "+self.current_user)

        if not self.current_user['email_verified']:
            send_verification_email(email, self.current_user['id'], self.current_user['verification_code'])
            User.set_email(self.current_user['id'], email)
            logging.info("Writing verification email sent")
            self.render("verification_email_sent.html", email=email)

class VotingHandler(WriteHandler):
    def get(self):
        self.render("vote.html")

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

app = webapp2.WSGIApplication(
     [('/', HomeHandler),
        ('/logout', LogoutHandler),
        ('/verify', VerifyHandler),
        ('/email', EmailHandler),
        ('/vote', VotingHandler)],
    debug=True,
    config=config
)