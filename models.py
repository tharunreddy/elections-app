__author__ = 'Tharun'

from google.appengine.api import memcache
from google.appengine.ext import db
import logging

class User(db.Model):

    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    email = db.StringProperty(required=False)
    email_verified = db.BooleanProperty(required=True)
    verification_code = db.StringProperty(required=True)

    @classmethod
    def update_data(cls):
        all_data = db.GqlQuery("SELECT *"
                                    "FROM User")
        all_data = list(all_data)
        return all_data

    @classmethod
    def set_email(cls, id, email):
        user = User.get_by_key_name(id)
        user.email = email
        user.put()
        memcache.set('users', User.update_data())

    @classmethod
    def is_email_verified(cls, email):
        all_data = memcache.get('users')
        if all_data is not None:
            all_emails = {user.email : user.email_verified for user in all_data}
            logging.info(all_emails)
            return all_emails.get(email, False)




