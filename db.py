import sqlite3
import os.path

def initTable(c) :
	# Creating a table for message archive and accounts info storage
	c.execute("CREATE TABLE messages (sender STRING, destination STRING, message STRING, stamp STRING, encoding STRING, encryption STRING, hashing STRING, hash STRING, status STRING)")
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
		pass
	else:
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