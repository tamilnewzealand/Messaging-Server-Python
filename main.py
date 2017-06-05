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
import thread
import access_control
import Ciphers
from Crypto.Hash import SHA512
from cherrypy.lib.static import serve_fileobj

header = ''
footer = "</div><link rel='stylesheet' href='simplemde.min.css'><script src='simplemde.min.js'></script><script>new SimpleMDE({ element: document.getElementById('message'), spellChecker: false, });</script></body></html>"
with open ("chat_header.html", "r") as myfile : 
    header = myfile.read()
listLoggedInUsers = []
thread.start_new_thread(access_control.ac_timer, ('0', ))

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

def sendAcknowledge(data, ip):
    try:
        stuff = {'sender': data['sender'], 'stamp': data['stamp'], 'hashing': data['hashing'], 'hash': data['hash']}
        for peer in protocol_login_server.peerList:
            if data['sender'] == peer['username']:
                if peer['ip'] == ip:
                    db.updateMessageStatus(data, 'SEEN')
                    continue
                elif peer['location'] == '2':
                    pass
                elif peer['location'] == self.location:
                    pass
                else:
                    continue
                payload = json.dumps(stuff)
                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/acknowledge', payload, {'Content-Type': 'application/json'})
                response = urllib2.urlopen(req).read()
                db.updateMessageStatus(data, 'SEEN')
    except:
        pass

def get_formated_message_list(userID):
    messageHistory = """</div><div class="message-wrap col-lg-8"><div class="msg-wrap" id="your_div">"""
    messageList = db.readOutMessages(userID, cherrypy.session['userdata'].username)
    contact = db.getUserProfile(userID)[0]
    userdata = db.getUserProfile(cherrypy.session['userdata'].username)[0]
    for row in messageList :
        if row['status'] != 'SEEN':
            if row['sender'] == userID:
                sendAcknowledge(row, cherrypy.session['userdata'].ip)
        name = userdata['fullname']
        pict = userdata['picture']
        row['message'] = string.replace(row['message'], "''", "'")
        if int(row['markdown']) == 1:
            text = markdown.markdown(row['message'])
        else:
            text = row['message']
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
    messageHistory = messageHistory + "</div><div class='send-wrap '><textarea name='message' id='message' form='usrform' class='form-control send-message' rows='3' placeholder='Write a reply...'></textarea></div><div class='btn-panel'><form accept-charset='UTF-8' action='/sendMessage' id='usrform' method='post' enctype='multipart/form-data'><input type='file' class=' col-lg-6 btn    send-message-btn' name='attachments' maxlength=50><input type='submit' class=' col-lg-4 text-right btn send-message-btn pull-right' role='button' value='Send Message'/></form></div></div></div>"
    messageHistory = unicode(messageHistory)

    if len(messageHistory) < 74 :
        messageHistory = messageHistory + "You have no chat history with this user, start chatting below ..."
    
    return messageHistory

def stop():
    if cherrypy.session['userdata'] != None:
        protocol_login_server.protocol_login_server.logoff_API_call(cherrypy.session['userdata'])
        del cherrypy.session['userdata']
        global listLoggedInUsers
        del listLoggedInUsers

