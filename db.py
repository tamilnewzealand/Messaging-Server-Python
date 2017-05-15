import sqlite3
import os.path
import stuff

def initTable(c) :
	# Creating a table for message archive and accounts info storage
	c.execute("CREATE TABLE messages (from_user STRING, to_user STRING, time_stamp STRING, status STRING, message STRING, attachment STRING, attachment_name STRING)")
	c.execute("CREATE TABLE accounts (username STRING PRIMARY KEY  NOT NULL  UNIQUE , password STRING NOT NULL , email STRING, realname STRING, gender STRING)")
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

def closeDB(conn, c) :
	conn.commit()
	conn.close()
	return (conn, c)

def registerAccount(c, username, password, email, realname, gender) :
	try:
		c.execute("INSERT INTO accounts VALUES ('{a}', '{b}', '{c}', '{d}', '{e}')".format(a=username, b=password, c=email, d=realname, e=gender))
		return True
	except:
		return False

def addNewMessage(c, ob) :
	try:
		c.execute("INSERT INTO messages VALUES ('{a}', '{b}', '{c}', '{d}', '{e}', '{f}', '{g}')".format(a=ob.fromUser, b=ob.toUser, c=ob.time_stamp, d=ob.status, e=ob.message, f=ob.attachment, g=ob.attachment_name))
	except:
		print('Error: Primary key already exists')
		
def readOutMessages(c, messageList, messageUser, myUserID) :
	try :
		for row in c.execute("SELECT * FROM messages WHERE from_user='{a}' AND to_user='{b}' OR from_user='{b}' AND to_user='{a}'".format(a=messageUser, b=myUserID)) :
			rowTuples = str(row).split(', u')
			for i in range(len(rowTuples)) :
				rowTuples[i] =rowTuples[i].replace("\'", "").replace("(u", "").replace(")", "")
			mess = stuff.classMessage(rowTuples[0], rowTuples[1], rowTuples[2], rowTuples[3], rowTuples[4], rowTuples[5], rowTuples[6])			
			messageList.append(mess)
	except :
		message = ''
	return messageList

def lookUpUser(c, username) :
	for row in c.execute("SELECT * FROM accounts WHERE username='{a}'".format(a=username)) :
		rowTuples = str(row).split(', u')
		for i in range(len(rowTuples)) :
			rowTuples[i] =rowTuples[i].replace("\'", "").replace("(", "").replace(")", "")
		return (rowTuples[1], rowTuples[3])
	return "User not found"
