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
from cherrypy.lib.static import serve_fileobj

def get_formated_peer_list():
    sidebar = ''
    for peer in db.getPeerList() :
        name = peer['username']
        if peer['fullname'] != None:
            name = peer['fullname']
        lastLogin = time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
        if int(peer['lastLogin'] or 0) + 86400 > int(time.time()):
            lastLogin = time.strftime("%H:%M:%S", time.localtime(float(peer['lastLogin'] or 0)))
        else:
            lastLogin = time.strftime("%a, %d %b %Y", time.localtime(float(peer['lastLogin'] or 0)))
        if peer['lastLogin'] == None:
            lastLogin = 'NEVER'
        elif int(peer['lastLogin']) + 300 > int(time.time()):
            name = name + u' 🔵'
        else:
            name = name + u' 🔴'
        pict = peer['picture']
        if peer['picture'] == None:
            pict = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"
        sidebar = sidebar + """<div class="media conversation"><a class="pull-left" href="chat?userID='""" + peer['username'] + "\'" + """"><img class="media-object" data-src="holder.js/64x64" alt="profilepic" style="width: 50px; height: 50px;" src=\"""" + pict + """"></a><div class="media-body"><h5 class="media-heading">""" + name + ' </h5><small>Last Online: ' + lastLogin + '</small></div></div>'
    return unicode(sidebar)

def sizeb64(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)

def get_formated_message_list(userID):
    messageHistory = """</div><div class="message-wrap col-lg-8"><div class="msg-wrap" id="your_div">"""
    messageList = db.readOutMessages(userID, pls.username)
    contact = db.getUserProfile(userID)[0]
    userdata = db.getUserProfile(pls.username)[0]
    for row in messageList :
        name = userdata['fullname']
        pict = userdata['picture']
        row['message'] = string.replace(row['message'], "''", "'")
        text = markdown.markdown(row['message'])
        if row['sender'] == userdata['username'] :
            pass
        else :
            name = contact['username']
            if contact['fullname'] != None:
                name = contact['fullname']
            pict = contact['picture']
            if contact['picture'] == None:
                pict = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"
        messageHistory = messageHistory + """<div class="media msg"><a class="pull-left" href="#"><img class="media-object" data-src="holder.js/64x64" alt="profilepic" style="width: 32px; height: 32px;" src=\"""" + pict + """"></a><div class="media-body"><small class="pull-right time"><i class="fa fa-clock-o"></i>""" + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(float(row['stamp']))) + "<br>" + row['status'] + """</small><h5 class="media-heading">""" + name + """</h5><small class="col-lg-10">""" + text + '</small></div></div>'
    messageHistory = unicode(messageHistory)

    if len(messageHistory) < 74 :
        messageHistory = messageHistory + "You have no chat history with this user, start chatting below ..."
    
    return messageHistory

currentChat = ''
header = ''
footerb = ''
footer = ''
pls = None

