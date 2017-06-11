# coding=utf8

"""   
    Peer to Peer Chat Application
    
    Copyright (C) 2017 Sakayan Sitsabesan <ssit662@aucklanduni.ac.nz>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """

import cherrypy
import thread
import time

accessList = []

"""
    Retrieves the current blacklist that has been
    stored to a file and returns it as a list.
"""


def getBlackList():
    blacklist = open("blacklist.txt", "r")
    lines = blacklist.read().split(',')
    blacklist.close()
    return lines


"""
    Saves a new black list to the text file.
"""


def setBlackList(listings):
    blacklist = open("blacklist.txt", "w")
    blacklist.write(listings)
    blacklist.close()


"""
    Main access control function that is called by 
    every external facing API to restrict access.
    This function will check the IP is not in the black
    list and will also rate limit by adding every IP 
    to the ratelimiting list. If an IP appears more than
    100 times a minute, that IP is ratelimited till the
    next minute.
"""


def access_control():
    ip = cherrypy.request.headers["Remote-Addr"]
    if ip in getBlackList():
        return False
    accessList.append(ip)
    if accessList.count(ip) > 100:
        return False
    return True


"""
    Seperate thread that clears the rate limiting
    list every 60 seconds to reset the rate limiting
    feature.
"""


def ac_timer(started):
    starttime = time.time()
    while True:
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        global accessList
        accessList = []
