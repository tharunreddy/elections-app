#!/usr/bin/env python
#
# Penn Rangoli Elections 2014
#

FACEBOOK_APP_ID = "608511272550491"
FACEBOOK_APP_SECRET = "7cf6282934b900d77afe7c4ceed90669"


import facebook
import webapp2
import os
import jinja2
import logging
import datetime
import json
from collections import Counter

from webapp2_extras import sessions
from helpers import verify_email,\
                    send_verification_email, \
                    generate_verification_code
from candidates import CHAIRS, COMMUNICATIONS_CHAIR, GAPSA_LIASON, MARKETING_CHAIR, OPERATIONS_CHAIR, SOCIAL_CHAIR, \
                       TREASURER, VICE_CHAIR, WEB_ADMIN


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
            self.response.out.write("Invalid user, may be something went wrong")
            return

        #user has already been verified, so redirect him to elections page
        if user.email_verified:
            logging.info("User's email is verified, redirecting him to elections page")
            self.redirect('/vote')
        else:
            logging.info("Verifying user's Verification cod")
            if user.verification_code == verification_code:
                user.email_verified = True
                logging.info("email verified set to true")
                user.put()
                User.update_cache()
                self.render("verified_email.html")
                self.redirect('/logout')
            else:
                self.render("email_form.html", error_msg="Your Verification Code is wrong. Try again.")
        return None

class EmailHandler(WriteHandler):
    def get(self):
        # if user is not verified, send him a confirmation page
        try:
            logging.info("I'm in email handler and user is "+str(self.current_user['name']))
        except:
            logging.info("self.current_user error")
            return

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
            self.render("email_form.html", error_msg="Email already Verified")
            return

        if User.is_pennid_verified(email):
            self.render("email_form.html", error_msg="Penn ID already verified")
            return

        # if email is not verified
        #logging.info("current user is "+self.current_user)
        if not self.current_user['email_verified']:
            User.set_email(self.current_user['id'], email)
            send_verification_email(email, self.current_user)
            logging.info("Writing verification email sent")
            self.render("verification_email_sent.html", email=email)

class VotingHandler(WriteHandler):
    def get(self):
        if self.current_user is not None:
            user = User.get_by_key_name(self.current_user['id'])
            if self.current_user['email_verified']:
                self.render("vote.html")
        else:
            self.redirect("/")

    def post(self):
        pass


class ChairHandler(BaseHandler):
    """
    def get(self):
        some_result = {'saxena': 30, 'nirmal': 31}
        dump_json = json.dumps(some_result)

        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(dump_json)
    """

    def get(self):
        if self.current_user is not None:
            all_data = User.all_data()
            chair = [user.chair for user in all_data]
            counted = Counter(chair)
            if None in counted:
                del counted[None]
            total_votes = sum(counted.values())
            return json.dumps({x:y/total_votes for x,y in counted.iteritems()})


    def post(self):
        logging.info("Posted chair")
        logging.info(self.request.get("chair"))
        if self.current_user is not None:
            user = User.get_by_key_name(self.current_user['id'])
        chair = self.request.get("chair")
        if chair in CHAIRS:
            if user.chair_count is None:
                user.chair = chair
                user.chair_count = 1
            elif user.chair_count < 4:
                user.chair = chair
                user.chair_count += 1
            else:
                pass
        user.put()


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

app = webapp2.WSGIApplication(
       [('/', HomeHandler),
        ('/logout', LogoutHandler),
        ('/verify', VerifyHandler),
        ('/email', EmailHandler),
        ('/vote', VotingHandler),
        ('/vote/chair', ChairHandler)],
    debug=True,
    config=config
)