def stop():
    if pls != None:
        global pls
        protocol_login_server.protocol_login_server.logoff_API_call(pls)
        del pls

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
    def logout(self):
        global pls
        protocol_login_server.protocol_login_server.logoff_API_call(pls)
        del pls
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def login_check(self, username, password):
        try:
            hashed = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
            global pls
            pls = protocol_login_server.protocol_login_server(username, hashed)
            protocol_login_server.protocol_login_server.reporter_thread(pls)
            protocol_login_server.protocol_login_server.profile_thread(pls)
            if pls.status:
                raise cherrypy.HTTPRedirect("home")
        except:
            pass
        raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def home(self):
        if pls == None:
            raise cherrypy.HTTPRedirect("login.html")
        if pls.status:
            sidebar = get_formated_peer_list()
            sidebar = sidebar + "</div>"
            return header + sidebar + footerb
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def editProfile(self):
        if pls == None:
            raise cherrypy.HTTPRedirect("login.html")
        if pls.status:
            head = ''
            foot = ''
            with open ("editprofile_header.html", "r") as myfile : 
                head = myfile.read()
            with open ("editprofile_footer.html", "r") as myfile :
                foot = myfile.read()
            payload = db.getUserData(pls.username)
            if payload == []:
                payload = [{'picture': '', 'description': '', 'location': '', 'position': '', 'fullname': ''}]
            sidebar = pls.username + "</div><div class='login-form-1'><form accept-charset='UTF-8' action='/updateProfile' id='updateProfile'  class='text-left' method='post' enctype='multipart/form-data'><div class='login-form-main-message'></div><div class='main-login-form'><div class='login-group'>"
            for thing in payload[0]:
                if thing == 'username':
                    continue
                sidebar = sidebar + "<div class='form-group'><label for='" + thing + "' class='sr-only'>" + thing + "</label><input type='text' class='form-control' id='" + thing + "' name='" + thing + "' placeholder='" + thing + "' value='" + payload[0][thing] + "'></div>"
            return head + sidebar.encode("ascii") + foot
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def updateProfile(self, picture, description, location, position, fullname):
        db.updateUserData(pls.username, picture, description, location, position, fullname)
        raise cherrypy.HTTPRedirect("home")

    @cherrypy.expose
    def chat(self, userID):
        if pls == None:
            raise cherrypy.HTTPRedirect("login.html")
        if pls == None or pls.status:
            userID = userID.replace("\'", "")
            global currentChat
            currentChat = userID
            sidebar = get_formated_peer_list()
            messageHistory = unicode(get_formated_message_list(userID))
            return header + sidebar + messageHistory + footer
        else:
            raise cherrypy.HTTPRedirect("login.html")
        
    @cherrypy.expose
    def sendMessage(self, message, attachments):
        print(cherrypy.url())
        if pls == None:
            raise cherrypy.HTTPRedirect("login.html")
        if pls.status:
            data = {'sender': pls.username, 'destination': currentChat, 'message': message, 'markdown': '1', 'stamp': unicode(int(time.time())), 'encoding': '2', 'encryption': '0', 'hashing': '0', 'hash': '', 'markdown': '0'}
            for peer in pls.peerList:
                if currentChat == peer[1]['username']:
                    payload = json.dumps(data)
                    if currentChat == pls.username:
                        peer[1]['ip'] = 'localhost'
                    elif peer[1]['location'] == '2':
                        pass
                    elif peer[1]['location'] == pls.location:
                        pass
                    else:
                        raise cherrypy.HTTPRedirect("chat?userID=\'" + currentChat + "\'")
                    if data['message'] != "":
                        req = urllib2.Request('http://' + unicode(peer[1]['ip']) + ':' + unicode(peer[1]['port']) + '/receiveMessage', payload, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req).read()
                        response = '0: '
                        if '0: ' in unicode(response):
                            data['status'] = 'DELIVERED'
                        else:
                            data['status'] = 'OUTBOX'
                    try :
                        filname = attachments.filename
                        content_type = mimetypes.guess_type(filname)[0]
                        attachments = base64.b64encode(attachments.file.read())
                        stuff = {'sender': pls.username, 'destination': currentChat, 'file': attachments, 'content_type': content_type,'filename': filname, 'stamp': unicode(int(time.time())), 'encryption': '0', 'hash': ''}
                        payload = json.dumps(stuff)
                        req = urllib2.Request('http://' + unicode(peer[1]['ip']) + ':' + unicode(peer[1]['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                        response = urllib2.urlopen(req).read()
                        if '0: ' in unicode(response):
                            data['status'] = 'DELIVERED'
                        else:
                            data['status'] = 'OUTBOX'
                        file = open ('static/downloads/' + filname.encode("ascii"), "wb")
                        file.write(base64.b64decode(attachments))
                        file.close()
                        text = '<a href=\"downloads\\' + filname + '\" download>' + filname + '</a>'
                        if 'image/' in content_type:
                            text = '<img src=\"downloads\\' + filname + '\" alt=\"' + filname + '\" width="320">'
                        if 'audio/' in content_type:
                            text = '<audio controls><source src=\"downloads\\' + filname + '\" type=\"' + content_type + '\"></audio>'
                        if 'video/' in content_type:
                            text = '<video width="320" height="240" controls><source src=\"downloads\\' + filname + '\" type=\"' + content_type + '\"></video>'
                        data['message'] = data['message'] + text
                    except:
                        pass
            db.addNewMessage(data)
            raise cherrypy.HTTPRedirect("chat?userID=\'" + currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        return file("404.html")

    @cherrypy.expose
    def listAPI(self):
        return ('Available APIs: /listAPI /ping /recieveMessage [sender] [destination] [message] [stamp(opt)] [markdown] [encoding(opt)] [encryption(opt)] [hashing(opt)] [hash(opt)] /acknowledge [sender] [stamp] [hash] [hashing] /getPublicKey [sender] /handshake [message] [encryption] /getProfile [sender] /recieveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption] [hash]' + 
         '<br> Encoding: 0, 2' + 
         '<br> Encryption: 0, 1, 2' + 
         '<br> Hashing: ')
        
    @cherrypy.expose
    def ping(self):
        return ('0')
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json
        data = messageProcess.unprocess(data, pls)
        if isinstance(data, basestring):
            return data
        if data['destination'] == 'pls.username':
            data['status'] = 'DELIVERED'
        else:
            data['status'] = 'SENDING'
        if db.addNewMessage(data):
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ('1: Missing Compulsory Field')
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def acknowledge(self):
        data = cherrypy.request.json
        if db.lookUpMessage(data):
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return (u'7: Hash does not match')
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getPublicKey(self):
        sender = cherrypy.request.json
        return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'pubkey': pls.pubkey}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handshake(self):
        data = cherrypy.request.json
        if data['encryption'] == '1':
            data['message'] = Ciphers.XORCipher.decrypt(data['message'])
        if data['encryption'] == '2':
            data['message'] = Ciphers.AESCipher.decrypt(data['message'])
        if date['encryption'] == '3':
            return {'error': u'9: Encryption Standard Not Supported', 'message': date['message']}
        return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'message': data['message']}
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
        sender = cherrypy.request.json
        data = db.getUserData(sender['profile_username'])
        data[0]['encoding'] = '2'
        data[0]['encryption'] = '0'
        return data[0]  
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        data = cherrypy.request.json
        if sizeb64(data['file']) > 5242880:
            return (u'6, உங்கள் கோப்பு எல்லைக்குள் இல்லை')
        file = open ('static/downloads/' + data['filename'].encode("ascii"), "wb")
        file.write(base64.b64decode(data['file']))
        file.close()
        content_type = mimetypes.guess_type(data['filename'])[0]
        text = '<a href=\"downloads\\' + data['filename'] + '\" download>' + data['filename'] + '</a>'
        if 'image/' in content_type:
            text = '<img src=\"downloads\\' + data['filename'] + '\" alt=\"' + data['filename'] + '\" width="320">'
        if 'audio/' in content_type:
            text = '<audio controls><source src=\"downloads\\' + data['filename'] + '\" type=\"' + content_type + '\"></audio>'
        if 'video/' in content_type:
            text = '<video width="320" height="240" controls><source src=\"downloads\\' + data['filename'] + '\" type=\"' + content_type + '\"></video>'
        payload = {'sender': data['sender'], 'destination': data['destination'], 'message': text, 'stamp': data['stamp'], 'encoding': '2', 'encryption': '2', 'hashing': '0', 'hash': '', 'status': 'delivered', 'markdown': '0'}
        db.addNewMessage(payload)
        return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
    
    #TODO: add retrieveMessages function

    @cherrypy.expose
    def getList(self, username, encryption=0, json=0):
        peerList = []
        for peer in db.getPeerList():
            if int(peer['lastLogin'] or 0) + 300 > time.time():
                peerList.append(peer)  
        for peer in peerList:
            del peer['picture']
            del peer['description']
            del peer['position']
            del peer['fullname']
            if int(encryption) == 1:
                for thing in peer:
                    thing = Ciphers.XORCipher.decrypt(thing)
            if int(encryption) == 2:
                for thing in peer:
                    thing = Ciphers.AESCipher.decrypt(thing)
            if int(encryption) == 3:
                return (u'9: Encryption Standard Not Supported')
        if json == 1:
            return json.dumps(peerList)
        resp = '0: '
        for peer in peerList:
            resp = resp + peer['username'] + ',' + peer['location'] + ',' + peer['ip'] + ',' + peer['port'] + ',' + peer['lastLogin'] + ','
        return resp
        
    WEB_ROOT = os.getcwd() + '\\static'

    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 10008,
                            'engine.autoreload.on': True,
                            'tools.encode.on': True,
                            'tools.encode.encoding': 'utf-8',
                            'tools.staticdir.on' : True,
                            'tools.staticdir.dir' : WEB_ROOT,
                            'tools.staticdir.index' : 'index.html'})

cherrypy.engine.subscribe('stop', stop)
cherrypy.quickstart(MainClass())
