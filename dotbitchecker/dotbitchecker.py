"""
Script to check status of dotbit accounts
Copyright (C) 2014 ado-ua

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
        for response in new_responses:
            if response == old_responses[response_index]:
                print response[0].rstrip(), "not updated"
                response_index = response_index + 1
            else:
                old_responses[response_index] = response
                print response[0].rstrip(), "updated"
                if float(response[1]) > 0:
                    btc = "\033[92m" + str(round(float(response[1]),1)) + "\033[0m"
                else:
                    btc = float(response[1])
                if float(response[2]) > 0:
                    ltc = "\033[92m" + str(round(float(response[2]),1)) + "\033[0m"
                else:
                    ltc = float(response[2])
                if float(response[3]) > 0:
                    ppc = "\033[92m" + str(round(float(response[3]),1)) + "\033[0m"
                else:
                    ppc = float(response[3])
                if float(response[4]) > 0:
                    xmp = "\033[92m" + str(round(float(response[4]),1)) + "\033[0m"
                else:
                    xmp = float(response[4])
                print "BTC: ", btc, "LTC: ", ltc, "PPC: ", ppc, "XMP: ", xmp
                response_index = response_index + 1
        if loop == "False":
            break

# Construction of array based on input given
if opts.file:
    sessions = list()
    file_handler = open(opts.file)
    for session in file_handler:
        sessions.append(session)
else:
    sessions = (opts.session,)

main(sessions,opts.loop)
