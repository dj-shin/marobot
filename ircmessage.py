#-*- coding: utf-8 -*-

class IRCMessage():
    msgType = None
    sender = None
    channel = None
    msg = None

    def __init__(self, origMessage):
        self.msgType = origMessage.split()[1]
        if self.msgType == 'PRIVMSG':
            self.sender = origMessage.split()[0].split('~')[1]
            self.channel = origMessage.split()[2]
            self.msg = origMessage[ origMessage[2:].find(':') + 3 : ]
            print self.msg
        elif self.msgType == 'MODE':
            self.sender = origMessage.split()[0].split('~')[1]
            self.channel = origMessage.split()[2]
            self.msg = 'OP' if origMessage.split()[3] == '+o' else 'DEOP'
        elif self.msgType == 'KICK':
            self.sender = origMessage.split()[0].split('~')[1]
            self.channel = origMessage.split()[2]
        elif self.msgType == 'JOIN':
            self.sender = origMessage.split()[0].split('~')[1]
            self.channel = origMessage.split()[2]
        elif self.msgType == 'INVITE':
            self.sender = origMessage.split()[0].split('~')[1]
            self.channel = origMessage.split()[3][1:]
        else:
            pass
