__author__ = 'Tharun'

import random
import string
import re


def generate_verification_code():
    code = ""
    for _ in range(12):
        code += string.ascii_letters[random.randint(0, 51)]
    return code

for _ in range(5):
    print generate_verification_code()

def verify_email(email):
    return re.search(r"(\.upenn\.edu)$", email)

assert not verify_email("")

print """

Dear %s,

You have requested to verify the following Facebook profile - %s - for Rangoli Elections 2014.
Please confirm your email by clicking on the following link:

%s

If the above Facebook profile isn't you, please ignore!

""" %("1", "2", "3")