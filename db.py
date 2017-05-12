import sqlite3
import os.path
import stuff

def initTable(c) :
    # Creating a table for message archive
    c.execute("CREATE TABLE messages (from_user STRING)")
    c.execute("ALTER TABLE messages ADD COLUMN to_user STRING")
    c.execute("ALTER TABLE messages ADD COLUMN time_stamp STRING")
    c.execute("ALTER TABLE messages ADD COLUMN status STRING")
    c.execute("ALTER TABLE messages ADD COLUMN message STRING")
    c.execute("ALTER TABLE messages ADD COLUMN attachment STRING")
    return c

def openDB(conn, c) :
	if os.path.isfile('user_data.sqlite'):
		conn = sqlite3.connect('user_data.sqlite')
		c = conn.cursor()
	else :
		conn = sqlite3.connect('user_data.sqlite')
		c = conn.cursor()
		c = initTable(c)
	return (conn, c)

def closeDB(conn, c) :
	conn.commit()
	conn.close()
	return (conn, c)

def addNewMessage(c, ob) :
	try:
		c.execute("INSERT INTO messages VALUES ('{a}', '{b}', '{c}', '{d}', '{e}', '{f}')".format(a=ob.fromUser, b=ob.toUser, c=ob.time_stamp, d=ob.status, e=ob.message, f=ob.attachment))
	except sqlite3.IntegrityError:
		print('Error: Primary key already exists')
		
def readOutMessages(c, messageList, messageUser) :
	try :
		for row in c.execute("SELECT * FROM messages WHERE from_user='{a}' OR to_user='{a}'".format(a=messageUser)) :
			rowTuples = str(row).split(', u')
			for i in range(len(rowTuples)) :
				rowTuples[i] =rowTuples[i].replace("'", "").replace("(u", "").replace(")", "")
			mess = stuff.classMessage(rowTuples[0], rowTuples[1], rowTuples[2], rowTuples[3], rowTuples[4], rowTuples[5])			
			messageList.append(mess)
	except :
		message = ''
	return messageList
	

