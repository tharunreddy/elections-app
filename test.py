__author__ = 'Tharun'

import random
import string

def generate_verification_code():
    code = ""
    for _ in range(12):
        code += string.ascii_letters[random.randint(0, 51)]
    return code

for _ in range(5):
    print generate_verification_code()
