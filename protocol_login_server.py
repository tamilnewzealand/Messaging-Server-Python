import urllib2
import urllib
import json
import time
import thread
import socket
import db
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import binascii
import Ciphers

centralServer = 'https://cs302.pythonanywhere.com/'

class protocol_login_server():
    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(32)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return urllib.quote(binascii.hexlify(iv + cipher.encrypt(raw)), safe='')
    
    def report_API_call(self):
        print("Login starting..")
        data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
        ip =  data["ip"]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = s.getsockname()[0]
        s.close()
        port = '10008'
        if '130.216' in ip:
            self.location = '0'
            ip = localip
        elif '172.23' in localip:
            self.location = '1'
            ip = localip
        elif '172.24' in localip:
            self.location = '1'
            ip = localip
        else:
            self.location = '2'
        try:
            #req = urllib2.Request(centralServer + 'report?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&ip=' + self.encrypt(ip) + '&port=' + self.encrypt(port) + '&location=' + self.encrypt(self.location) + '&enc=1')
            req = urllib2.Request(centralServer + 'report?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&ip=' + self.encrypt(ip) + '&port=' + self.encrypt(port) + '&location=' + self.encrypt(self.location) + '&pubkey=' + self.encrypt(self.pubkey) + '&enc=1')
            response = urllib2.urlopen(req).read()
        except:
            if db.checkUserHash(self.username, self.hashed):
                response = u'0, Server offline but user verified'
            else:
                response = u'2, Unauthenticated User'
        print("Response is: " + str(response))
        if '0, ' in str(response):
            self.status = True
            db.updateUserHash(self.username, self.hashed)
        else:
            self.status = False

    def logoff_API_call(self):
        try:
            req = urllib2.Request(centralServer + 'logoff?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1')
            response = urllib2.urlopen(req).read()
            print("Response is: " + str(response))
            if '0, ' in str(response):
                self.status = False
            else:
                self.status = True
        except:
            pass

    def getList_API_call(self):
        try:
            req = urllib2.Request(centralServer + 'getList?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1&json=' + self.encrypt('1'))
            response = urllib2.urlopen(req).read()
            selfpeerList = json.loads(response).items()
            for peer in self.peerList:
                if 'publicKey' not in peer[1]:
                    peer[1]['publicKey'] = ''
                db.updateUserProfileB(peer[1]['username'], peer[1]['ip'], peer[1]['location'], peer[1]['lastLogin'], peer[1]['port'], peer[1]['publicKey'])
        except:
            pass
    
    def reporter_thread(self):
        protocol_login_server.report_API_call(self)
        protocol_login_server.getList_API_call(self)
        thread.start_new_thread(protocol_login_server.reporter_timer, (self, ))

    def reporter_timer(self):
        starttime=time.time()
        while True:
            protocol_login_server.getList_API_call(self)
            protocol_login_server.report_API_call(self)
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    def profile_thread(self):
        thread.start_new_thread(protocol_login_server.profile_timer, (self, ))

    def profile_timer(self):
        starttime=time.time()
        while True:
            data = None
            for peer in self.peerList:
                if self.currentChat == self.username:
                        peer[1]['ip'] = 'localhost'
                elif peer[1]['location'] == '2':
                    pass
                elif peer[1]['location'] == self.location:
                    pass
                else:
                    continue
                try:
                    payload = {'profile_username': peer[1]['username']}
                    payload = json.dumps(payload)
                    req = urllib2.Request('http://' + unicode(peer[1]['ip']) + ':' + unicode(peer[1]['port']) + '/getProfile', payload, {'Content-Type': 'application/json'})                  
                    data = json.loads(urllib2.urlopen(req).read())
                except:
                    pass
                db.updateUserProfileA(data)
            time.sleep(300.0 - ((time.time() - starttime) % 300.0))
    
    def __init__(self, username, hashed):
        self.username = username
        self.hashed = hashed
        self.currrentChat = ''
        self.status = False
        self.peerList = None
        self.location = '2'
        self.bs = 16
        self.key = '150ecd12d550d05ad83f18328e536f53'
        self.rsakey = Ciphers.RSA1024Cipher.generatekeys()
        self.pubkey = binascii.hexlify(self.rsakey.publickey().exportKey('DER'))