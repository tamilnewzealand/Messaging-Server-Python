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

import json
import urllib2
import cherrypy
import db
import logserv
import time
import base64
import markdown
import messageProcess
import mimetypes
import os
import string
import access_control
import Ciphers
from Crypto.Hash import SHA512
from cherrypy.lib.static import serve_fileobj


"""
    Returns the size of a base 64 string.
"""


def sizeb64(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)


class external(object):
    """
        Lists the APIs supported by the client, as well as the encryption and
        hashing standards. If the standards are not included, it is assumed that
        the client does not support any encoding (beyond ASCII), encryption, or
        hashing. The output is returned in plaintext (i.e. not JSON encoded).
    """
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
Encryption: 0 1 2 3 4
Hashing: 0 1 2 3 4 5 6 7 8""")
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        Allows another client to check if this client is still here before initiating
        other communication. It can also allow a client to test the round-trip delay time
        for messages to another node. No JSON encoding is required for this API.
    """
    @cherrypy.expose
    def ping(self, sender):
        return ('0')
    """
        This API allows another client to send this client a message.
        A single message, its metadata, and any control arguments are placed
        in a dictionary and then JSON encoded. All messages sent and received
        are stored locally. 
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        if access_control.access_control():
            data = cherrypy.request.json
            try:
                data = messageProcess.unprocess(
                    data, logserv.listLoggedInUsers)
            except:
                return ('1: Use my new private key already...')
            if isinstance(data, basestring):
                return data

            data['status'] = 'IN TRANSIT'
            for user in logserv.listLoggedInUsers:
                if user['username'] == data['destination']:
                    data['status'] = 'DELIVERED'

            if db.addNewMessage(data):
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            else:
                return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This marks a sent message as seen in the database
        if the hash matches.
    """
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

    """
        Returns the public key of the username that
        the request if for.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getPublicKey(self):
        if access_control.access_control():
            sender = cherrypy.request.json
            for user in logserv.listLoggedInUsers:
                if user['username'] == sender['profile_username']:
                    return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'pubkey': user['pubkey']}
            return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to confirm that a particular
        encryption standard is supported correctly by this client. 
        An encrypted message sent to this client will be decrypted, 
        and then returned in plaintext for verification at the other
        end. This can also be used for verifying users/clients with
        their public keys as necessary.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handshake(self):
        if access_control.access_control():
            data = cherrypy.request.json
            if int(data['encryption']) == 1:
                data['message'] = Ciphers.XORCipher.decrypt(data['message'])
            if int(data['encryption']) == 2:
                data['message'] = Ciphers.AESCipher.decrypt(
                    data['message'], '41fb5b5ae4d57c5ee528adb078ac3b2e')
            if int(data['encryption']) == 3:
                for user in logserv.listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['message'] = Ciphers.RSA1024Cipher.decryptValue(
                            data['message'], user['rsakey'])
            if int(data['encryption']) == 4:
                for user in logserv.listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['decryptionKey'] = Ciphers.RSA1024Cipher.decryptValue(
                            data['decryptionKey'], user['rsakey'])
                data['message'] = Ciphers.AESCipher.decrypt(
                    data['message'], data['decryptionKey'])
            return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'message': data['message']}
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to request information about 
        the user operating this client. It implies that the current
        user has a profile existing on this client that contains the
        necessary information.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
        if access_control.access_control():
            try:
                sender = cherrypy.request.json
                data = db.getUserData(sender['profile_username'])[0]
                for peer in logserv.peerList:
                    if peer['username'] == sender['sender']:
                        data = messageProcess.processProf(data, peer)
                        return data
                return('2: Unauthenticated User')
            except:
                return('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to send this client an
        arbitrary file (in binary). A single base64 encoded file,
        its metadata, and any control arguments should be in a
        dictionary and then JSON encoded. A maximum file size of 5MB 
        has been enforced for the purposes of prototype testing.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        if access_control.access_control():
            data = cherrypy.request.json
            data = messageProcess.unprocess(data, logserv.listLoggedInUsers)
            if isinstance(data, basestring):
                return data
            if sizeb64(data['file']) > 5242880:
                return (u'6, உங்கள் கோப்பு எல்லைக்குள் இல்லை')
            file = open('static/downloads/' +
                        data['filename'].encode("ascii"), "wb")
            file.write(base64.b64decode(data['file']))
            file.close()
            content_type = mimetypes.guess_type(data['filename'])[0]
            text = '<a href="' + \
                os.path.join(
                    'downloads', data['filename']) + '\" download>' + data['filename'] + '</a>'
            if 'image/' in content_type:
                text = '<img src="' + \
                    os.path.join(
                        'downloads', data['filename']) + '\" alt=\"' + data['filename'] + '\" width="320">'
            if 'audio/' in content_type:
                text = '<audio controls><source src="' + \
                    os.path.join(
                        'downloads', data['filename']) + '\" type=\"' + content_type + '\"></audio>'
            if 'video/' in content_type:
                text = '<video width="320" height="240" controls><source src="' + \
                    os.path.join(
                        'downloads', data['filename']) + '\" type=\"' + content_type + '\"></video>'
            payload = {'sender': data['sender'], 'destination': data['destination'], 'message': text,
                       'stamp': data['stamp'], 'encryption': data['encryption'], 'hashing': data['hashing'], 'hash': data['hash'], 'status': 'IN TRANSIT', 'markdown': 0}
            for user in logserv.listLoggedInUsers:
                if user['username'] == payload['destination']:
                    payload['status'] = 'DELIVERED'
            try:
                db.addNewMessage(payload)
            except:
                return('1: Missing Compulsory Field')
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows a requesting client that has recently logged on to
        ask this client for any messages that were intended for the requesting
        client when they were offline. This client will then use the requesting 
        client’s /receiveMessage and /receiveFile APIs to pass on any necessary
        messages. This allows re-use of the existing push APIs, but allows the
        requesting client to control when that pushing occurs.
    """
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
                    file = open('static/downloads/' +
                                filname.encode("ascii"), "rb")
                    attachments = base64.b64encode(file.read())
                    file.close()
                    for peer in logserv.peerList:
                        if message['destination'] == peer['username']:
                            stuff = {'sender': message['sender'], 'destination': message['destination'], 'file': attachments,
                                     'content_type': content_type, 'filename': filname, 'stamp': message['stamp'], 'encryption': 0, 'hash': '', 'hashing': 0}
                            payload = json.dumps(stuff)
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                                peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req, timeout=2).read()
                            db.updateMessageStatus(message, 'DELIVERED')
                else:
                    data = message
                    for peer in logserv.peerList:
                        if message['destination'] == peer['username']:
                            payload = json.dumps(data)
                            try:
                                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                                    peer['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                                response = urllib2.urlopen(
                                    req, timeout=2).read()
                                db.updateMessageStatus(message, 'DELIVERED')
                            except:
                                pass
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to request information about
        the current status of the user operating this client. The valid values
        to be returned are {“Online”, “Idle”, “Away”, “Do Not Disturb”, “Offline”}.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getStatus(self):
        if access_control.access_control():
            data = cherrypy.request.json
            for user in logserv.listLoggedInUsers:
                if user['username'] == data['profile_username']:
                    return {'status': user['status']}
            return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to send this client an event
        invitation. A single event, its metadata, and any control arguments
        should be in a dictionary and then JSON encoded. All events sent and
        received should be stored locally.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveEvent(self):
        if access_control.access_control():
            message = cherrypy.request.json
            for peer in logserv.peerList:
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

    """
        This should be called by a receiving client when the
        receiving user wishes to inform the sending user about
        their attendance.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def acknowledgeEvent(self):
        if access_control.access_control():
            message = cherrypy.request.json
            try:
                db.updateEventStatus(
                    message['attendance'], message['sender'], message['event_name'], int(message['start_time']))
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            except:
                return ('1: Missing Compulsory Field')
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        Identical output as server /getList, maintaining
        the plaintext output. Essentially provides the current
        user list maintained by this client.
    """
    @cherrypy.expose
    def getList(self, username, json_format=0):
        if access_control.access_control():
            if int(json_format) == 1:
                peerlist = {str(k): v for k, v in enumerate(logserv.peerList)}
                return json.dumps(peerlist)
            else:
                resp = '0: '
                for peer in logserv.peerList:
                    resp = resp + peer['username'] + ',' + peer['location'] + ',' + peer['ip'] + \
                        ',' + peer['port'] + ',' + peer['lastLogin'] + \
                        ',' + peer['publicKey'] + ','
                return resp
        else:
            return ("11: Blacklisted or Rate Limited")

    """
        This API allows another client to add themselves to the
        local user list on this client. Input is expected to be JSON.
    """
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def report(self):
        if access_control.access_control():
            message = cherrypy.request.json
            hashed = SHA512.new(data['passphrase']).hexdigest()
            if message['signature'] == Ciphers.RSA1024Cipher.encryptValue(hashed, db.getUserProfile(message['username'])[0]['publicKey']):
                return ('0: <Action was successful>')
        else:
            return ("11: Blacklisted or Rate Limited")
