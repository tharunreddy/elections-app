__author__ = 'Chitrang'

import requests
from candidates import CANDIDATES

URL = "http://rangolielections2015.appspot.com/vote/"

def main():
    for position in CANDIDATES:
        url = URL+position
        #print url
        j = requests.get(url)
        print j.text


main()
