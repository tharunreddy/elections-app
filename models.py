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
    penn_id = db.StringProperty(required=False)
    email_verified = db.BooleanProperty(required=True)
    verification_code = db.StringProperty(required=True)

    #posts
    chair = db.StringProperty(required=False)
    chair_count = db.IntegerProperty(required=False)
    vice_chair = db.StringProperty(required=False)
    treasurer = db.StringProperty(required=False)
    social_chair = db.StringProperty(required=False)
    operations_chair = db.StringProperty(required=False)
    gapsa_liason = db.StringProperty(required=False)
    communications_chair = db.StringProperty(required=False)
    web_admin = db.StringProperty(required=False)
    marketing_chair = db.StringProperty(required=False)

    @classmethod
    def all_data(cls):
        all_data = db.GqlQuery("SELECT *"
                                    "FROM User")
        return list(all_data)
        #logging.info("updating cache")
        #memcache.set('users', list(all_data))

    @classmethod
    def set_email(cls, id, email):
        user = User.get_by_key_name(id)
        penn_id = email.split("@")[0]
        user.email = email
        user.penn_id = penn_id
        user.put()
        #User.update_cache()

    @classmethod
    def is_email_verified(cls, email):
        data = User.all_data()
        if data is not None:
            all_emails = {user.email : user.email_verified for user in data}
            logging.info("all email information "+ str(all_emails))
            return all_emails.get(email, False)

    @classmethod
    def is_pennid_verified(cls, email):
        penn_id = email.split("@")[0]
        all_data = User.all_data()
        if all_data is not None:
            all_penn_ids = {user.penn_id: user.email_verified for user in all_data}
            logging.info("all penn id information" + str(all_penn_ids))
            return all_penn_ids.get(penn_id, False)




