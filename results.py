__author__ = 'Tharun'

import requests
from candidates import CANDIDATES

URL = "http://rangolielections2014.appspot.com/vote/"

def main():
    for position in CANDIDATES:
        url = URL+position
        #print url
        j = requests.get(url)
        print j.text


main()
