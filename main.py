# coding=utf8

import pageGenerator
import internalJSON
import internalAPI
import external
import thread
import logserv
import cherrypy
import access_control
import os

thread.start_new_thread(access_control.ac_timer, ('0', ))


def stop():
    if cherrypy.session['userdata'] is not None:
        logserv.logserv.logoff_API_call(cherrypy.session['userdata'])
        del cherrypy.session['userdata']
        del logserv.listLoggedInUsers


class internal(internalJSON.internalJSON, internalAPI.internalAPI):
    pass


class external(pageGenerator.pageGenerator, external.external):
    pass


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
