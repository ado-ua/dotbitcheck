"""
Script to check status of dotbit accounts
"""

import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import time
import random
from optparse import OptionParser
import sys

"""
Options for script
"""
options = OptionParser(usage="%prog [options]", description="Dotbit accounts checker")
options.add_option("-f", "--file", help="filename with ids listed (one id per line)")
options.add_option("-s", "--session", help="session id")
options.add_option("-l", "--loop", help="loop indefinetly, defalut - False", default="False", action="store_true")

opts, args = options.parse_args()
print opts.file

"""
Errors handling
a) no file nor session id supplied
b) both file and session id supplied
c) file supplied but it can not be acessed
"""
if opts.file is None and opts.session is None:
    print "Error. Filename or session id should be used"
    sys.exit()
if opts.file and opts.session:
    options.error("options -f and -f are mutually exclusive")
if opts.file:
    try:
        file_handler = open(opts.file)
    except:
        print "Error. File is not found."
        sys.exit()

"""
Some configuration variables
"""
url = "https://dotbit.me/your_account/"
user_agent = "Mozilla/5.0"

"""
session_check(session id) - session check function, receive session id, returns tupil with coins
"""
def session_check(session):
    session_header = "dotbit_session=" + session
    headers = { "User-Agent" : user_agent, "Cookie" : session_header }
    req = urllib2.Request(url, "GET", headers)
    response = urllib2.urlopen(req)
    response_page = response.read()
    soup = BeautifulSoup(''.join(response_page))
    btc = soup.findAll(id="totalbitcoin")[0]
    ltc = soup.findAll(id="totallitecoin")[0]
    ppc = soup.findAll(id="totalpeercoin")[0]
    xmp = soup.findAll(id="totalprimecoin")[0]
    return (session,btc.text,ltc.text,ppc.text,xmp.text)

"""
main(sessions, loop) - main program logic, receive list of sessions for check and bool if loop should be infinite
"""
def main(sessions, loop):
    old_responses = list()
    new_responses = list()
    while (True):
        session_index = 0
        response_index = 0
        for session in sessions:
            session_check(session)
            try:
                new_responses[session_index] = -1
            except:
                new_responses.append(session_index)
                old_responses.append(session_index)

            new_responses[session_index] = session_check(session)
            session_index = session_index + 1
        print new_responses
        for response in new_responses:
            if response == old_responses[response_index]:
                print response[0], "not updated"
                response_index = response_index + 1
            else:
                old_responses[response_index] = response
                print response[0], "updated"
                print "BTC: ", float(response[1]), "LTC: ", float(response[2]), "PPC: ", float(response[3]), "XMP: ", float(response[4])
                response_index = response_index + 1
        if loop == False:
            break

if opts.file:
    sessions = list()
    file_handler = open(opts.file)
    for session in file_handler:
        sessions.append(session)
else:
    sessions = (opts.session,)

main(sessions,opts.loop)
