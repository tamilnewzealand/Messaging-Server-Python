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

import cherrypy
import logserv


class pageGenerator(object):

    """
        Checks if the user is logged in, if so redirects
        to the logged in home page. If not returns the login
        page.
    """
    @cherrypy.expose
    def login(self):
        if 'userdata' in cherrypy.session:
            cherrypy.session['userdata'] = None
            return file("login.html")
        if 'userdata' not in cherrypy.session:
            return file("login.html")
        else:
            raise cherrypy.HTTPRedirect("home")
    
    """
        Calls the logoff API call function, then deletes the user's
        session data and redirects the user to the websites root.
    """
    @cherrypy.expose
    def logout(self):
        if 'userdata' in cherrypy.session:
            logserv.logserv.logoffAPICall(cherrypy.session['userdata'])
            thisUser = None
            for user in logserv.listLoggedInUsers:
                if user['username'] == cherrypy.session['userdata'].username:
                    thisUser = user
            logserv.listLoggedInUsers.remove(thisUser)
            del cherrypy.session['userdata']
        raise cherrypy.HTTPRedirect("/")

    """
        Checks if the user is logged in and presents the
        appropriate page. If not logged in redirects to
        the login page.
    """
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
    
    """
        Checks if the user is logged in and presents the
        appropriate page. If not logged in redirects to
        the login page.
    """
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

    """
        Checks if the user is logged in and presents the
        appropriate page. If not logged in redirects to
        the login page.
    """
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

    """
        Checks if the user is logged in and presents the
        appropriate page. If not logged in redirects to
        the login page.
    """
    @cherrypy.expose
    def event(self, sender, name, start_time):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentEvent = {'sender': sender.replace(
                "\'", ""), 'name': name.replace("\'", ""), 'start_time': start_time.replace("\'", "")}
            return file("event.html")
        else:
            raise cherrypy.HTTPRedirect("login")

    """
        Checks if the user is logged in and presents the
        appropriate page. If not logged in redirects to
        the login page.
    """
    @cherrypy.expose
    def editProfile(self):
        if 'userdata' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("login")
        if cherrypy.session['userdata'].status:
            cherrypy.session['userdata'].currentChat = ''
            return file("editprofile.html")
        else:
            raise cherrypy.HTTPRedirect("login")
