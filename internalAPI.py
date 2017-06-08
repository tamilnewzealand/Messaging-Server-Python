# coding=utf8

import cherrypy
import json
import urllib2
import protocol_login_server
import db
import time
import access_control
import datetime
import base64
import hashlib
import mimetypes
import os
import messageProcess

class internalAPI(object):

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
    def processEvent(self, destinations, event_name, start_time, end_time, event_description='', event_location='', event_picture=''):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            destinations = destinations.split(',')
            start_time = time.mktime(datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M").timetuple())
            end_time = time.mktime(datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M").timetuple())
            for destination in destinations:
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
    def updateProfile(self, picture, description, location, position, fullname, blacklist, tfa='off'):
        db.updateUserData(cherrypy.session['userdata'].username, picture, description, location, position, fullname, tfa)
        access_control.setBlackList(blacklist)
        if cherrypy.session['userdata'].currentChat == '':
            raise cherrypy.HTTPRedirect("home")
        else:
            raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")

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
    def makeHandshake(self, destination):
        text = protocol_login_server.randomword(512)
        data = {'message': text, 'sender': cherrypy.session['userdata'].username, 'destination': destination, 'markdown': '1', 'stamp': str(int(time.time())), 'encryption': '0', 'hashing': '0', 'hash': ' '}
        for peer in protocol_login_server.peerList:
            if peer['username'] == destination:
                data = messageProcess.process(data, peer)
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
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/handshake', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req).read()
                    response = json.loads(response)
                    if response['message'] == text:
                        return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
                except:
                    return ('7: Hash does not match')
        return ('2: Unauthenticated User')