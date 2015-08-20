#-*- coding: utf-8 -*-
import re

class IRCMessage():
    msgType = None
    sender = None
    channel = None
    msg = None
    target = None

    def __init__(self, origMessage):
        parse = re.search(r':.*!~(\S+)\s+(\S+)\s+(.*?)\s+:?(.*)', origMessage)
        if parse:
            self.sender = parse.group(1)
            self.msgType = parse.group(2)
            self.channel = parse.group(3)
            self.msg = parse.group(4)
            if self.msg:
                self.msg = self.msg.decode('utf-8')
            if self.msgType == 'INVITE':
                self.channel = parse.group(4)
        else:
            pass

    def __repr__(self):
        msg = self.msg
        if msg:
            msg = msg.encode('utf-8')
        return '<IRCMessage : %s %s %s %s %s>' % (self.msgType, self.sender, self.channel, msg, self.target)
