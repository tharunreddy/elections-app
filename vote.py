__author__ = 'Tharun'

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='fart')

import logging
import json
import os
import jinja2
import webapp2

import collections
from main import BaseHandler
from models import User
from candidates import CANDIDATES
from google.appengine.ext import db

class VotingHandler(BaseHandler):

    def _get_result(self, data, DATA):
        data = collections.Counter(data)
        result_dict = {cand: 0 for cand in DATA}
        for cand in result_dict:
            if cand in DATA:
                result_dict[cand] = data[cand]
        total_votes = sum(result_dict.values())
        result_dict = {cand: result_dict[cand]*100/float(total_votes) for cand in result_dict}
        result_dict = {DATA[cand]: result_dict[cand] for cand in result_dict}
        return result_dict


    def get(self, position):
        if self.current_user is not None:
            if position in CANDIDATES:
                user = User.get_by_key_name(self.current_user['id'])
                count = getattr(user, position+"_count")
                query = "SELECT %s FROM User" % position
                data = list(db.GqlQuery(query))
                data = map(lambda obj: getattr(obj, position), data)
                results = self._get_result(data, CANDIDATES[position])
                dump = {"results": results, "count": count}
                json_dump = json.dumps(dump)
                self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                self.response.out.write(json_dump)

    def post(self, position):
        if self.current_user is not None and self.current_user['email_verified']:
            user = User.get_by_key_name(self.current_user['id'])
            if user is not None:
                user_chair = self.request.get(position)
                if user_chair in CANDIDATES[position]:
                    if getattr(user, position+"_count") < 4:
                        setattr(user, position, user_chair)
                        count = getattr(user, position+"_count")
                        setattr(user, position+"_count", count+1)
                user.put()
            else:
                logging.warning("User is none while posting for position " + position)
        else:
            logging.warning("current user is none when posting for "+position)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

app = webapp2.WSGIApplication(
       [('/vote/([a-z]+)', VotingHandler),],
       debug=True,
       config=config)
