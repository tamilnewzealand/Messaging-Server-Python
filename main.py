# coding=utf8

import json
import urllib2
import cherrypy
import db
import protocol_login_server
import time
import hashlib
import base64
import markdown
import messageProcess
import mimetypes
import string
import os
import thread
import access_control
import Ciphers
from Crypto.Hash import SHA512
from cherrypy.lib.static import serve_fileobj

thread.start_new_thread(access_control.ac_timer, ('0', ))

def sizeb64(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)

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

def stop():
    if cherrypy.session['userdata'] != None:
        protocol_login_server.protocol_login_server.logoff_API_call(cherrypy.session['userdata'])
        del cherrypy.session['userdata']
        del protocol_login_server.listLoggedInUsers

class MainClass(object):
    @cherrypy.expose
    def logout(self):
        if 'userdata' in cherrypy.session:
            protocol_login_server.protocol_login_server.logoff_API_call(cherrypy.session['userdata'])
            thisUser = None
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    thisUser = user
            protocol_login_server.listLoggedInUsers.remove(thisUser)
            del cherrypy.session['userdata']
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def login(self):
        if 'userdata' in cherrypy.session:
            cherrypy.session['userdata'] = None
            return file("login.html")
        if 'userdata' not in cherrypy.session:
            return file("login.html")
        else:
            raise cherrypy.HTTPRedirect("home")

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
    def updateEventStatus(self, newStatus):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            data = {'attendance': '0'}
            if newStatus == 'Not Going':
                data['attendance'] = '0'
            if newStatus == 'Going':
                data['attendance'] = '1'
            if newStatus == 'Maybe':
                data['attendance'] = '2'
            name = cherrypy.serving.request.headers['Referer']
            data['sender'] = name.split('%27')[1]
            data['event_name'] = name.split('%27')[3]
            data['start_time'] = name.split('%27')[5]
            data['event_name'] = urllib2.unquote(data['event_name'])
            db.updateEventStatus(data['attendance'], data['sender'], data['event_name'], data['start_time'])
            for peer in protocol_login_server.peerList:
                if data['sender'] == peer['username']:
                    if peer['ip'] == cherrypy.session['userdata'].ip:
                        continue
                    elif peer['location'] == '2':
                        pass
                    elif peer['location'] == cherrypy.session['userdata'].location:
                        pass
                    else:
                        continue
                    payload = json.dumps(data)
                    try:
                        req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/acknowledgeEvent', payload, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req).read()
                    except:
                        pass
            raise cherrypy.HTTPRedirect("event?sender='" + data['sender'] + "'&name='" + data['event_name'] + "'&start_time='" + data['start_time'] + "'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def login_check(self, username, password):
        hashed = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
        cherrypy.session['userdata'] = protocol_login_server.protocol_login_server(username, hashed)
        protocol_login_server.protocol_login_server.reporter_thread(cherrypy.session['userdata'])
        if cherrypy.session['userdata'].tfa:
            raise cherrypy.HTTPRedirect("tfa.html")
        if cherrypy.session['userdata'].status:
            newUser = {'username': cherrypy.session['userdata'].username, 'rsakey': cherrypy.session['userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            protocol_login_server.listLoggedInUsers.append(newUser)
            if len(protocol_login_server.listLoggedInUsers) == 1:
                protocol_login_server.protocol_login_server.peerlist_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.profile_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.retrieve_messages_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.peerstatus_thread(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")
    
    @cherrypy.expose
    def tfa_check(self, seccode):
        if int(seccode) == int(cherrypy.session['userdata'].seccode):
            cherrypy.session['userdata'].status = True
            cherrypy.session['userdata'].tfa = False
        if cherrypy.session['userdata'].status:
            newUser = {'username': cherrypy.session['userdata'].username, 'rsakey': cherrypy.session['userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            protocol_login_server.listLoggedInUsers.append(newUser)
            if len(protocol_login_server.listLoggedInUsers) == 1:
                protocol_login_server.protocol_login_server.profile_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.peerlist_thread(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def home(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("home.html")
        else:
            cherrypy.session['userdata'] = None
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def calendar(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("calendar.html")
        else:
            cherrypy.session['userdata'] = None
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def processEvent(self, destination, event_name, start_time, end_time, event_description='', event_location='', event_picture=''):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            data = {'sender': cherrypy.session['userdata'].username, 'destination': destination, 'event_name': event_name, 'event_description': event_description, 'event_location': event_location, 'event_picture': event_picture, 'start_time': start_time, 'end_time': end_time}
            packet = data
            for peer in protocol_login_server.peerList:
                if peer['username'] == packet['sender']:
                    packet = messageProcess.processProf(packet, peer)
                    if peer['ip'] == cherrypy.session['userdata'].ip:
                        continue
                    elif peer['location'] == '2':
                        pass
                    elif peer['location'] == cherrypy.session['userdata'].location:
                        pass
                    else:
                        continue
                    payload = json.dumps(packet)
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveEvent', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req).read()
            db.addNewEvent(data)
            raise cherrypy.HTTPRedirect("event?sender='" + data['sender'] + "'&name='" + data['event_name'] + "'&start_time='" + data['start_time'] + "'")
        else:
            raise cherrypy.HTTPRedirect("login")
    
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
    def editProfile(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("editprofile.html")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def updateProfile(self, picture, description, location, position, fullname, blacklist, tfa='off'):
        db.updateUserData(cherrypy.session['userdata'].username, picture, description, location, position, fullname, tfa)
        access_control.setBlackList(blacklist)
        if cherrypy.session['userdata'].currentChat == '':
            raise cherrypy.HTTPRedirect("home")
        else:
            raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getHTMLStatus(self):
        statusTypes = {'a': 'Online', 'b': 'Idle', 'c': 'Do Not Disturb', 'd': 'Away', 'e': 'Offline'}
        for user in protocol_login_server.listLoggedInUsers:
            if user['username'] == cherrypy.session['userdata'].username:
                for typ in statusTypes:
                    if statusTypes[typ] == user['status']:
                        return {typ: 'true'}

    @cherrypy.expose
    def chat(self, userID):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            userID = userID.replace("\'", "")
            cherrypy.session['userdata'].currentChat = userID
            return file("chat.html")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def event(self, sender, name, start_time):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentEvent = {'sender': sender.replace("\'", ""), 'name': name.replace("\'", ""), 'start_time': start_time.replace("\'", "")}
            return file("event.html")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def updateStatus(self, newStatus):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    user['status'] = newStatus
            if cherrypy.session['userdata'].currentChat == '':
                raise cherrypy.HTTPRedirect("home")
            else:
                raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def sendMessage(self, message, attachments):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            data = {'sender': unicode(cherrypy.session['userdata'].username), 'destination': unicode(cherrypy.session['userdata'].currentChat), 'message': unicode(message), 'markdown': '1', 'stamp': str(int(time.time())), 'encryption': '0', 'hashing': '0', 'hash': ' '}
            files = False
            stuff = None
            text = ""
            try:
                filname = attachments.filename
                content_type = mimetypes.guess_type(filname)[0]
                attachments = base64.b64encode(attachments.file.read())
                file = open ('static/downloads/' + filname.encode("ascii"), "wb")
                file.write(base64.b64decode(attachments))
                file.close()
                text = '<a href="' + os.path.join('downloads', filname) + '" download>' + filname + '</a>'
                if 'image/' in content_type:
                    text = '<img src="' + os.path.join('downloads', filname) + '\" alt=\"' + filname + '\" width="320">'
                if 'audio/' in content_type:
                    text = '<audio controls><source src="' + os.path.join('downloads', filname) + '\" type=\"' + content_type + '\"></audio>'
                if 'video/' in content_type:
                    text = '<video width="320" height="240" controls><source src="' + os.path.join('downloads', filname) + '\" type=\"' + content_type + '\"></video>'
                stuff = {'sender': cherrypy.session['userdata'].username, 'destination': cherrypy.session['userdata'].currentChat, 'file': attachments, 'content_type': content_type,'filename': filname, 'stamp': unicode(int(time.time())), 'encryption': '0', 'hash': '', 'hashing': '0'}
                files = True
            except:
                pass
            if not files:
                db.addNewMessage(data)
            offline = True
            for peer in protocol_login_server.peerList:
                if cherrypy.session['userdata'].currentChat == peer['username']:
                    offline = False
            for peer in protocol_login_server.peerList:
                if not offline:
                    if cherrypy.session['userdata'].currentChat == peer['username']:
                        sentMessage = data
                        if cherrypy.session['userdata'].currentChat == cherrypy.session['userdata'].username:
                            peer['ip'] = 'localhost'
                        elif peer['location'] == '2':
                            pass
                        elif peer['location'] == cherrypy.session['userdata'].location:
                            pass
                        else:
                            raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
                        if data['message'] != "":
                            try:
                                data = messageProcess.process(data, peer)
                                payload = json.dumps(data)
                                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                                response = urllib2.urlopen(req).read()
                                if '0: ' in response:
                                    db.updateMessageStatus(sentMessage, 'DELIVERED')
                            except:
                                pass
                        if files:
                            payload = messageProcess.process(stuff, peer)
                            payload = json.dumps(payload)
                            try:
                                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                                response = urllib2.urlopen(req).read()
                                if '0: ' in response:
                                    sentMessage['message'] = sentMessage['message'] + text
                                    sentMessage['status'] = 'DELIVERED'
                                db.addNewMessage(sentMessage)
                            except:
                                pass
                        raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
            if offline:
                payload = json.dumps(data)
                payloads = json.dumps(stuff)
                for peer in protocol_login_server.peerList:
                    if cherrypy.session['userdata'].currentChat == cherrypy.session['userdata'].username:
                        continue
                    elif peer['location'] == '2':
                        pass
                    elif peer['location'] == cherrypy.session['userdata'].location:
                        pass
                    else:
                        continue
                    if data['message'] != "":
                        try:
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                            if '0: ' in response:
                                db.updateMessageStatus(data, 'IN TRANSIT')
                        except:
                            pass
                    if files:
                        try:
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveFile', payloads, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                        except:
                            pass
                        data['message'] = data['message'] + text
                        data['status'] = 'IN TRANSIT'
                        db.addNewMessage(data)
            raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        return file("404.html")

    @cherrypy.expose
    def listAPI(self):
        if access_control.access_control():
            return ("""Available APIs: 
/listAPI 
/ping [sender]
/receiveMessage [sender] [destination] [message] [stamp(opt)] [markdown] [encryption(opt)] [hashing(opt)] [hash(opt)]
/acknowledge [sender] [stamp] [hash] [hashing]
/getPublicKey [sender]
/handshake [message] [encryption]
/getProfile [sender]
/recieveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption] [hash]
/retrieveMessages [sender]
/getStatus [profile_username]
/getList [username] [encryption] [json]
/report [username] [passphrase] [signature] [location] [ip] [port] [encryption(opt)]
Encryption: 0, 1, 2, 3, 4
Hashing: 0, 1, 2, 3, 4, 5, 6, 7, 8""")
        else:
            return ("11: Blacklisted or Rate Limited")
        
    @cherrypy.expose
    def ping(self, sender):
        return ('0')
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        if access_control.access_control():
            data = cherrypy.request.json
            try:
                data = messageProcess.unprocess(data, protocol_login_server.listLoggedInUsers)
            except:
                return ('1: Missing Compulsory Field')
            if isinstance(data, basestring):
                return data
            
            data['status'] = 'IN TRANSIT'
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == data['destination']:
                    data['status'] = 'DELIVERED'
            
            if db.addNewMessage(data):
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            else:
                return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def acknowledge(self):
        if access_control.access_control():
            data = cherrypy.request.json
            if db.updateMessageStatus(data, 'SEEN'):
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            else:
                return (u'7: Hash does not match')
        else:
            return ("11: Blacklisted or Rate Limited")
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getPublicKey(self):
        if access_control.access_control():
            sender = cherrypy.request.json
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == sender['profile_username']:
                    return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'pubkey': user['pubkey']}
            return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handshake(self):
        if access_control.access_control():
            data = cherrypy.request.json
            if int(data['encryption']) == 1:
                data['message'] = Ciphers.XORCipher.decrypt(data['message'])
            if int(data['encryption']) == 2:
                data['message'] = Ciphers.AESCipher.decrypt(data['message'], '41fb5b5ae4d57c5ee528adb078ac3b2e')
            if int(data['encryption']) == 3:
                for user in protocol_login_server.listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['message'] = Ciphers.RSA1024Cipher.decryptValue(data['message'], user['rsakey'])
            if int(data['encryption']) == 4:
                for user in protocol_login_server.listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['decryptionKey'] = Ciphers.RSA1024Cipher.decryptValue(data['decryptionKey'], user['rsakey'])
                data['message'] = Ciphers.AESCipher.decrypt(data['message'], data['decryptionKey'])
            return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'message': data['message']}
        else:
            return ("11: Blacklisted or Rate Limited")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
        if access_control.access_control():
            try:
                sender = cherrypy.request.json
                data = db.getUserData(sender['profile_username'])[0]
                for peer in protocol_login_server.peerList:
                    if peer['username'] == sender['sender']:
                        data = messageProcess.processProf(data, peer)
                        return data
                return('2: Unauthenticated User')
            except:
                return('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        if access_control.access_control():
            data = cherrypy.request.json
            data = messageProcess.unprocess(data, protocol_login_server.listLoggedInUsers)
            if isinstance(data, basestring):
                return data
            if sizeb64(data['file']) > 6990506:
                return (u'6, உங்கள் கோப்பு எல்லைக்குள் இல்லை')
            file = open ('static/downloads/' + data['filename'].encode("ascii"), "wb")
            file.write(base64.b64decode(data['file']))
            file.close()
            content_type = mimetypes.guess_type(data['filename'])[0]
            text = '<a href="'  + os.path.join('downloads', data['filename']) + '\" download>' + data['filename'] + '</a>'
            if 'image/' in content_type:
                text = '<img src="'  + os.path.join('downloads', data['filename']) + '\" alt=\"' + data['filename'] + '\" width="320">'
            if 'audio/' in content_type:
                text = '<audio controls><source src="' + os.path.join('downloads', data['filename']) + '\" type=\"' + content_type + '\"></audio>'
            if 'video/' in content_type:
                text = '<video width="320" height="240" controls><source src="'  + os.path.join('downloads', data['filename']) + '\" type=\"' + content_type + '\"></video>'
            payload = {'sender': data['sender'], 'destination': data['destination'], 'message': text, 'stamp': data['stamp'], 'encryption': 2, 'hashing': 0, 'hash': '', 'status': 'IN TRANSIT', 'markdown': 0}
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == payload['destination']:
                    payload['status'] = 'DELIVERED'
            try:
                db.addNewMessage(payload)
            except:
                return('1: Missing Compulsory Field')
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("11: Blacklisted or Rate Limited")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def retrieveMessages(self):
        if access_control.access_control():
            inputs = cherrypy.request.json
            messages = db.getTransitingMessages(inputs['requestor'])
            for message in messages:
                if "downloads\\" in message['message']:
                    filname = message['message'].split("\\")[1].split('"')[0]
                    content_type = mimetypes.guess_type(filname)[0]
                    file = open ('static/downloads/' + filname.encode("ascii"), "rb")
                    attachments = base64.b64encode(file.read())
                    file.close()
                    for peer in protocol_login_server.peerList:
                        if message['destination'] == peer['username']:
                            stuff = {'sender': message['sender'], 'destination': message['destination'], 'file': attachments, 'content_type': content_type,'filename': filname, 'stamp': message['stamp'], 'encryption': 0, 'hash': '', 'hashing': 0}
                            payload = json.dumps(data)
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                            db.updateMessageStatus(message, 'DELIVERED')
                else:
                    data = message
                    for peer in protocol_login_server.peerList:
                        if message['destination']== peer['username']:
                            payload = json.dumps(data)
                            try:
                                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                                response = urllib2.urlopen(req).read()
                                db.updateMessageStatus(message, 'DELIVERED')
                            except:
                                pass
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("11: Blacklisted or Rate Limited")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getStatus(self):
        if access_control.access_control():
            data = cherrypy.request.json
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == data['profile_username']:
                    return {'status': user['status']}
            return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveEvent(self):
        if access_control.access_control():
            message = cherrypy.request.json
            for peer in protocol_login_server.peerList:
                    if peer['username'] == message['sender']:
                            message = messageProcess.unprocessProf(message, peer)
            if 'event_description' not in message:
                message['event_description'] = ''
            if 'event_location' not in message:
                message['event_location'] = ''
            if 'event_picture' not in message:
                message['event_picture'] = '' 
            if 'markdown' not in message:
                message['markdown'] = ''
            message['status'] = '0'
            if db.addNewEvent(message):
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            else:
                return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def acknowledgeEvent(self):
        if access_control.access_control():
            message = cherrypy.request.json
            try:
                updateEventStatus(message['attendance'], message['sender'], message['event_name'], message['start_time'])
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            except:
                return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    @cherrypy.expose
    def getList(self, username, json_format=0):
        if access_control.access_control():
            if int(json_format) == 1:
                peerlist = {str(k): v for k, v in enumerate(protocol_login_server.peerList)}
                return json.dumps(peerlist)
            else:
                resp = '0: '
                for peer in protocol_login_server.peerList:
                    resp = resp + peer['username'] + ',' + peer['location'] + ',' + peer['ip'] + ',' + peer['port'] + ',' + peer['lastLogin'] + ',' + peer['publicKey'] + ','
                return resp
        else:
            return ("11: Blacklisted or Rate Limited")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def report(self):
        if access_control.access_control():
            message = cherrypy.request.json
            hashed = SHA512.new(data['passphrase']).hexdigest()
            if message['signature'] == Ciphers.RSA1024Cipher.encryptValue(hashed, db.getUserProfile(message['username'])[0]['publicKey']):
                pass
        else:
            return ("11: Blacklisted or Rate Limited")

        
    WEB_ROOT = os.path.join(os.getcwd(), 'static') 

    cherrypy.config.update({'error_page.404': error_page_404,
                            'server.socket_host': '0.0.0.0',
                            'server.socket_port': 10008,
                            'engine.autoreload.on': False,
                            'tools.sessions.on': True,
                            'tools.encode.on': True,
                            'tools.encode.encoding': 'utf-8',
                            'tools.staticdir.on' : True,
                            'tools.staticdir.dir' : WEB_ROOT,
                            'tools.staticdir.index' : 'index.html'})

cherrypy.engine.subscribe('stop', stop)
cherrypy.quickstart(MainClass())