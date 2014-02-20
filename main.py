#!/usr/bin/env python
#
# Penn Rangoli Elections 2014
#

FACEBOOK_APP_ID = "608511272550491"
FACEBOOK_APP_SECRET = "7cf6282934b900d77afe7c4ceed90669"
RANGOLI_GROUP_ID = "39581072545"

import facebook
import webapp2
import os
import jinja2
import logging

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

    def is_part_of_group(self, cookie, group_id):
        logging.info("Entering checking for is part of group")
        graph = facebook.GraphAPI(cookie['access_token'])
        groups = graph.get_connections("me", "groups")
        for group in groups['data']:
            logging.info("group name" + group['name'])
            if group['id'] == group_id:
                return True
        return False

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
                        verification_code = verification_code,
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
                    verification_code = user.verification_code,
                    is_part_of_rangoli = self.is_part_of_group(cookie, RANGOLI_GROUP_ID)
                )
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
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
            logging.warning("Invalid User, this must not happen in Verify Handler")
            self.redirect('/logout')
            return

        #user has already been verified, so redirect him to elections page
        if user.email_verified:
            logging.info("User's email is verified, redirecting him to elections page")
            self.redirect('/vote')
        else:
            logging.info("Verifying user's Verification code")
            if user.verification_code == verification_code:
                user.email_verified = True
                user.put()
                #TODO Ask gopi to put a verified email and redirecting to homepage
                self.render("verified_email.html")
                self.redirect('/logout')
            else:
                #TODO Ask gopi to put a verification code is wrong message and take him to login page
                self.render("email_form.html", error_msg="Your Verification Code is wrong. Try again.")
        return None

class EmailHandler(WriteHandler):
    def get(self):
        # if user is not verified, send him a confirmation page
        if self.current_user is None:
            self.redirect('/')
            return

        if not self.current_user['is_part_of_rangoli']:
            logging.info("Not a part of rangoli")
            self.redirect('/notrangoli')
            return

        if not self.current_user['email_verified']:
            self.render("email_form.html", error_msg="")
        else:
            self.redirect('/vote')

    def post(self):
        if self.current_user is not None:

            if not self.current_user['is_part_of_rangoli']:
                self.redirect('/notrangoli')
                return

            email = self.request.get('email')

            if not verify_email(email):
                self.render("email_form.html", error_msg="Not a Valid UPenn email or email not registered with Rangoli")
                return

            if User.is_email_verified(email):
                self.render("email_form.html", error_msg="Email already Verified")
                return

            if User.is_pennid_verified(email):
                logging.warning("Penn ID already verified but %s is trying to use different email" % self.current_user['name'])
                self.render("email_form.html", error_msg="Penn ID already verified")
                return

            # if email is not verified
            #logging.info("current user is "+self.current_user)
            if not self.current_user['email_verified']:
                user = User.get_by_key_name(self.current_user['id'])
                if user is None:
                    logging.warning("User is None when posting email in confirm email page")
                    self.redirect("/logout")
                    return
                user.email = email
                user.penn_id = email.split("@")[0]
                user.put()
                send_verification_email(email, self.current_user, webapp2.uri_for('verify', _full=True))
                self.render("verification_email_sent.html", email=email)
            else:
                # User's email is already verified so redirecting him to voting page
                self.redirect("/vote")

        else:
            # if user is none
            self.redirect('/logout')

class NotRangoliHandler(WriteHandler):
    def get(self):
        #if self.current_user is not None:
        #    self.session["user"] = None
        self.render("not_rangoli.html")


class VotingPageHandler(WriteHandler):
    def get(self):
        if self.current_user is not None:
            user = User.get_by_key_name(self.current_user['id'])
            if self.current_user['email_verified']:
                self.render("vote.html", user=user)
        else:
            self.redirect("/logout")

    def post(self):
        pass

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

app = webapp2.WSGIApplication(
       [webapp2.Route('/', handler=HomeHandler),
        webapp2.Route('/logout', handler=LogoutHandler),
        webapp2.Route('/verify', handler=VerifyHandler, name="verify"),
        webapp2.Route('/email', handler=EmailHandler),
        webapp2.Route('/vote', handler=VotingPageHandler),
        webapp2.Route('/notrangoli', handler=NotRangoliHandler),],
    debug=True,
    config=config
)