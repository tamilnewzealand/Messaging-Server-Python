# coding=utf8

import json
import urllib2
import cherrypy
import db
import protocol_login_server
import time
import hashlib
from cherrypy.lib.static import serve_fileobj

def get_formated_peer_list():
    sidebar = ''
    for peer in pls.peerList :
        sidebar = sidebar + """<div class="media conversation"><a class="pull-left" href="chat?userID='""" + peer[1]['username'] + "\'" + """">
        <img class="media-object" data-src="holder.js/64x64" alt="64x64" style="width: 50px; height: 50px;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"></a>
        <div class="media-body"><h5 class="media-heading">""" + peer[1]['username'] + ' </h5><small>Last Online: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(float(peer[1]['lastLogin']))) + '</small></div></div>'
    return str(sidebar)

def get_formated_message_list(userID):
    messageHistory = """</div><div class="message-wrap col-lg-8"><div class="msg-wrap">"""
    messageList = db.readOutMessages(userID, pls.username)
    for row in messageList :
        name = pls.username
        if row['sender'] == pls.username :
            pass
        else :
            name = userID
        messageHistory = messageHistory + """<div class="media msg">
            <a class="pull-left" href="#"><img class="media-object" data-src="holder.js/64x64" alt="64x64" style="width: 32px; height: 32px;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC">
            </a><div class="media-body"><small class="pull-right time"><i class="fa fa-clock-o"></i>""" + row['stamp'] + "<br>" + row['status'] + """</small>
            <h5 class="media-heading">""" + name + """</h5><small class="col-lg-10">""" + row['message'] + '</small></div></div>'
    messageHistory = str(messageHistory)

    if len(messageHistory) < 74 :
        messageHistory = messageHistory + "You have no chat history with this user, start chatting below ..."
    
    return messageHistory

currentChat = ''
header = ''
footerb = ''
footer = ''
pls = None
with open ("chat_header.html", "r") as myfile : 
    header = myfile.read()
with open ("chat_footerb.html", "r") as myfile :
    footerb = myfile.read()
with open ("chat_footer.html", "r") as myfile :
    footer = myfile.read()

class MainClass(object):

    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',}
    @cherrypy.expose
    def index(self):
        return file("index.html")
    
    @cherrypy.expose
    def login(self):
        return file("login.html")
    
    @cherrypy.expose
    def register(self):
        return file("register.html")
    
    @cherrypy.expose
    def logout(self):
        global pls
        protocol_login_server.protocol_login_server.logoff_API_call(pls)
        del pls
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def login_check(self, username, password):
        hashed = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
        global pls
        pls = protocol_login_server.protocol_login_server(username, hashed)
        protocol_login_server.protocol_login_server.reporter_thread(pls)
        if pls.status:
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def home(self):
        if pls == None:
            raise cherrypy.HTTPRedirect("login")
        if pls.status:
            sidebar = get_formated_peer_list()
            sidebar = sidebar + "</div>"
            return header + sidebar + footerb
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def chat(self, userID):
        if pls == None:
            raise cherrypy.HTTPRedirect("login")
        if pls == None or pls.status:
            userID = userID.replace("\'", "")
            global currentChat
            currentChat = userID
            sidebar = get_formated_peer_list()
            messageHistory = get_formated_message_list(userID)
            return header + sidebar + messageHistory + footer
        else:
            raise cherrypy.HTTPRedirect("login")
        
    @cherrypy.expose
    def sendMessage(self, message, attachments):
        print(cherrypy.url())
        if pls == None:
            raise cherrypy.HTTPRedirect("login")
        if pls.status:
            data = {'sender': pls.username, 'destination': currentChat, 'message': message, 'stamp': int(time.time()), 'encoding': '0', 'encryption': '0', 'hashing': '0', 'hash': ''}
            for peer in pls.peerList:
                if currentChat == peer[1]['username']:
                    payload = json.dumps(data)
                    req = urllib2.Request('http://' + str(peer[1]['ip']) + ':' + str(peer[1]['port']) +  '/receiveMessage', payload, {'Content-Type': 'application/json'})
                    response = urllib2.urlopen(req).read()
                    if '0, ' in str(response):
                        data['status'] = 'DELIVERED'
                    else:
                        data['status'] = 'OUTBOX'
            db.addNewMessage(data)
            raise cherrypy.HTTPRedirect("chat?userID=\'" + currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def download(self, userID, realUsersName, message):
        if pls == None:
            raise cherrypy.HTTPRedirect("login")
        if pls.status:
            (messageHistory, messageList) = get_formated_message_list(userID, realUsersName)
            attachment = ''
            filname = ''
            for x in messageList:
                if message == x.message:
                    attachment = x.attachment
                    filname = x.attachment_name
            file = open ('uploads/' + filname, "wb")
            file.write(base64.b64decode(attachment))
            file.close()
            RETURN_FILE = open('uploads/' + filname, 'rb')
            return serve_fileobj(RETURN_FILE, "application/x-download", "attachment", filname)
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        return file("404.html")

    @cherrypy.expose
    def listAPI(self):
        return ('Available APIs: /listAPI /ping /recieveMessage' + 
         '<br> Encoding: ' + 
         '<br> Encryption: ' + 
         '<br> Hashing: ')
        
    @cherrypy.expose
    def ping(self):
        return ('0')
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json
        if data['destination'] == 'pls.username':
            data['staus'] = 'DELIVERED'
        else:
            data['status'] = 'SENDING'
        db.addNewMessage(data)
        return (u'0, உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
    
    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 5050,
                            'engine.autoreload.on': True,
                            'tools.encode.on': True,
                            'tools.encode.encoding': 'utf-8',})

cherrypy.quickstart(MainClass())
