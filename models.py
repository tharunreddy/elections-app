__author__ = 'Tharun'

from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import os
import jinja2

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
    vicechair = db.StringProperty(required=False)
    treasurer = db.StringProperty(required=False)
    socialchair = db.StringProperty(required=False)
    operationschair = db.StringProperty(required=False)
    gapsaliason = db.StringProperty(required=False)
    communicationschair = db.StringProperty(required=False)
    webadmin = db.StringProperty(required=False)
    marketingchair = db.StringProperty(required=False)

    #counts
    chair_count = db.IntegerProperty(required=False, default=0)
    vicechair_count = db.IntegerProperty(required=False, default=0)
    treasurer_count = db.IntegerProperty(required=False, default=0)
    socialchair_count = db.IntegerProperty(required=False, default=0)
    operationschair_count = db.IntegerProperty(required=False, default=0)
    gapsaliason_count = db.IntegerProperty(required=False, default=0)
    communicationschair_count = db.IntegerProperty(required=False, default=0)
    webadmin_count = db.IntegerProperty(required=False, default=0)
    marketingchair_count = db.IntegerProperty(required=False, default=0)

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



class Answer(db.Model):
    answer = db.TextProperty(required=True)
    answered_by = db.StringProperty(required=True)
    answerer_name = db.StringProperty(required=True)
    upvoted_by = db.ListProperty(str)

    def get_votes(self):
        return len(self.upvoted_by)

    def get_upvote_link(self):
        return "/q/question/upvote/%s"%self.key().id()

def render_str(template, **params):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
        t = jinja_environment.get_template(template)
        return t.render(params)


class Question(db.Model):
    question = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    answers = db.ListProperty(item_type=db.Key,required=True)
    asked_by = db.StringProperty(required=True)
    asker_name = db.StringProperty(required=True)


    def render(self):
        self._render_text = self.question.replace('\n', '<br>')
        return render_str("question.html", q = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'question': self.question,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d

    def link(self):
        qid = self.key().id()
        href_link = "/q/question/%s"%str(qid)
        return href_link

