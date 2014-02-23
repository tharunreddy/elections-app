__author__ = 'Tharun'

import webapp2
import os
import jinja2
from models import Question, Answer
from main import BaseHandler, WriteHandler
import logging
from google.appengine.ext import db
from collections import OrderedDict

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='fart')


class HomepageHandler(WriteHandler):
    def get(self):
        questions = list(Question.all())
        questions = sorted(questions, key=lambda x: len(x.answers), reverse=True)
        q_dict = OrderedDict()
        for question in questions:
            answers = question.answers
            answers = list(db.get(answers))
            answers = sorted(answers, key=lambda answer: answer.get_votes(), reverse=True)
            if len(answers) != 0:
                q_dict[question] = answers[0].answer
            else:
                q_dict[question] = "No answers yet"
        self.render("quora_homepage.html", q_dict=q_dict)

class AskHandler(WriteHandler):
    def get(self):
        if self.current_user is not None:
            self.render("ask_question.html", user = self.current_user)

    def post(self):
        if self.current_user is not None:
            question = self.request.get("question")
            user_anon = self.request.get("user_anon")
            asker_name = None
            if user_anon == "anon":
                asker_name = "Anonymous"
            elif user_anon == "notanon":
                asker_name = self.current_user['name']
            else:
                pass
            q = Question(question=question, asked_by=self.current_user['name'], asker_name = asker_name)
            q.put()
            self.redirect("/quora")

class QuestionHandler(WriteHandler):
    def get(self, qid):
        if self.current_user is not None:
            key = db.Key.from_path('Question', int(qid))
            question = db.get(key)
            logging.info(question.question)

            if not question:
                self.error(404)
                return

            self.render("display_question.html", q=question, answers = db.get(question.answers), user=self.current_user)

    def post(self, qid):
        if self.current_user is not None:
            key = db.Key.from_path('Question', int(qid))
            question = db.get(key)

            if not question:
                self.error(404)
                return

            answer = self.request.get('answer')
            user_anon = self.request.get('user_anon')
            answerer_name = None
            if user_anon == "anon":
                answerer_name = "Anonymous"
            elif user_anon == "notanon":
                answerer_name = self.current_user['name']
            a = Answer(answer=answer, answered_by=self.current_user['name'], answerer_name=answerer_name)
            a.put()

            question.answers.append(a.key())
            question.put()
            self.redirect('/quora/question/%s'%qid)

class UpvoteHandler(WriteHandler):
    def get_answer(self, aid):
        key = db.Key.from_path('Answer', int(aid))
        answer = db.get(key)
        return answer

    def already_voted(self, answer, name):
        return name in list(answer.upvoted_by)

    def get(self, aid):
        if self.current_user is not None:
            answer = self.get_answer(aid)
            upvoted_by = list(answer.upvoted_by)
            already_voted = self.already_voted(answer, self.current_user['name'])
            upvotes = answer.get_votes()
            self.render_json({"upvotes": upvotes, "already_voted": already_voted})

    def post(self, aid):
        if self.current_user is not None:
            answer = self.get_answer(aid)
            upvoted_by = list(answer.upvoted_by)
            already_voted = self.already_voted(answer, self.current_user['name'])
            if not already_voted:
                answer.upvoted_by.append(self.current_user['name'])
            answer.put()
            #self.redirect("/quora")

template_dir = os.path.join(os.path.dirname(__file__), 'templates/quora')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


app = webapp2.WSGIApplication([
    webapp2.Route('/quora', handler=HomepageHandler),
    webapp2.Route('/quora/ask', handler=AskHandler),
    ('/quora/question/([0-9]+)',QuestionHandler,'question'),
    ('/quora/question/upvote/([0-9]+)', UpvoteHandler)
], debug=True, config=config)