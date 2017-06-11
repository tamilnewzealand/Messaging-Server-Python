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

import urllib2
import urllib
import json
import time
import thread
import socket
import db
import messageProcess
import tfa
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512
import binascii
import Ciphers
import random
import string

centralServer = 'https://cs302.pythonanywhere.com/'
peerList = None
listLoggedInUsers = []


"""
    Generates a lowercase string of characters of a given length.
"""


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


"""
    Pads with spaces for rounding to the nearest block.
"""


def _pad(s):
    return s + (16 - len(s) % 16) * chr(32)


"""
    Encrypts the data using the hard coded AES key from
    the login server protocol.
"""


def encrypt(raw):
    raw = _pad(raw)
    iv = Random.new().read(16)
    cipher = AES.new('150ecd12d550d05ad83f18328e536f53', AES.MODE_CBC, iv)
    return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')


class logserv():

    """
        Gets external and internal IP and inteligentally
        figures out current location and sets the appropriate
        variables.
    """

    def getIP(self):
        data = json.loads(urllib2.urlopen("http://ip.jsontest.com/").read())
        self.ip = data["ip"]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = s.getsockname()[0]
        s.close()
        if '130.216' in self.ip:
            self.location = '0'
            self.ip = localip
        elif '172.23' in localip:
            self.location = '1'
            self.ip = localip
        elif '172.24' in localip:
            self.location = '1'
            self.ip = localip
        else:
            self.location = '2'

    """
        Trys to make a report API call on the login server.
        If this fails, then it directly reports to all peers
        on the currently maintained local peer list.
    """

    def reportAPICall(self):
        try:
            req = urllib2.Request(centralServer + 'report?username=' + encrypt(self.username) + '&password=' + encrypt(self.hashed) + '&ip=' + encrypt(
                self.ip) + '&port=' + encrypt(self.port) + '&location=' + encrypt(self.location) + '&pubkey=' + encrypt(self.pubkey) + '&enc=1')
            response = urllib2.urlopen(req, timeout=2).read()
            self.online = True
        except:
            if db.checkUserHash(self.username, self.hashed):
                for peer in peerList:
                    passphrase = randomword(1024)
                    hashed = SHA512.new(passphrase).hexdigest()
                    signature = self.rsakey.encrypt(hashed)
                    data = {'username': self.username, 'passphrase': passphrase, 'signature': signature,
                            'location': self.location, 'ip': self.ip, 'port': self.port}
                    payload = json.dumps(data)
                    try:
                        req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                            peer['port']) + '/report', payload, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req, timeout=2).read()
                    except:
                        pass
                response = u'0, Server offline but user verified'
                self.online = False
            else:
                response = u'2, Unauthenticated User'
        if '0, ' in str(response):
            self.status = True
        else:
            self.status = False

    """
        Timer method calls the above function every
        60 seconds. If the Kill flag has been set then it
        kills the current reporting thread.
    """

    def reporterTimer(self):
        starttime = time.time()
        while True:
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
            if self.Kill:
                thread.exit()
            else:
                logserv.reportAPICall(self)
        thread.exit()

    """
        Makes the first report API call then starts the
        reporterTimer in its own thread.
    """

    def reporterThread(self):
        logserv.getIP(self)
        logserv.reportAPICall(self)
        if self.status:
            db.updateUserHash(self.username, self.hashed)
            if db.getUserData(self.username)[0]['tfa'] == 'on':
                self.status = False
                self.tfa = True
                self.seccode = tfa.tfainit(self.username)
        thread.start_new_thread(logserv.reporterTimer, (self, ))

    """
        Logs off everyone in the currently logged into this
        node list of users. This is in preparation of a node
        being shut down.
    """
    @staticmethod
    def logoffEveryone(listLogInUsers):
        for user in listLogInUsers:
            req = urllib2.Request(centralServer + 'logoff?username=' + encrypt(
                user['username']) + '&password=' + encrypt(user['hashed']) + '&enc=1')
            response = urllib2.urlopen(req, timeout=2).read()

    """
        Logs of the current user by making a logoff
        API call to the server. Also sets the flag 
        to kill the reporter thread for this user.
        This is called when a user presses the Logout
        button from their browser.
    """

    def logoffAPICall(self):
        try:
            if self.online:
                req = urllib2.Request(centralServer + 'logoff?username=' + encrypt(
                    self.username) + '&password=' + encrypt(self.hashed) + '&enc=1')
                response = urllib2.urlopen(req, timeout=2).read()
                print("Response is: " + str(response))
                if '0, ' in str(response):
                    self.status = False
                    self.Kill = True
                else:
                    self.status = True
        except:
            pass

    """
        Gets the current peer list from the server. In the
        case of server outage, a request for a peer list is
        made to every peer in the local list and these lists
        are merged into the locally maintained peer list.
    """

    def getPeerList(self):
        starttime = time.time()
        while True:
            try:
                if self.online:
                    req = urllib2.Request(centralServer + 'getList?username=' + encrypt(
                        self.username) + '&password=' + encrypt(self.hashed) + '&enc=1&json=' + encrypt('1'))
                    response = urllib2.urlopen(req, timeout=2).read()
                    global peerList
                    peerList = json.loads(response).values()
                    for peer in peerList:
                        if 'publicKey' not in peer:
                            peer['publicKey'] = ''
                        db.updateUserProfileB(
                            peer['username'], peer['ip'], peer['location'], peer['lastLogin'], peer['port'], peer['publicKey'])
                else:
                    newPeerList = peerList
                    for peer in peerList:
                        if peer['ip'] != self.ip:
                            req = urllib2.Request(
                                centralServer + 'getList?username=' + self.username + '&json_format=1')
                            newPeerList.extend(json.loads(
                                urllib2.urlopen(req, timeout=2).read()).values())
                    somelist = [x for x in newPeerList if (
                        int(x['stamp']) + 120 > int(time.time()))]
                    global peerList
                    peerList = [dict(tupleized) for tupleized in set(
                        tuple(item.items()) for item in somelist)]
            except:
                pass
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    """
        Starts the getPeerList method in a seperate thread.
    """

    def peerListThread(self):
        thread.start_new_thread(logserv.getPeerList, (self, ))

    """
        Loops through all the peers in the local peer list and
        makes a getProfile API call on everyone of them. Exludes
        calls to locations that are unreachable from the current 
        location and to users on this node. This data is stored in
        the database. Is timed to run once every five minutes.
    """

    def getProfile(self):
        starttime = time.time()
        while True:
            data = None
            for peer in peerList:
                if peer['ip'] == self.ip:
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == self.location:
                    pass
                else:
                    continue
                try:
                    payload = {
                        'profile_username': peer['username'], 'sender': listLoggedInUsers[0]['username']}
                    payload = json.dumps(payload)
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                        peer['port']) + '/getProfile', payload, {'Content-Type': 'application/json'})
                    data = json.loads(urllib2.urlopen(req, timeout=2).read())
                    data['username'] = peer['username']
                    messageProcess.unprocessProf(data, listLoggedInUsers[0])
                    db.updateUserProfileA(data)
                except:
                    pass
            time.sleep(300.0 - ((time.time() - starttime) % 300.0))

    """
        Calls a retrieveMessage API call on everyone in
        the local peer list. This method is executed once
        at startup in its own thread. Only runs once at 
        startup and then kills the thread.
    """

    def retrieveMessages(self):
        for peer in peerList:
            if peer['ip'] == self.ip:
                continue
            elif peer['location'] == '2':
                pass
            elif peer['location'] == self.location:
                pass
            else:
                continue
            data = {'requestor': self.username}
            payload = json.dumps(data)
            try:
                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                    peer['port']) + '/retrieveMessages', payload, {'Content-Type': 'application/json'})
                response = urllib2.urlopen(req).read()
            except:
                pass
        thread.exit()

    """
        Loops through all the peers in the local peer list and
        makes a getStatus API call on everyone of them. Exludes
        calls to locations that are unreachable from the current 
        location and to users on this node. This data is stored in
        the database. This is run every 30 seconds on a timer.
    """

    def getPeerStatus(self):
        starttime = time.time()
        while True:
            time.sleep(30.0 - ((time.time() - starttime) % 30.0))
            for peer in peerList:
                if peer['ip'] == self.ip:
                    db.updateUserStatus(peer['username'], 'Online')
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == self.location:
                    pass
                else:
                    continue
                try:
                    payload = {'profile_username': peer['username']}
                    payload = json.dumps(payload)
                    req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                        peer['port']) + '/getStatus', payload, {'Content-Type': 'application/json'})
                    data = json.loads(urllib2.urlopen(req, timeout=1).read())
                    db.updateUserStatus(peer['username'], data['status'])
                except:
                    db.updateUserStatus(peer['username'], 'Offline')

    """
        Waits for 15 seconds after startup and then 
        starts all the above threads as background threads.
    """

    def daemonQueuer(self):
        time.sleep(15.0)
        thread.start_new_thread(logserv.getProfile, (self, ))
        thread.start_new_thread(logserv.retrieveMessages, (self, ))
        thread.start_new_thread(logserv.getPeerStatus, (self, ))
        thread.exit()

    """
        Starts the above daemonQueuer in its own thread.
    """

    def daemonInit(self):
        thread.start_new_thread(logserv.daemonQueuer, (self, ))

    """
        Initializes the logserv class for the user that
        is logging in. Generates a new RSA 1024
        public-private key pair for this session.
    """

    def __init__(self, username, hashed):
        self.username = username
        self.hashed = hashed
        self.port = '10008'
        self.Kill = False
        self.ip = ''
        self.currrentChat = ''
        self.status = False
        self.tfa = False
        self.seccode = ''
        self.online = True
        self.location = '2'
        self.currentEvent = None
        self.rsakey = Ciphers.RSA1024Cipher.generatekeys()
        self.pubkey = binascii.hexlify(
            self.rsakey.publickey().exportKey('DER'))
