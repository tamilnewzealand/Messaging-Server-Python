
class classMessage:
    def __init__ (self, fromUser, toUser, time_stamp, status, message='', attachment='') :
        self.fromUser = fromUser
        self.toUser = toUser
        self.time_stamp = time_stamp
        self.status = status
        self.message = message
        self.attachment = attachment

class peerList :
    def __init__ (self, userID, realName, ipAddress) :
        self.userID = userID
        self.realName = realName
        self.ipAddress = ipAddress