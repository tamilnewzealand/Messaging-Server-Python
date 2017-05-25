import urllib2
import urllib
import json
import time
import thread
import socket
import db
from Crypto import Random
from Crypto.Cipher import AES
import binascii

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
        localip = socket.gethostbyname(socket.gethostname())
        if '130.216' in ip:
            ip = localip
            port = '10008'
            if '172.23' in ip:
                self.location = '1'
            elif '172.24' in ip:
                self.location = '1'
            else:
                self.location = '0'
        else:
            port = '5050'
            self.location = '2'
        req = urllib2.Request(centralServer + 'report?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&ip=' + self.encrypt(ip) + '&port=' + self.encrypt(port) + '&location=' + self.encrypt(self.location) + '&enc=1')
        response = urllib2.urlopen(req).read()
        print("Response is: " + str(response))
        if '0, ' in str(response):
            self.status = True
        else:
            self.status = False

    def logoff_API_call(self):
        req = urllib2.Request(centralServer + 'logoff?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1')
        response = urllib2.urlopen(req).read()
        print("Response is: " + str(response))
        if '0, ' in str(response):
            self.status = False
        else:
            self.status = True

    def getList_API_call(self):
        req = urllib2.Request(centralServer + 'getList?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&enc=1&json=1')
        response = urllib2.urlopen(req).read()
        self.peerList = json.loads(response).items()
        for peer in self.peerList:
            db.updateUserProfileB(peer[1]['username'], peer[1]['ip'], peer[1]['location'], peer[1]['lastLogin'], peer[1]['port'])
    
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
                if peer[1]['username'] == 'ssit662':
                    data = """{"username": "ssit662", "picture": "https://s3.amazonaws.com/37assets/svn/1065-IMG_2529.jpg", "description": "Enquire for more information", "encoding": "2", "encryption": "0", "location": "Earth", "position": "Student", "fullname": "Sakayan Sitsabesan"}"""
                    data = json.loads(data)
                elif '192.168' in peer[1]['ip']:
                    data = None
                else:
                    try:
                        data = json.loads(urllib.urlopen('http://' + peer[1]['ip'] + ':' + peer[1]['port'] + "/getProfile?sender=" + self.username).read())                   
                    except:
                        pass
                db.updateUserProfileA(data)
            time.sleep(300.0 - ((time.time() - starttime) % 300.0))
    
    def __init__(self, username, hashed):
        self.username = username
        self.hashed = hashed
        self.status = False
        self.peerList = None
        self.location = '2'
        self.bs = 16
        self.key = '150ecd12d550d05ad83f18328e536f53'