# coding=utf8

import cherrypy
import protocol_login_server
import time
import datetime
import db
import markdown
import urllib2
import json
import string

def sendAcknowledge(data, ip):
    try:
        stuff = {'sender': data['sender'], 'stamp': data['stamp'], 'hashing': data['hashing'], 'hash': data['hash']}
        for peer in protocol_login_server.peerList:
            if data['sender'] == peer['username']:
                if peer['ip'] == cherrypy.session['userdata'].ip:
                    db.updateMessageStatus(data, 'SEEN')
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == cherrypy.session['userdata'].location:
                    pass
                else:
                    continue
                payload = json.dumps(stuff)
                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/acknowledge', payload, {'Content-Type': 'application/json'})
                response = urllib2.urlopen(req).read()
                db.updateMessageStatus(data, 'SEEN')
    except:
        pass

class internalJSON(object):
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getPeerListJSON(self):
        somelist = db.getPeerList()
        for peer in somelist:
            if peer['fullname'] == None:
                peer['fullname'] = peer['username']
                
            lastLogin = time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
            if int(peer['lastLogin'] or 0) + 86400 > int(time.time()):
                peer['lastLogin'] = time.strftime("%H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
            elif peer['lastLogin'] == None:
                peer['lastLogin'] = 'NEVER'
            else:
                peer['lastLogin'] = time.strftime("%a, %d %b %Y", time.localtime(float(peer['lastLogin'] or 0)))

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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getEventListJSON(self):
        somelist = db.getEventList()
        for item in somelist:
            item['time'] = time.strftime("%H:%M on %d/%m/%Y", time.localtime(float(item['start_time'])))
        return somelist
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getMessageListJSON(self):
        userID = cherrypy.serving.request.headers['Referer']
        userID = userID.split('%27')[1]
        messageList = db.readOutMessages(userID, cherrypy.session['userdata'].username)
        contact = db.getUserProfile(userID)[0]
        userdata = db.getUserProfile(cherrypy.session['userdata'].username)[0]
        for row in messageList :
            if row['status'] != 'SEEN':
                if row['sender'] == userID:
                    sendAcknowledge(row, cherrypy.session['userdata'].ip)
            row['stamp'] = time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(float(row['stamp'])))
            row['fullname'] = userdata['fullname']
            row['picture'] = userdata['picture']
            row['message'] = string.replace(row['message'], "''", "'")
            if int(row['markdown']) == 1:
                row['message'] = markdown.markdown(row['message'])
            row['username'] = contact['username']
            if row['sender'] == userdata['username'] :
                pass
            else :
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
        final['start_time'] = time.strftime("%H:%M", time.localtime(float(final['start_time'])))
        final['event_description'] = orig[0]['event_description']
        final['event_location'] = orig[0]['event_location']
        final['event_picture'] = orig[0]['event_picture']
        final['end_time'] = time.strftime("%H:%M on %d/%m/%Y", time.localtime(float(orig[0]['end_time'])))
        if orig[0]['markdown'] == 1:
            final['event_description'] = markdown.markdown(final['event_description'])
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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getHTMLStatus(self):
        statusTypes = {'a': 'Online', 'b': 'Idle', 'c': 'Do Not Disturb', 'd': 'Away', 'e': 'Offline'}
        for user in protocol_login_server.listLoggedInUsers:
            if user['username'] == cherrypy.session['userdata'].username:
                for typ in statusTypes:
                    if statusTypes[typ] == user['status']:
                        return {typ: 'true'}