listen_ip = "127.0.0.1"
listen_port = 8080

import cherrypy
import db
import stuff
import datetime
import base64
import bcrypt
from cherrypy.lib.static import serve_fileobj

def create_dummy_users():
    peerList = []
    peerList.append(stuff.peerList('userA', 'Pierre Pierre', '192.168.1.122'))
    peerList.append(stuff.peerList('userB', 'Paul Paul', '192.168.1.121'))
    peerList.append(stuff.peerList('userC', 'Jacques Jacques', '192.168.1.123'))
    peerList.append(stuff.peerList('userD', 'Tartampion Tartampion', '192.168.1.120'))
    peerList.append(stuff.peerList('userE', 'Machin Machin', '192.168.1.124'))
    peerList.append(stuff.peerList('userF', 'Trucmuche Trucmuche', '192.168.1.119'))
    peerList.append(stuff.peerList('userG', 'Patante Patante', '192.168.1.125'))
    return peerList

def get_formated_peer_list():
    peerList = create_dummy_users()
    sidebar = ''
    for peer in peerList :
        sidebar = sidebar + """<div class="media conversation"><a class="pull-left" href="chat?userID='""" + peer.userID + "\'" + """">
        <img class="media-object" data-src="holder.js/64x64" alt="64x64" style="width: 50px; height: 50px;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC"></a>
        <div class="media-body"><h5 class="media-heading">""" + peer.realName + """ </h5><small>Sample Text</small></div></div>"""
    return (str(sidebar), peerList)

def get_formated_message_list(userID, realUsersName):
    messageHistory = """</div><div class="message-wrap col-lg-8"><div class="msg-wrap">"""
    messageList = []
    (conn, c) = db.openDB()
    messageList = db.readOutMessages(c, messageList, userID, myUserID)
    (conn, c) = db.closeDB(conn, c)
    for row in messageList :
        name = myRealName
        if row.fromUser == myUserID :
            pass
        else :
            name = realUsersName
        messageHistory = messageHistory + """<div class="media msg">
            <a class="pull-left" href="#"><img class="media-object" data-src="holder.js/64x64" alt="64x64" style="width: 32px; height: 32px;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACqUlEQVR4Xu2Y60tiURTFl48STFJMwkQjUTDtixq+Av93P6iBJFTgg1JL8QWBGT4QfDX7gDIyNE3nEBO6D0Rh9+5z9rprr19dTa/XW2KHl4YFYAfwCHAG7HAGgkOQKcAUYAowBZgCO6wAY5AxyBhkDDIGdxgC/M8QY5AxyBhkDDIGGYM7rIAyBgeDAYrFIkajEYxGIwKBAA4PDzckpd+322243W54PJ5P5f6Omh9tqiTAfD5HNpuFVqvFyckJms0m9vf3EY/H1/u9vb0hn89jsVj8kwDfUfNviisJ8PLygru7O4TDYVgsFtDh9Xo9NBrNes9cLgeTybThgKenJ1SrVXGf1WoVDup2u4jFYhiPx1I1P7XVBxcoCVCr1UBfTqcTrVYLe3t7OD8/x/HxsdiOPqNGo9Eo0un02gHkBhJmuVzC7/fj5uYGXq8XZ2dnop5Mzf8iwMPDAxqNBmw2GxwOBx4fHzGdTpFMJkVzNB7UGAmSSqU2RoDmnETQ6XQiOyKRiHCOSk0ZEZQcUKlU8Pz8LA5vNptRr9eFCJQBFHq//szG5eWlGA1ywOnpqQhBapoWPfl+vw+fzweXyyU+U635VRGUBOh0OigUCggGg8IFK/teXV3h/v4ew+Hwj/OQU4gUq/w4ODgQrkkkEmKEVGp+tXm6XkkAOngmk4HBYBAjQA6gEKRmyOL05GnR99vbW9jtdjEGdP319bUIR8oA+pnG5OLiQoghU5OElFlKAtCGr6+vKJfLmEwm64aosd/XbDbbyIBSqSSeNKU+HXzlnFAohKOjI6maMs0rO0B20590n7IDflIzMmdhAfiNEL8R4jdC/EZIJj235R6mAFOAKcAUYApsS6LL9MEUYAowBZgCTAGZ9NyWe5gCTAGmAFOAKbAtiS7TB1Ng1ynwDkxRe58vH3FfAAAAAElFTkSuQmCC">
            </a><div class="media-body"><small class="pull-right time"><i class="fa fa-clock-o"></i>""" + row.time_stamp + "<br>" + row.status + """</small>
            <h5 class="media-heading">""" + name + """</h5><small class="col-lg-10">""" + row.message + """</small>"""
        if row.attachment_name == '' :
            messageHistory = messageHistory + """</div></div>"""
        else:
            messageHistory = messageHistory + """<a href=""" + '"download?userID=' + userID + '&realUsersName=' + realUsersName + '&message=' + row.message + '"' +  '>' + row.attachment_name + '</a></div></div>'
    messageHistory = str(messageHistory)

    if len(messageHistory) < 74 :
        messageHistory = messageHistory + "You have no chat history with this user, start chatting below ..."
    
    return (messageHistory, messageList)

currentChat = ''
myRealName = ''
myUserID = ''
status = False
header = ''
footerb = ''
footer = ''
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
        global myUserID
        global status
        myUserID = ''
        status = False
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def login_check(self, username, password):
        (conn, c) = db.openDB()
        (hashed, realname) = db.lookUpUser(c, username)
        (conn, c) = db.closeDB(conn, c)
        if bcrypt.checkpw(base64.b64encode(password), hashed):
            global myUserID
            myUserID = username
            global myRealName
            myRealName = realname
            global status
            status = True
            raise cherrypy.HTTPRedirect("home")
        raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def register_user(self, username, password, password_confirm, email, fullname, gender, reg_agree=''):
        if reg_agree == 'on':
            if password == password_confirm:
                hashed = bcrypt.hashpw(base64.b64encode(password), bcrypt.gensalt())
                (conn, c) = db.openDB()
                result = db.registerAccount(c, username, hashed, email, fullname, gender)
                (conn, c) = db.closeDB(conn, c)
                if result:
                    raise cherrypy.HTTPRedirect("login")
        raise cherrypy.HTTPRedirect("register")

    @cherrypy.expose
    def home(self):
        if status:
            (sidebar, peerlist) = get_formated_peer_list()
            sidebar = sidebar + "</div>"
            return header + sidebar + footerb
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def chat(self, userID):
        if status:
            userID = userID.replace("\'", "")
            global currentChat
            currentChat = userID
            (sidebar, peerList) = get_formated_peer_list()
            realUsersName = ''
            for x in peerList :
                if x.userID == userID :
                    realUsersName = x.realName
            (messageHistory, messageList) = get_formated_message_list(userID, realUsersName)
            return header + sidebar + messageHistory + footer
        else:
            raise cherrypy.HTTPRedirect("login")
        
    @cherrypy.expose
    def sendMessage(self, message, attachments):
        if status:
            filname = ''
            try :
                filname = attachments.filename
                attachments = base64.b64encode(attachments.file.read())
            except:
                attachments = ''
            
            global currentChat
            ob = stuff.classMessage(myUserID, currentChat, str(datetime.datetime.now()), 'SENT', message, attachments, filname)
            (conn, c) = db.openDB()
            db.addNewMessage(c, ob)
            (conn, c) = db.closeDB(conn, c)
            raise cherrypy.HTTPRedirect("chat?userID=\'" + currentChat + "\'")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def download(self, userID, realUsersName, message):
        if status:
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
    
    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,})

cherrypy.quickstart(MainClass())
