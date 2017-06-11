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

import pageGenerator
import internalJSON
import internalAPI
import external
import thread
import logserv
import cherrypy
import access_control
import os

"""
    Starts a thread which keeps count of how many connections
    are coming from various IPs for rate limiting.
"""
thread.start_new_thread(access_control.ac_timer, ('0', ))

"""
    Called when closing down node, calls logoff on every logged in node.
"""
def stop():
    logserv.logserv.logoffEveryone(logserv.listLoggedInUsers)
    del logserv.listLoggedInUsers


class internal(internalJSON.internalJSON, internalAPI.internalAPI):
    pass


class external(pageGenerator.pageGenerator, external.external):
    pass

"""
    Main class which contains all the exposed APIs,
    inherits from multiple classes which contain the necessary
    methods sorted by task.
"""
class MainClass(internal, external):

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        return file("404.html")

    WEB_ROOT = os.path.join(os.getcwd(), 'static')

    cherrypy.config.update({'error_page.404': error_page_404,
                            'server.socket_host': '0.0.0.0',
                            'server.socket_port': 10008,
                            'engine.autoreload.on': False,
                            'tools.sessions.on': True,
                            'tools.encode.on': True,
                            'tools.encode.encoding': 'utf-8',
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': WEB_ROOT,
                            'tools.staticdir.index': 'index.html'})


cherrypy.engine.subscribe('stop', stop)
cherrypy.quickstart(MainClass())
