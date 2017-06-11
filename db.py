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

import sqlite3
import os.path
import urllib2
import string


def initTable(c):
    # Creating a table for message archive and accounts info storage
    c.execute("CREATE TABLE messages (sender STRING, destination STRING, message STRING, stamp STRING, encryption STRING, hashing STRING, hash STRING, status STRING, markdown STRING)")
    c.execute("CREATE TABLE usernames (username STRING, fullname STRING, position STRING, description STRING, location STRING, picture STRING, hash STRING, tfa STRING)")
    c.execute("CREATE TABLE userprofiles (username STRING, ip STRING, location STRING, lastLogin STRING, port STRING, fullname STRING, position STRING, description STRING, picture STRING, publicKey STRING, status STRING)")
    c.execute("CREATE TABLE events (sender STRING, destination STRING, event_name STRING, event_description STRING, event_location STRING, event_picture STRING, start_time STRING, end_time STRING, markdown STRING, encryption STRING, status STRING)")
    data = urllib2.urlopen(
        "https://cs302.pythonanywhere.com/listUsers", timeout=5).read()
    data = data.replace(",", "'), ('")
    c.execute("INSERT INTO userprofiles (username) VALUES ('" + data + "')")
    return c


"""
    Opens the database file ready for SQL operations.
    If file doesn't exist, a new file with appropriate
    tables are created.
"""


def openDB():
    if os.path.isfile('user_data.sqlite'):
        conn = sqlite3.connect('user_data.sqlite')
        c = conn.cursor()
        return (conn, c)
    else:
        conn = sqlite3.connect('user_data.sqlite')
        c = conn.cursor()
        c = initTable(c)
        return (conn, c)


"""
    Closes the connection to the data base file.
"""


def closeDB(conn, c):
    conn.commit()
    conn.close()


"""
    The following methods abstract particular read and
    write operations to the database away from the rest 
    of the codebase. Methods are named appropriately to
    reflect the read / write operation which they make 
    possible.
"""


def addNewMessage(data):
    (conn, c) = openDB()
    c.execute("SELECT * FROM messages WHERE sender='{a}' AND destination='{b}' AND stamp='{d}'".format(
        a=data['sender'], b=data['destination'], d=data['stamp']))
    stuff = c.fetchall()
    if 'status' not in data:
        data['status'] = 'OUTBOX'
    if stuff == []:
        try:
            c.execute(
                "INSERT INTO messages VALUES (:sender, :destination, :message, :stamp, :encryption, :hashing, :hash, :status, :markdown)", data)
            closeDB(conn, c)
            return True
        except:
            closeDB(conn, c)
            return False


