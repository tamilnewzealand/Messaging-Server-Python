import urllib2
import urllib
import json
import time
import thread
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
        port = '5050'
        location = '2'
        req = urllib2.Request(centralServer + 'report?username=' + self.encrypt(self.username) + '&password=' + self.encrypt(self.hashed) + '&ip=' + self.encrypt(ip) + '&port=' + self.encrypt(port) + '&location=' + self.encrypt(location) + '&enc=1')
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
    
    def reporter_thread(self):
        protocol_login_server.report_API_call(self)
        protocol_login_server.getList_API_call(self)
        thread.start_new_thread(protocol_login_server.reporter_timer, (self, ))

    def reporter_timer(self):
        print('thread started')
        starttime=time.time()
        while True:
            protocol_login_server.getList_API_call(self)
            protocol_login_server.report_API_call(self)
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    
    def __init__(self, username, hashed):
        self.username = username
        self.hashed = hashed
        self.status = False
        self.peerList = None
        self.bs = 16
        self.key = '150ecd12d550d05ad83f18328e536f53'