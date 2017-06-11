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
import logserv
import time
import access_control
import datetime
import db
import markdown
import urllib2
import json
import thread
import string


"""
    Sends an /acknowledge API call on messages on the current page
    that have not been marked as SEEN. The messages are then marked
    as SEEN. Only messages from the currently loaded page are processed
    by this method. Runs in a seperate thread so as to not hinder the user.
"""


def sendAcknowledge(messageList, userID, userdata):
    for row in messageList:
        if row['status'] != 'SEEN':
            if row['sender'] == userID:
                try:
                    stuff = {'sender': row['sender'], 'stamp': row['stamp'],
                             'hashing': row['hashing'], 'hash': row['hash']}
                    for peer in logserv.peerList:
                        if row['sender'] == peer['username']:
                            if peer['ip'] == userdata.ip:
                                db.updateMessageStatus(row, 'SEEN')
                                continue
                            elif peer['location'] == '2':
                                pass
                            elif peer['location'] == userdata.location:
                                pass
                            else:
                                continue
                            payload = json.dumps(stuff)
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                                peer['port']) + '/acknowledge', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req, timeout=1).read()
                            db.updateMessageStatus(row, 'SEEN')
                except:
                    pass


class internalJSON(object):

    """
        Retrieves peer list data and formats it for
        displaying in the sidebar. Data is returned 
        as JSON for processing by Handlebar.JS
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getPeerListJSON(self):
        somelist = db.getPeerList()
        for peer in somelist:
            if peer['fullname'] == None:
                peer['fullname'] = peer['username']

            lastLogin = time.strftime(
                "%Y/%m/%d, %H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
            if int(peer['lastLogin'] or 0) + 86400 > int(time.time()):
                peer['lastLogin'] = time.strftime(
                    "%H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
            elif peer['lastLogin'] == None:
                peer['lastLogin'] = 'NEVER'
            else:
                peer['lastLogin'] = time.strftime(
                    "%a, %d %b %Y", time.localtime(float(peer['lastLogin'] or 0)))

            if peer['status'] == "Online":
                peer['fullname'] = peer['fullname'] + u' 🔵'
            elif peer['status'] == "Idle":
                peer['fullname'] = peer['fullname'] + u' 💁'
            elif peer['status'] == "Away":
                peer['fullname'] = peer['fullname'] + u' ⭕'
            elif peer['status'] == 'Do Not Disturb':
                peer['fullname'] = peer['fullname'] + u' 🔴'
            else:
                peer['fullname'] = peer['fullname'] + u' ◯'

            if peer['picture'] == None:
                peer['picture'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"
        peerlist = {str(k): v for k, v in enumerate(somelist)}
        return peerlist

    """
        Retrieves event list data and formats it for
        displaying in the sidebar. Data is returned 
        as JSON for processing by Handlebar.JS
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getEventListJSON(self):
        somelist = db.getEventList()
        for item in somelist:
            item['time'] = time.strftime(
                "%H:%M on %d/%m/%Y", time.localtime(float(item['start_time'])))
        return somelist

    """
        Retrieves message data and formats it for
        displaying in the webpage. Data is returned 
        as JSON for processing by Handlebar.JS
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getMessageListJSON(self):
        userID = cherrypy.serving.request.headers['Referer']
        userID = userID.split('%27')[1]
        messageList = db.readOutMessages(
            userID, cherrypy.session['userdata'].username)
        contact = db.getUserProfile(userID)[0]
        userdata = db.getUserProfile(cherrypy.session['userdata'].username)[0]
        thread.start_new_thread(
            sendAcknowledge, (messageList, userID, cherrypy.session['userdata']))
        for row in messageList:
            row['stamp'] = time.strftime(
                "%Y/%m/%d, %H:%M:%S", time.localtime(float(row['stamp'])))
            row['fullname'] = userdata['fullname']
            row['picture'] = userdata['picture']
            row['message'] = string.replace(row['message'], "''", "'")
            if int(row['markdown']) == 1:
                row['message'] = markdown.markdown(row['message'])
            row['username'] = contact['username']
            if row['sender'] == userdata['username']:
                pass
            else:
                if contact['fullname'] != None:
                    row['fullname'] = contact['fullname']
                else:
                    row['fullname'] = contact['username']

                if contact['picture'] == None:
                    row['picture'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"
                else:
                    row['picuture'] = contact['picture']
        somelist = {str(k): v for k, v in enumerate(messageList)}
        return somelist

    """
        Retrieves event data and formats it for
        displaying in the webpage. Data is returned 
        as JSON for processing by Handlebar.JS
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getEventDetailsJSON(self):
        name = cherrypy.serving.request.headers['Referer']
        final = {}
        final['sender'] = name.split('%27')[1]
        final['event_name'] = name.split('%27')[3]
        final['start_time'] = name.split('%27')[5]
        final['event_name'] = urllib2.unquote(final['event_name'])
        orig = db.getEvent(final['event_name'], final['start_time'])
        final['start_time'] = time.strftime(
            "%H:%M", time.localtime(float(final['start_time'])))
        final['event_description'] = orig[0]['event_description']
        final['event_location'] = orig[0]['event_location']
        final['event_picture'] = orig[0]['event_picture']
        final['end_time'] = time.strftime(
            "%H:%M on %d/%m/%Y", time.localtime(float(orig[0]['end_time'])))
        if orig[0]['markdown'] == 1:
            final['event_description'] = markdown.markdown(
                final['event_description'])
        for item in orig:
            if str(item['status']) == '0':
                item['status'] = "Not Going"
            if str(item['status']) == '1':
                item['status'] = "Going"
            if str(item['status']) == '2':
                item['status'] = "Maybe"
            fullname = db.getUserProfile(item['destination'])[0]['fullname']
            if fullname != None:
                item['destination'] = fullname
        if final['sender'] == cherrypy.session['userdata'].username:
            final['responses'] = orig
        else:
            final['dropdown'] = 'true'
            statusTypes = {'x': 'Going', 'y': 'Maybe', 'z': 'Not Going'}
            for typ in statusTypes:
                if statusTypes[typ] == orig[0]['status']:
                    final[typ] = 'true'
        return final

    """
        Retrieves profile data and formats it for
        displaying in the edit profile page. Data is
        returned as JSON for processing by Handlebar.JS
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getProfileDetailsJSON(self):
        data = db.getUserData(cherrypy.session['userdata'].username)[0]
        data['blacklist'] = ",".join(access_control.getBlackList())
        if data['tfa'] == 'on':
            pass
        else:
            del data['tfa']
        return data

    """
        Generates JSON data for generating the Status setting
        toolbar. Data is sent to Handlebar.JS for rendering.
    """
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getHTMLStatus(self):
        statusTypes = {'a': 'Online', 'b': 'Idle',
                       'c': 'Do Not Disturb', 'd': 'Away', 'e': 'Offline'}
        for user in logserv.listLoggedInUsers:
            if user['username'] == cherrypy.session['userdata'].username:
                for typ in statusTypes:
                    if statusTypes[typ] == user['status']:
                        return {typ: 'true'}