def readOutMessages(messageUser, myUserID):
    (conn, c) = openDB()
    messageList = ''
    try:
        c.execute(
            "SELECT * FROM messages WHERE sender='{a}' AND destination='{b}' OR sender='{b}' AND destination='{a}'".format(a=messageUser, b=myUserID))
        messageList = [dict(zip(['sender', 'destination', 'message', 'stamp', 'encryption',
                                 'hashing', 'hash', 'status', 'markdown'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return messageList


def getTransitingMessages(messageUser):
    (conn, c) = openDB()
    messageList = ''
    try:
        c.execute(
            "SELECT * FROM messages WHERE destination='{a}' AND status='IN TRANSIT'".format(a=messageUser))
        messageList = [dict(zip(['sender', 'destination', 'message', 'stamp', 'encryption',
                                 'hashing', 'hash', 'status', 'markdown'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return messageList


def updateMessageStatus(data, newStatus):
    (conn, c) = openDB()
    c.execute("SELECT * FROM messages WHERE sender='{a}' AND hashing='{b}' AND hash='{c}' AND stamp='{d}'".format(
        a=data['sender'], b=data['hashing'], c=data['hash'], d=data['stamp']))
    stuff = c.fetchall()
    if stuff == []:
        closeDB(conn, c)
        return False
    c.execute("UPDATE messages SET status='{a}' WHERE sender='{b}' AND hashing='{c}' AND hash='{d}' AND stamp='{e}'".format(
        a=newStatus, b=data['sender'], c=data['hashing'], d=data['hash'], e=data['stamp']))
    closeDB(conn, c)
    return True


def getUserData(user):
    (conn, c) = openDB()
    userdata = ''
    try:
        c.execute(
            "SELECT * FROM usernames WHERE username='{a}'".format(a=user))
        userdata = [dict(zip(['username', 'fullname', 'position', 'description',
                              'location', 'picture', 'hash', 'tfa'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return userdata


def updateUserData(username, picture, description, location, position, fullname, tfa):
    try:
        (conn, c) = openDB()
        c.execute(
            "SELECT * FROM usernames WHERE username='{a}'".format(a=username))
        stuff = c.fetchall()
        if stuff == []:
            c.execute("INSERT INTO usernames VALUES ('{a}', '{b}', '{c}', '{d}', '{e}', '{f}', '{g}')".format(
                a=username, b=fullname, c=position, d=description, e=location, f=picture, g=tfa))
        c.execute("UPDATE usernames SET fullname='{b}', position='{c}', description='{d}', location='{e}', picture='{f}', tfa='{g}' WHERE username='{a}'".format(
            a=username, b=fullname, c=position, d=description, e=location, f=picture, g=tfa))
        closeDB(conn, c)
    except:
        pass


def updateUserHash(username, hashed):
    try:
        (conn, c) = openDB()
        c.execute(
            "SELECT * FROM usernames WHERE username='{a}'".format(a=username))
        stuff = c.fetchall()
        if stuff == []:
            c.execute("INSERT INTO usernames (username, hash, tfa) VALUES ('{a}', '{b}', 'on')".format(
                a=username, b=hashed))
        else:
            c.execute("UPDATE usernames SET hash='{b}' WHERE username='{a}'".format(
                a=username, b=hashed))
        closeDB(conn, c)
    except:
        pass


def checkUserHash(username, hashed):
    try:
        (conn, c) = openDB()
        c.execute(
            "SELECT * FROM usernames WHERE username='{a}' AND hash='{b}'".format(a=username, b=hashed))
        stuff = c.fetchall()
        closeDB(conn, c)
        if stuff == []:
            return False
        else:
            return True
    except:
        return False


def getUserProfile(user):
    (conn, c) = openDB()
    userdata = ''
    try:
        c.execute(
            "SELECT * FROM userprofiles WHERE username='{a}'".format(a=user))
        userdata = [dict(zip(['username', 'ip', 'location', 'lastLogin', 'port', 'fullname',
                              'position', 'description', 'picture', 'publicKey'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return userdata


def updateUserProfileA(data):
    try:
        (conn, c) = openDB()
        if 'fullname' not in data:
            data['fullname'] = ''
        if 'position' not in data:
            data['position'] = ''
        if 'description' not in data:
            data['description'] = ''
        if 'picture' not in data:
            data['picture'] = ''
        c.execute("UPDATE userprofiles SET fullname='{b}', position='{c}', description='{d}', picture='{e}' WHERE username='{a}'".format(
            a=data['username'], b=data['fullname'], c=data['position'], d=data['description'], e=data['picture']))
        closeDB(conn, c)
    except:
        pass


def updateUserStatus(username, currentstatus):
    try:
        (conn, c) = openDB()
        c.execute("UPDATE userprofiles SET status='{a}' WHERE username='{b}'".format(
            a=currentstatus, b=username))
        closeDB(conn, c)
    except:
        pass


def updateUserProfileB(username, ip, location, lastLogin, port, publickey):
    try:
        (conn, c) = openDB()
        c.execute("UPDATE userprofiles SET ip='{b}', location='{c}', lastLogin='{d}', port='{e}', publicKey='{f}' WHERE username='{a}'".format(
            a=username, b=ip, c=location, d=lastLogin, e=port, f=publickey))
        closeDB(conn, c)
    except:
        pass


def getPeerList():
    (conn, c) = openDB()
    userdata = ''
    try:
        c.execute("SELECT * FROM userprofiles")
        userdata = [dict(zip(['username', 'ip', 'location', 'lastLogin', 'port', 'fullname', 'position',
                              'description', 'picture', 'publicKey', 'status'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return userdata


def getEventList():
    (conn, c) = openDB()
    userdata = ''
    try:
        c.execute("SELECT * FROM events")
        eventdata = [dict(zip(['sender', 'destination', 'event_name', 'event_description', 'event_location',
                               'event_picture', 'start_time', 'end_time', 'markdown', 'encryption', 'status'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return eventdata


def getEvent(event_name, start_time):
    (conn, c) = openDB()
    userdata = ''
    try:
        c.execute(
            "SELECT * FROM events WHERE event_name='{a}' AND start_time='{b}'".format(a=event_name, b=start_time))
        eventdata = [dict(zip(['sender', 'destination', 'event_name', 'event_description', 'event_location',
                               'event_picture', 'start_time', 'end_time', 'markdown', 'encryption', 'status'], row)) for row in c.fetchall()]
    except:
        pass
    closeDB(conn, c)
    return eventdata


def updateEventStatus(newStatus, sender, event_name, start_time):
    try:
        (conn, c) = openDB()
        c.execute("UPDATE events SET status='{a}' WHERE sender='{b}' AND event_name='{c}' AND start_time='{d}'".format(
            a=newStatus, b=sender, c=event_name, d=start_time))
        closeDB(conn, c)
    except:
        pass


def addNewEvent(data):
    (conn, c) = openDB()
    c.execute("SELECT * FROM events WHERE sender='{a}' AND event_name='{b}' AND start_time='{c}'".format(
        a=data['sender'], b=data['event_name'], c=data['start_time']))
    stuff = c.fetchall()
    if stuff == []:
        try:
            c.execute("INSERT INTO events VALUES (:sender, :destination, :event_name, :event_description, :event_location, :event_picture, :start_time, :end_time, :markdown, :encryption, :status)", data)
            closeDB(conn, c)
            return True
        except:
            closeDB(conn, c)
            return False
