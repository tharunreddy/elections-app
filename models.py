__author__ = 'Tharun'


from google.appengine.ext import db

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
    def add_email(cls, id, email):
        user = User.get_by_key_name(id)
        user.email = email
        return user