class MainClass(object):
    @cherrypy.expose
    def logout(self):
        if 'userdata' in cherrypy.session:
            protocol_login_server.protocol_login_server.logoff_API_call(cherrypy.session['userdata'])
            global listLoggedInUsers
            thisUser = None
            for user in listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    thisUser = user
            listLoggedInUsers.remove(thisUser)
            del cherrypy.session['userdata']
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def login_check(self, username, password):
        hashed = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
        cherrypy.session['userdata'] = protocol_login_server.protocol_login_server(username, hashed)
        protocol_login_server.protocol_login_server.reporter_thread(cherrypy.session['userdata'])
        if cherrypy.session['userdata'].tfa:
            raise cherrypy.HTTPRedirect("tfa.html")
        if cherrypy.session['userdata'].status:
            global listLoggedInUsers
            newUser = {'username': cherrypy.session['userdata'].username, 'rsakey': cherrypy.session['userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            listLoggedInUsers.append(newUser)
            if len(listLoggedInUsers) == 1:
                protocol_login_server.protocol_login_server.peerlist_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.profile_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.retrieve_messages_thread(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login.html")
    
    @cherrypy.expose
    def tfa_check(self, seccode):
        if int(seccode) == int(cherrypy.session['userdata'].seccode):
            cherrypy.session['userdata'].status = True
            cherrypy.session['userdata'].tfa = False
        if cherrypy.session['userdata'].status:
            global listLoggedInUsers
            newUser = {'username': cherrypy.session['userdata'].username, 'rsakey': cherrypy.session['userdata'].rsakey, 'pubkey': cherrypy.session['userdata'].pubkey, 'status': 'Online'}
            listLoggedInUsers.append(newUser)
            if len(listLoggedInUsers) == 1:
                protocol_login_server.protocol_login_server.profile_thread(cherrypy.session['userdata'])
                protocol_login_server.protocol_login_server.peerlist_thread(cherrypy.session['userdata'])
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def home(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login.html")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            sidebar = get_formated_peer_list()
            sidebar = sidebar + "</div><div class='intro-screen-wrap col-lg-8'><table style='height: 400px;'><tbody><tr><td class='align-middle'><h2><center>Click on an active users name on the left to start chatting.</center></h2></td></tr></tbody></table></div></div>"
            statusStuff = "</br><form action='/updateStatus' id='usrstatus' method='post' enctype='multipart/form-data'><select name='newStatus' onchange='if(this.value != 0) { this.form.submit(); }'>"
            statusTypes = ['Online', 'Idle', 'Do Not Disturb', 'Away', 'Offline']
            for user in listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    for typ in statusTypes:
                        if typ == user['status']:
                            statusStuff = statusStuff + "<option selected value='" + typ + "'>" + typ + "</option>"
                        else:
                            statusStuff = statusStuff + "<option value='" + typ + "'>" + typ + "</option>"
            statusStuff = statusStuff + "</select></form>"
            return header + sidebar + statusStuff + footer
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def editProfile(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login.html")
        if cherrypy.session['userdata'].status:
            head = ''
            foot = ''
            with open ("editprofile_header.html", "r") as myfile : 
                head = myfile.read()
            with open ("editprofile_footer.html", "r") as myfile :
                foot = myfile.read()
            payload = db.getUserData(cherrypy.session['userdata'].username)
            if payload == []:
                payload = [{'picture': '', 'description': '', 'location': '', 'position': '', 'fullname': ''}]
            sidebar = cherrypy.session['userdata'].username + "</div><div class='login-form-1'><form accept-charset='UTF-8' action='/updateProfile' id='updateProfile'  class='text-left' method='post' enctype='multipart/form-data'><div class='login-form-main-message'></div><div class='main-login-form'><div class='login-group'>"
            for thing in payload[0]:
                if thing == 'username':
                    continue
                sidebar = sidebar + "<div class='form-group'><label for='" + thing + "' class='sr-only'>" + thing + "</label><input type='text' class='form-control' id='" + thing + "' name='" + thing + "' placeholder='" + thing + "' value='" + payload[0][thing] + "'></div>"
            if payload[0]['tfa'] == 'on':
                sidebar = sidebar + "<div class='form-group login-group-checkbox'><input type='checkbox' class='' id='tfa' name='tfa' checked><label for='tfa'>Two Factor Authentication</label></div>"
            else:
                sidebar = sidebar + "<div class='form-group login-group-checkbox'><input type='checkbox' class='' id='tfa' name='tfa'><label for='tfa'>Two Factor Authentication</label></div>"
            return head + sidebar.encode("ascii") + foot
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def updateProfile(self, picture, description, location, position, fullname, tfa):
        if tfa[1] == 'on':
            tfa = 'on'
        else:
            tfa = 'off'
        db.updateUserData(cherrypy.session['userdata'].username, picture, description, location, position, fullname, tfa)
        if cherrypy.session['userdata'].currentChat == '':
            raise cherrypy.HTTPRedirect("home")
        else:
            raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")

    @cherrypy.expose
    def chat(self, userID):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login.html")
        if cherrypy.session['userdata'].status:
            userID = userID.replace("\'", "")
            cherrypy.session['userdata'].currentChat = userID
            sidebar = get_formated_peer_list()
            messageHistory = unicode(get_formated_message_list(userID))
            statusStuff = "</br><form action='/updateStatus' id='usrstatus' method='post' enctype='multipart/form-data'><select name='newStatus' onchange='if(this.value != 0) { this.form.submit(); }'>"
            statusTypes = ['Online', 'Idle', 'Do Not Disturb', 'Away', 'Offline']
            for user in listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    for typ in statusTypes:
                        if typ == user['status']:
                            statusStuff = statusStuff + "<option selected value='" + typ + "'>" + typ + "</option>"
                        else:
                            statusStuff = statusStuff + "<option value='" + typ + "'>" + typ + "</option>"
            statusStuff = statusStuff + "</select></form>"
            return header + sidebar + messageHistory + statusStuff + footer
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def updateStatus(self, newStatus):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login.html")
        if cherrypy.session['userdata'].status:
            global listLoggedInUsers
            for user in listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    user['status'] = newStatus
            if cherrypy.session['userdata'].currentChat == '':
                raise cherrypy.HTTPRedirect("home")
            else:
                raise cherrypy.HTTPRedirect("chat?userID=\'" + cherrypy.session['userdata'].currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def sendMessage(self, message, attachments):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login.html")
        if cherrypy.session['userdata'].status:
            data = {'sender': unicode(cherrypy.session['userdata'].username), 'destination': unicode(cherrypy.session['userdata'].currentChat), 'message': unicode(message), 'markdown': '1', 'stamp': unicode(int(time.time())), 'encryption': '0', 'hashing': '0', 'hash': ' '}
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
                stuff = {'sender': cherrypy.session['userdata'].username, 'destination': cherrypy.session['userdata'].currentChat, 'file': attachments, 'content_type': content_type,'filename': filname, 'stamp': unicode(int(time.time())), 'encryption': 0, 'hash': '', 'hashing': 0}
                files = True
            except:
                pass
            if not files:
                db.addNewMessage(data)
            offline = True
            for peer in protocol_login_server.peerList:
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
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage?encoding=2', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                            if '0: ' in response:
                                db.updateMessageStatus(sentMessage, 'DELIVERED')
                            offline = False
                        except:
                            pass
                    if files:
                        payload = messageProcess.process(stuff, peer)
                        payload = json.dumps(payload)
                        try:
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                        except:
                            pass
                        sentMessage['message'] = sentMessage['message'] + text
                        sentMessage['status'] = 'SENT'
                        db.addNewMessage(sentMessage)
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
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage?encoding=2', payload, {'Content-Type': 'application/json'})
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
            raise cherrypy.HTTPRedirect("login.html")

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        return file("404.html")

    @cherrypy.expose
    def listAPI(self):
        if access_control.access_control():
            return ("""Available APIs: 
/listAPI 
/ping 
/recieveMessage [sender] [destination] [message] [stamp(opt)] [markdown] [encoding(opt)] [encryption(opt)] [hashing(opt)] [hash(opt)]
/acknowledge [sender] [stamp] [hash] [hashing]
/getPublicKey [sender]
/handshake [message] [encryption]
/getProfile [sender]
/recieveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption] [hash]
/retrieveMessages [sender]
/getStatus [profile_username]
/getList [username] [encryption] [json]
/report [username] [passphrase] [signature] [location] [ip] [port] [encryption(opt)]
Encoding: 0, 2
Encryption: 0, 1, 2, 3, 4
Hashing: 0, 1, 2, 3, 4, 5, 6, 7, 8""")
        else:
            return ("403: Forbidden error")
        
    @cherrypy.expose
    def ping(self):
        return ('0')
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self, encoding=2):
        if access_control.access_control():
            data = cherrypy.request.json
            data = messageProcess.unprocess(data, listLoggedInUsers)
            if isinstance(data, basestring):
                return data
            
            data['status'] = 'IN TRANSIT'
            for user in listLoggedInUsers:
                if user['username'] == data['destination']:
                    data['status'] = 'DELIVERED'
            
            if db.addNewMessage(data):
                return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
            else:
                return ('1: Missing Compulsory Field')
        else:
            return ("403: Forbidden error")
    
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
            return ("403: Forbidden error")
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getPublicKey(self):
        if access_control.access_control():
            sender = cherrypy.request.json
            for user in listLoggedInUsers:
                if user['username'] == sender['profile_username']:
                    return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'pubkey': user['pubkey']}
        else:
            return ("403: Forbidden error")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handshake(self):
        if access_control.access_control():
            data = cherrypy.request.json
            if int(data['encryption']) == 1:
                data['message'] = Ciphers.XORCipher.decrypt(data['message'])
            if int(data['encryption']) == 2:
                data['message'] = Ciphers.AESCipher.decrypt(data['message'], '41fb5b5ae4d57c5ee528adb078ac3b2e')
            if int(data['encryption']) == 3:
                for user in listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['message'] = Ciphers.RSA1024Cipher.decryptValue(data['message'], user['rsakey'])
            if int(data['encryption']) == 4:
                for user in listLoggedInUsers:
                    if user['username'] == data['destination']:
                        data['decryptionKey'] = Ciphers.RSA1024Cipher.decryptValue(data['decryptionKey'], user['rsakey'])
                data['message'] = Ciphers.AESCipher.decrypt(data['message'], data['decryptionKey'])
            return {'error': u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது', 'message': data['message']}
        else:
            return ("403: Forbidden error")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
        if access_control.access_control():
            sender = cherrypy.request.json
            data = db.getUserData(sender['profile_username'])
            data[0]['encoding'] = 2
            data[0]['encryption'] = 0
            return data[0]  
        else:
            return ("403: Forbidden error")
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        if access_control.access_control():
            data = messageProcess.unprocess(data, listLoggedInUsers)
            if isinstance(data, basestring):
                return data
            if sizeb64(data['file']) > 5242880:
                return (u'6, உங்கள் கோப்பு எல்லைக்குள் இல்லை')
            file = open ('static/downloads/' + data['filename'].encode("ascii"), "wb")
            file.write(base64.b64decode(data['file']))
            file.close()
            content_type = mimetypes.guess_type(data['filename'])[0]
            text = '<a href="'  + os.path.join('downloads', data['filename']) + '\" download>' + data['filename'] + '</a>'
            if 'image/' in content_type:
                text = '<img src="'  + os.path.join('downloads', data['filename']) + '\" alt=\"' + data['filename'] + '\" width="320">'
            if 'audio/' in content_type:
                text = '<audio controls><source src="' + os.path.join('downloads', data['filename']) + '\" type=\"' + content_type + '\"></audio>'
            if 'video/' in content_type:
                text = '<video width="320" height="240" controls><source src="'  + os.path.join('downloads', data['filename']) + '\" type=\"' + content_type + '\"></video>'
            payload = {'sender': data['sender'], 'destination': data['destination'], 'message': text, 'stamp': data['stamp'], 'encoding': 2, 'encryption': 2, 'hashing': 0, 'hash': '', 'status': 'IN TRANSIT', 'markdown': 0}
            for user in listLoggedInUsers:
                if user['username'] == payload['destination']:
                    payload['status'] = 'DELIVERED'
            db.addNewMessage(payload)
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("403: Forbidden error")
    
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
                    file = open ('static/downloads/' + filname.encode("ascii"), "rb")
                    attachments = base64.b64encode(file.read())
                    file.close()
                    for peer in protocol_login_server.peerList:
                        if message['destination'] == peer['username']:
                            stuff = {'sender': message['sender'], 'destination': message['desination'], 'file': attachments, 'content_type': content_type,'filename': filname, 'stamp': message['stamp'], 'encryption': 0, 'hash': '', 'hashing': 0}
                            data = messageProcess.process(stuff, peer)
                            payload = json.dumps(data)
                            req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveFile', payload, {'Content-Type': 'application/json'})
                            response = urllib2.urlopen(req).read()
                            db.updateMessageStatus(message, 'DELIVERED')
                else:
                    data = message
                    for peer in protocol_login_server.peerList:
                        if message['destination']== peer['username']:
                            data = messageProcess.process(data, peer)
                            payload = json.dumps(data)
                            try:
                                req = urllib2.Request('http://' + unicode(peer['ip']) + ':' + unicode(peer['port']) + '/receiveMessage?encoding=2', payload, {'Content-Type': 'application/json'})
                                response = urllib2.urlopen(req).read()
                                db.updateMessageStatus(message, 'DELIVERED')
                            except:
                                pass
            return (u'0: உரை வெற்றிகரமாகப் பெட்ட்ருகொண்டது')
        else:
            return ("403: Forbidden error")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getStatus(self):
        if access_control.access_control():
            data = cherrypy.request.json
            for user in listLoggedInUsers:
                if user['username'] == data['profile_username']:
                    return {'status', user['status']}
        else:
            return ("403: Forbidden error")

    @cherrypy.expose
    def getList(self, username, json_format=0):
        if access_control.access_control():
            if int(json_format) == 1:
                peerlist = {str(k): v for k, v in enumerate(protocol_login_server.peerList)}
                return json.dumps(peerlist)
            else:
                resp = '0: '
                for peer in protocol_login_server.peerList:
                    resp = resp + peer['username'] + ',' + peer['location'] + ',' + peer['ip'] + ',' + peer['port'] + ',' + peer['lastLogin'] + ',' + peer['publicKey'] + ','
                return resp
        else:
            return ("403: Forbidden error")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def report(self):
        if access_control.access_control():
            message = cherrypy.request.json
            hashed = SHA512.new(data['passphrase']).hexdigest()
            if message['signature'] == Ciphers.RSA1024Cipher.encryptValue(hashed, db.getUserProfile(message['username'])[0]['publicKey']):
                pass
        else:
            return ("403: Forbidden error")

        
    WEB_ROOT = os.path.join(os.getcwd(), 'static') 

    cherrypy.config.update({'error_page.404': error_page_404,
                            'server.socket_host': '0.0.0.0',
                            'server.socket_port': 10008,
                            'engine.autoreload.on': False,
                            'tools.sessions.on': True,
                            'tools.encode.on': True,
                            'tools.encode.encoding': 'utf-8',
                            'tools.staticdir.on' : True,
                            'tools.staticdir.dir' : WEB_ROOT,
                            'tools.staticdir.index' : 'index.html'})

cherrypy.engine.subscribe('stop', stop)
cherrypy.quickstart(MainClass())
