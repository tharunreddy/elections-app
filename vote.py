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
from google.appengine.api import memcache


class VotingHandler(BaseHandler):

    def _get_result(self, data, DATA):
        data = collections.Counter(data)
        result_dict = {cand: data.get(cand, 0) for cand in DATA}
        total_votes = sum(result_dict.values())
        res = None
        if total_votes > 0:
            res = {DATA[cand]: round(result_dict[cand]*100/float(total_votes), 2) for cand in result_dict}
        else:
            res = dict([(cand, 0) for cand in DATA.values()])
        return res

    def set_cache(self, query, key):
        data = list(db.GqlQuery(query))
        if not memcache.set(key, data):
            logging.warning("memcache set failed for setting position data")
            return False
        return True

    def get(self, position):
        if self.current_user is not None:
            if position in CANDIDATES:
                user = User.get_by_key_name(self.current_user['id'])
                position_count = getattr(user, position+"_count")
                position_count = 3 - position_count
                query = "SELECT %s FROM User" % position
                data = list(db.GqlQuery(query))
                data = map(lambda obj: getattr(obj, position), data)
                results = self._get_result(data, CANDIDATES[position])
                dump = {"results": results, "count": position_count}
                self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                self.response.out.write(json.dumps(dump))
        else:
            logging.warning("Current user is none in get request for a position")

    def post(self, position):
        if position not in CANDIDATES:
            logging.warning("Got position which is out of candidates")
            return
        if self.current_user is not None and self.current_user['email_verified'] and self.current_user['is_part_of_rangoli']:
            user = User.get_by_key_name(self.current_user['id'])
            if user is not None:
                user_vote = self.request.get(position)
                if user_vote in CANDIDATES[position]:
                    if getattr(user, position+"_count") < 4:
                        setattr(user, position, user_vote)
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
