__author__ = 'Chitrang'
#__modificationsdoneby__ = 'Anupam'

import requests
from candidates import CANDIDATES

URL = "https://rangolielections2017-160817.appspot.com/vote/"

def main():
    for position in CANDIDATES:
        url = URL+position
        #print url
        j = requests.get(url)
        print j.text


main()
