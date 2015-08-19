#-*- coding: utf-8 -*-

import socket, ssl
from setting import server, port, botname, botnick
from ircmessage import IRCMessage
from work import Work, dao, init_db


def ping():
    ircsock.send('PONG :pingis\n')


def sendmsg(chan, msg):
    ircsock.send('PRIVMSG ' + chan + ' :' + msg + '\n') 


def joinchan(chan):
    ircsock.send('JOIN '+ chan +'\n')


def partchan(chan):
    ircsock.send('PART '+ chan +'\n')


def chanlist():
    ircsock.send('WHOIS '+ botnick +'\n')


def run_bot():
    while 1:
        ircmsg = ircsock.recv(8192)
        ircmsg = ircmsg.strip('\n\r')
        # ping
        if ircmsg.find('PING :') != -1:
            ping()
            continue

        print
        print ircmsg

        if ircmsg[0] != ':':
            continue

        message = IRCMessage(ircmsg)

        if message.msgType == 'INVITE':
            joinchan(message.channel)
            sendmsg(message.channel, '안녕하세요, 업무 봇입니다')
            sendmsg(message.channel, '업무 추가/제거는 주인만 가능하고 열람은 자유입니다')

        elif message.msgType == 'MODE':
            if message.msg == 'OP':
                sendmsg(message.channel, '감사합니다 :)')

        elif message.msgType == 'PRIVMSG':
            if message.msg[:9] == '업무봇':
                if message.msg[10:16] == '조회':
                    # 업무 조회
                    worklist = dao.query(Work).filter(Work.done == False).order_by(Work.due)
                    if worklist.count() == 0:
                        sendmsg(message.channel, '남은 할 일이 없습니다')
                    else:
                        sendmsg(message.channel, '할 일 목록 :')
                        for work in worklist:
                            sendmsg(message.channel, '%s' % work)
                if message.sender == 'lastone81@175.197.23.22':
                    if message.msg[10:16] == '추가':
                        # 업무 추가
                        try:
                            message.msg[17:].split()[1]
                        except IndexError:
                            newWork = Work(message.msg[17:])
                        else:
                            newWork = Work(message.msg[17:message.msg.rfind(' ')], message.msg[message.msg.rfind(' ') + 1:])
                        dao.add(newWork)
                        dao.commit()
                        sendmsg(message.channel, '%s 추가되었습니다' % newWork)
                    elif message.msg[10:16] == '제거' or message.msg[10:16] == '삭제':
                        # 업무 제거
                        for work in dao.query(Work).filter(Work.name == message.msg[17:]):
                            dao.delete(work)
                            dao.commit()
                            sendmsg(message.channel, '%s 제거되었습니다' % work)
                else:
                    sendmsg(message.channel, '봇 주인만 업무 관리를 할 수 있습니다')

        else:
            pass


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, port))
ircsock = ssl.wrap_socket(s)
ircsock.send('USER ' + (botname + ' ') * 3 + ':' + botnick + '\n') # user authentication
ircsock.send('NICK '+ botnick +'\n')


if __name__ == '__main__':
    init_db()
    run_bot()
