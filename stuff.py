
class classMessage:
    def __init__ (self, fromUser, toUser, time_stamp, status, message='', attachment='', attachment_name='') :
        self.fromUser = fromUser
        self.toUser = toUser
        self.time_stamp = time_stamp
        self.status = status
        self.message = message
        self.attachment = attachment
        self.attachment_name = attachment_name

class peerList :
    def __init__ (self, userID, realName, ipAddress) :
        self.userID = userID
        self.realName = realName
        self.ipAddress = ipAddress