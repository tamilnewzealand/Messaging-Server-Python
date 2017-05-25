import sqlite3
import os.path
import urllib

def initTable(c) :
	# Creating a table for message archive and accounts info storage
	c.execute("CREATE TABLE messages (sender STRING, destination STRING, message STRING, stamp STRING, encoding STRING, encryption STRING, hashing STRING, hash STRING, status STRING)")
	c.execute("CREATE TABLE usernames (username STRING, fullname STRING, position STRING, description STRING, location STRING, picture STRING)")
	c.execute("CREATE TABLE userprofiles (username STRING, ip STRING, location STRING, lastLogin STRING, port STRING, fullname STRING, position STRING, description STRING, location STRING, picture STRING)")
	data = urllib.urlopen("https://cs302.pythonanywhere.com/listUsers").read()
	data = data.replace(",", "'), ('")
	c.execute("INSERT INTO userprofiles (username) VALUES ('" + data + "')")
	return c

def openDB() :
	if os.path.isfile('user_data.sqlite'):
		conn = sqlite3.connect('user_data.sqlite')
		c = conn.cursor()
		return (conn, c)
	else :
		conn = sqlite3.connect('user_data.sqlite')
		c = conn.cursor()
		c = initTable(c)
		return (conn, c)

def closeDB(conn, c):
	conn.commit()
	conn.close()

def addNewMessage(data):
	(conn, c) = openDB()
	c.execute("SELECT * FROM messages WHERE sender='{a}' AND destination='{b}' AND message='{c}' AND stamp='{d}'".format(a=data['sender'], b=data['destination'], c=data['message'], d=data['stamp']))
	stuff = c.fetchall()
	if stuff == []:
		try:
			c.execute("INSERT INTO messages VALUES ('{a}', '{b}', '{c}', '{d}', '{e}', '{f}', '{g}', '{h}', '{i}')".format(a=data['sender'], b=data['destination'], c=data['message'], d=data['stamp'], e=data['encoding'], f=data['encryption'], g=data['hashing'], h=data['hash'], i=data['status']))
		except:
			print('Error: Primary key already exists')
	closeDB(conn, c)
		
def readOutMessages(messageUser, myUserID):
	(conn, c) = openDB()
	messageList = ''
	try :
		c.execute("SELECT * FROM messages WHERE sender='{a}' AND destination='{b}' OR sender='{b}' AND destination='{a}'".format(a=messageUser, b=myUserID))
		messageList = [dict(zip(['sender', 'destination', 'message', 'stamp', 'encoding', 'encryption', 'hashing', 'hash', 'status'], row)) for row in c.fetchall()]
	except :
		pass
	closeDB(conn, c)
	return messageList

def lookUpMessage(data):
	(conn, c) = openDB()
	c.execute("SELECT * FROM messages WHERE sender='{a}' AND hashing='{b}' AND hash='{c}' AND stamp='{d}'".format(a=data['sender'], b=data['hashing'], c=data['hash'], d=data['stamp']))
	stuff = c.fetchall()
	if stuff == []:
		closeDB(conn, c)
		return False
	c.execute("UPDATE messages SET status='SEEN' WHERE sender='{a}' AND hashing='{b}' AND hash='{c}' AND stamp='{d}'".format(a=data['sender'], b=data['hashing'], c=data['hash'], d=data['stamp']))
	closeDB(conn, c)
	return True

def getUserData(user):
	(conn, c) = openDB()
	userdata = ''
	try :
		c.execute("SELECT * FROM usernames WHERE username='{a}'".format(a=user))
		userdata = [dict(zip(['username', 'fullname', 'position', 'description', 'location', 'picture'], row)) for row in c.fetchall()]
	except :
		pass
	closeDB(conn, c)
	return userdata

def updateUserData(username, picture, description, location, position, fullname):
	try :
		(conn, c) = openDB()
		c.execute("SELECT * FROM usernames WHERE username='{a}'".format(a=username))
		stuff = c.fetchall()
		if stuff == []:
			c.execute("INSERT INTO usernames VALUES ('{a}', '{b}', '{c}', '{d}', '{e}', '{f}')".format(a=username, b=fullname, c=position, d=description, e=location, f=picture))
		c.execute("UPDATE usernames SET fullname='{b}', position='{c}', description='{d}', location='{e}', picture='{f}' WHERE username='{a}'".format(a=username, b=fullname, c=position, d=description, e=location, f=picture))
		closeDB(conn, c)
	except :
		pass

def getUserProfile(user):
	(conn, c) = openDB()
	userdata = ''
	try :
		c.execute("SELECT * FROM userprofiles WHERE username='{a}'".format(a=user))
		userdata = [dict(zip(['username', 'ip', 'location', 'lastLogin', 'port', 'fullname', 'position', 'description', 'picture'], row)) for row in c.fetchall()]
	except :
		pass
	closeDB(conn, c)
	return userdata

def updateUserProfileA(data):
	try :
		(conn, c) = openDB()
		c.execute("UPDATE userprofiles SET fullname='{b}', position='{c}', description='{d}', picture='{e}' WHERE username='{a}'".format(a=data['username'], b=data['fullname'], c=data['position'], d=data['description'], e=data['picture']))
		closeDB(conn, c)
	except :
		pass

def updateUserProfileB(username, ip, location, lastLogin, port):
	try :
		(conn, c) = openDB()
		c.execute("UPDATE userprofiles SET ip='{b}', location='{c}', lastLogin='{d}', port='{e}'WHERE username='{a}'".format(a=username, b=ip, c=location, d=lastLogin, e=port))
		closeDB(conn, c)
	except :
		pass

def getPeerList():
	(conn, c) = openDB()
	userdata = ''
	try :
		c.execute("SELECT * FROM userprofiles")
		userdata = [dict(zip(['username', 'ip', 'location', 'lastLogin', 'port', 'fullname', 'position', 'description', 'picture'], row)) for row in c.fetchall()]
	except :
		pass
	closeDB(conn, c)
	return userdata