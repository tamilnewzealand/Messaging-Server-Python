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
import json
import urllib2
import logserv
import db
import time
import access_control
import datetime
import base64
import hashlib
import mimetypes
import os
import messageProcess
import thread


class internalAPI(object):

    @cherrypy.expose
    def login_check(self, username, password):
        hashed = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
        cherrypy.session['userdata'] = logserv.logserv(username, hashed)
        logserv.logserv.reporterThread(cherrypy.session['userdata'])
        if cherrypy.session['userdata'].tfa:
            raise cherrypy.HTTPRedirect("tfa.html")
        if cherrypy.session['userdata'].status:
            newUser = {'username': cherrypy.session['userdata'].username, 'hashed': cherrypy.session['userdata'].hashed, 'rsakey': cherrypy.session['userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            logserv.listLoggedInUsers.append(newUser)
            if len(logserv.listLoggedInUsers) == 1:
                logserv.logserv.peerListThread(cherrypy.session['userdata'])
                logserv.logserv.daemonInit(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def tfa_check(self, seccode):
        if int(seccode) == int(cherrypy.session['userdata'].seccode):
            cherrypy.session['userdata'].status = True
            cherrypy.session['userdata'].tfa = False
        if cherrypy.session['userdata'].status:
            newUser = {'username': cherrypy.session['userdata'].username, 'rsakey': cherrypy.session[
                'userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            logserv.listLoggedInUsers.append(newUser)
            if len(logserv.listLoggedInUsers) == 1:
                logserv.logserv.peerListThread(cherrypy.session['userdata'])
                logserv.logserv.daemonInit(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")
    
    @staticmethod
    def updateEventStatusDaemon(userdata, data):
        db.updateEventStatus(
            data['attendance'], data['sender'], data['event_name'], data['start_time'])
        for peer in logserv.peerList:
            if data['sender'] == peer['username']:
                if peer['ip'] == userdata.ip:
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == userdata.location:
                    pass
                else:
                    continue
                payload = json.dumps(data)
                try:
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                        peer['port']) + '/acknowledgeEvent', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req, timeout=2).read()
                except:
                    pass

    @cherrypy.expose
    def updateEventStatus(self, newStatus):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            data = {'attendance': '0'}
            name = cherrypy.serving.request.headers['Referer']
            if newStatus == 'Not Going':
                data['attendance'] = '0'
            if newStatus == 'Going':
                data['attendance'] = '1'
            if newStatus == 'Maybe':
                data['attendance'] = '2'
            data['sender'] = name.split('%27')[1]
            data['event_name'] = name.split('%27')[3]
            data['start_time'] = name.split('%27')[5]
            data['event_name'] = urllib2.unquote(data['event_name'])
            thread.start_new_thread(internalAPI.updateEventStatusDaemon, (cherrypy.session['userdata'], data))            
            raise cherrypy.HTTPRedirect(
                "event?sender='" + data['sender'] + "'&name='" + data['event_name'] + "'&start_time='" + data['start_time'] + "'")
        else:
            raise cherrypy.HTTPRedirect("login")
        
    @staticmethod
    def processEventDaemon(userdata, destinations, event_name, start_time, end_time, event_description, event_location, event_picture):
        destinations = destinations.split(',')
        end_time = time.mktime(datetime.datetime.strptime(
            end_time, "%Y-%m-%dT%H:%M").timetuple())
        for destination in destinations:
            data = {'sender': userdata.username, 'destination': destination, 'event_name': event_name, 'event_description': event_description,
                    'event_location': event_location, 'event_picture': event_picture, 'start_time': start_time, 'end_time': end_time, 'markdown': '1'}
            packet = data
            for peer in logserv.peerList:
                if peer['username'] == packet['sender']:
                    packet = messageProcess.processProf(packet, peer)
                    if peer['ip'] == userdata.ip:
                        continue
                    elif peer['location'] == '2':
                        pass
                    elif peer['location'] == userdata.location:
                        pass
                    else:
                        continue
                    payload = json.dumps(packet)
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                        peer['port']) + '/receiveEvent', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req, timeout=2).read()
            db.addNewEvent(data)

    @cherrypy.expose
    def processEvent(self, destinations, event_name, start_time, end_time, event_description='', event_location='', event_picture=''):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            start_time = time.mktime(datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M").timetuple())
            thread.start_new_thread(internalAPI.processEventDaemon, (cherrypy.session['userdata'], destinations, event_name, start_time, end_time, event_description, event_location, event_picture))
            raise cherrypy.HTTPRedirect(
                "event?sender='" + cherrypy.session['userdata'].username + "'&name='" + event_name + "'&start_time='" + start_time + "'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def updateProfile(self, picture, description, location, position, fullname, blacklist, tfa='off'):
        db.updateUserData(cherrypy.session['userdata'].username,
                          picture, description, location, position, fullname, tfa)
        access_control.setBlackList(blacklist)
        if cherrypy.session['userdata'].currentChat == '':
            raise cherrypy.HTTPRedirect("home")
        else:
            raise cherrypy.HTTPRedirect(
                "chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")

    @cherrypy.expose
    def updateStatus(self, newStatus):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            for user in logserv.listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    user['status'] = newStatus
            if cherrypy.session['userdata'].currentChat == '':
                raise cherrypy.HTTPRedirect("home")
            else:
                raise cherrypy.HTTPRedirect(
                    "chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @staticmethod
    def sendMessageDaemon(message, attachments, userdata):
        data = {'sender': unicode(userdata.username), 'destination': unicode(userdata.currentChat), 'message': unicode(
                message), 'markdown': '1', 'stamp': str(int(time.time())), 'encryption': '0', 'hashing': '0', 'hash': ' '}
        files = False
        stuff = None
        text = ""
        if attachments.file is not None:
            filname = attachments.filename
            content_type = mimetypes.guess_type(filname)[0]
            attachments = base64.b64encode(attachments.file.read())
            file = open('static/downloads/' +
                        filname.encode("ascii"), "wb")
            file.write(base64.b64decode(attachments))
            file.close()
            text = '<a href="' + \
                os.path.join('downloads', filname) + \
                '" download>' + filname + '</a>'
            if 'image/' in content_type:
                text = '<img src="' + \
                    os.path.join('downloads', filname) + \
                    '\" alt=\"' + filname + '\" width="320">'
            if 'audio/' in content_type:
                text = '<audio controls><source src="' + \
                    os.path.join('downloads', filname) + \
                    '\" type=\"' + content_type + '\"></audio>'
            if 'video/' in content_type:
                text = '<video width="320" height="240" controls><source src="' + \
                    os.path.join('downloads', filname) + \
                    '\" type=\"' + content_type + '\"></video>'
            stuff = {'sender': userdata.username, 'destination': userdata.currentChat, 'file': attachments,
                        'content_type': content_type, 'filename': filname, 'stamp': unicode(int(time.time())), 'encryption': '0', 'hash': '', 'hashing': '0'}
            files = True
        offline = True
        for peer in logserv.peerList:
            if userdata.currentChat == peer['username']:
                offline = False
        for peer in logserv.peerList:
            if not offline:
                if userdata.currentChat == peer['username']:
                    sentMessage = data.copy()
                    if userdata.currentChat == userdata.username:
                        peer['ip'] = 'localhost'
                    elif peer['location'] == '2':
                        pass
                    elif peer['location'] == userdata.location:
                        pass
                    else:
                        thread.exit()
                    if data['message'] is not u'':
                        try:
                            (data, hashing, hashe) = messageProcess.process(data, peer)
                            payload = json.dumps(data)
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                                peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req, timeout=2).read()
                            sentMessage['hash'] = hashe
                            sentMessage['hashing'] = hashing
                            if '0: ' in response:
                                sentMessage['status'] = 'DELIVERED'
                            db.addNewMessage(sentMessage)
                        except:
                            pass
                    if files:
                        (data, hashing, hashe) = messageProcess.process(stuff, peer)
                        payload = json.dumps(data)
                        try:
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                                peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                            if '0: ' in response:
                                sentMessage['message'] = sentMessage['message'] + text
                                sentMessage['status'] = 'DELIVERED'
                            sentMessage['hash'] = hashe
                            sentMessage['hashing'] = hashing
                            db.addNewMessage(sentMessage)
                        except:
                            pass
                    thread.exit()
        if offline:
            payload = json.dumps(data)
            payloads = json.dumps(stuff)
            for peer in logserv.peerList:
                if userdata.currentChat == userdata.username:
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == userdata.location:
                    pass
                else:
                    continue
                if data['message'] != "":
                    try:
                        req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                            peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req, timeout=2).read()
                        if '0: ' in response:
                            db.updateMessageStatus(data, 'IN TRANSIT')
                    except:
                        pass
                if files:
                    try:
                        req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                            peer['port']) + '/receiveFile', payloads, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req).read()
                    except:
                        pass
                    data['message'] = data['message'] + text
                    data['status'] = 'IN TRANSIT'
                    db.addNewMessage(data)
        thread.exit()

    @cherrypy.expose
    def sendMessage(self, message, attachments):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            thread.start_new_thread(internalAPI.sendMessageDaemon, (message, attachments, cherrypy.session['userdata']))
            raise cherrypy.HTTPRedirect(
                "chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def makeHandshake(self, destination):
        text = logserv.randomword(512)
        data = {'message': text, 'sender': cherrypy.session['userdata'].username, 'destination': destination, 'markdown': '1', 'stamp': str(
            int(time.time())), 'encryption': '0', 'hashing': '0', 'hash': ' '}
        for peer in logserv.peerList:
            if peer['username'] == destination:
                (data, hashing, hashe) = messageProcess.process(data, peer)
                if destination == cherrypy.session['userdata'].username:
                    peer['ip'] = 'localhost'
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == cherrypy.session['userdata'].location:
                    pass
                else:
                    raise cherrypy.HTTPRedirect("home")
                try:
                    payload = json.dumps(data)
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                        peer['port']) + '/handshake', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req, timeout=2).read()
                    response = json.loads(response)
                    if response['message'] == text:
                        return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
                except:
                    return ('7: Hash does not match')
        return ('2: Unauthenticated User')
