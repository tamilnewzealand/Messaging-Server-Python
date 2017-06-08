import cherrypy
import thread
import time

accessList = []

def getBlackList():
    blacklist = open("blacklist.txt", "r")
    lines = blacklist.read().split(',')
    blacklist.close()
    return lines

def setBlackList(listings):
    blacklist = open("blacklist.txt", "w")
    blacklist.write(listings)
    blacklist.close()

def access_control():
    ip = cherrypy.request.headers["Remote-Addr"]
    if ip in getBlackList():
        return False
    accessList.append(ip)
    if accessList.count(ip) > 100:
        return False
    return True

def ac_timer(started):
    starttime=time.time()
    while True:
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        global accessList
        accessList = []
