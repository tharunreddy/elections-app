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
    return re.search(r"([A-Za-z0-9_]+)@([A-Za-z0-9]+)(\.upenn\.edu)$", email)

def get_penn_id(email):
    return email.split("@")[0]

assert get_penn_id("tharun@seas.upenn.edu") == "tharun"
assert get_penn_id("nityaa@design.upenn.edu") == "nityaa"

assert not verify_email("")
assert verify_email("tharun@seas.upenn.edu")
assert verify_email("nityaa@design.upenn.edu")
assert not verify_email("yolo@upenn.edu")
assert not verify_email("yolo@gmail.com")

