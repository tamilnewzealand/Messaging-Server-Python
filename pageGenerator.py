import cherrypy
import protocol_login_server

class pageGenerator(object):

    @cherrypy.expose
    def login(self):
        if 'userdata' in cherrypy.session:
            cherrypy.session['userdata'] = None
            return file("login.html")
        if 'userdata' not in cherrypy.session:
            return file("login.html")
        else:
            raise cherrypy.HTTPRedirect("home")
    
    @cherrypy.expose
    def logout(self):
        if 'userdata' in cherrypy.session:
            protocol_login_server.protocol_login_server.logoff_API_call(cherrypy.session['userdata'])
            thisUser = None
            for user in protocol_login_server.listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    thisUser = user
            protocol_login_server.listLoggedInUsers.remove(thisUser)
            del cherrypy.session['userdata']
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def home(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("home.html")
        else:
            cherrypy.session['userdata'] = None
            raise cherrypy.HTTPRedirect("login")
  
    @cherrypy.expose
    def chat(self, userID):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            userID = userID.replace("\'", "")
            cherrypy.session['userdata'].currentChat = userID
            return file("chat.html")
        else:
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def calendar(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("calendar.html")
        else:
            cherrypy.session['userdata'] = None
            raise cherrypy.HTTPRedirect("login")

    @cherrypy.expose
    def event(self, sender, name, start_time):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentEvent = {'sender': sender.replace("\'", ""), 'name': name.replace("\'", ""), 'start_time': start_time.replace("\'", "")}
            return file("event.html")
        else:
            raise cherrypy.HTTPRedirect("login")
    
    @cherrypy.expose
    def editProfile(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("editprofile.html")
        else:
            raise cherrypy.HTTPRedirect("login")