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


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


class logserv():
    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(32)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')

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

    def reportAPICall(self):
        try:
            req = urllib2.Request(centralServer + 'report?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&ip=' + self.encrypt(
                self.ip) + '&port=' + self.encrypt(self.port) + '&location=' + self.encrypt(self.location) + '&pubkey=' + self.encrypt(self.pubkey) + '&enc=1')
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

    def reporterTimer(self):
        starttime = time.time()
        while not self.Kill:
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
            logserv.reportAPICall(self)
        thread.exit()

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

    @staticmethod
    def logoffEveryone(listLogInUsers):
        for user in listLogInUsers:
            req = urllib2.Request(centralServer + 'logoff?username=' + self.encrypt(
                user['username']) + '&password=' + self.encrypt(user['hashed']) + '&enc=1')
            response = urllib2.urlopen(req, timeout=2).read()

    def logoffAPICall(self):
        try:
            if self.online:
                req = urllib2.Request(centralServer + 'logoff?username=' + self.encrypt(
                    self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1')
                response = urllib2.urlopen(req, timeout=2).read()
                print("Response is: " + str(response))
                if '0, ' in str(response):
                    self.status = False
                    self.Kill = True
                else:
                    self.status = True
        except:
            pass

    def getPeerList(self):
        starttime = time.time()
        while True:
            try:
                if self.online:
                    req = urllib2.Request(centralServer + 'getList?username=' + self.encrypt(
                        self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1&json=' + self.encrypt('1'))
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

    def peerListThread(self):
        thread.start_new_thread(logserv.getPeerList, (self, ))

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

    def retrieveMessages(self):
        for peer in peerList:
            data = {'requestor': self.username}
            payload = json.dumps(data)
            try:
                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(
                    peer['port']) + '/retrieveMessages', payload, {'Content-Type': 'application/json'})
                response = urllib2.urlopen(req).read()
            except:
                pass
        thread.exit()

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
    
    def daemonQueuer(self):
        time.sleep(15.0)
        thread.start_new_thread(logserv.getProfile, (self, ))
        thread.start_new_thread(logserv.retrieveMessages, (self, ))
        thread.start_new_thread(logserv.getPeerStatus, (self, ))

    def daemonInit(self):
        thread.start_new_thread(logserv.daemonQueuer, (self, ))

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
        self.bs = 16
        self.currentEvent = None
        self.key = '150ecd12d550d05ad83f18328e536f53'
        self.rsakey = Ciphers.RSA1024Cipher.generatekeys()
        self.pubkey = binascii.hexlify(
            self.rsakey.publickey().exportKey('DER'))
