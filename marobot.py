#-*- coding: utf-8 -*-

import socket, ssl
from setting import server, port, botname, botnick
from ircmessage import IRCMessage
from work import Work, init_db
from sqlalchemy import exc
import re


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
        print message

        if message.msgType == 'INVITE':
            joinchan(message.channel)
            sendmsg(message.channel, '안녕하세요, 업무 봇입니다')
            sendmsg(message.channel, '업무 추가/제거는 주인만 가능하고 열람은 자유입니다')

        elif message.msgType == 'MODE':
            if message.msg == u'+o 업무봇':
                sendmsg(message.channel, '감사합니다 :)')
            if message.msg == u'-o 업무봇':
                sendmsg(message.channel, '......')

        elif message.msgType == 'PRIVMSG':
            parse = re.match(ur'업무봇\s+조회\s*(?P<limit>전체|[0-9]+)?', message.msg)
            if parse:
                worklist = dao.query(Work).filter(Work.done == False).order_by(Work.due)
                if worklist.count() == 0:
                    sendmsg(message.channel, '남은 할 일이 없습니다')
                else:
                    sendmsg(message.channel, '할 일 목록 :')
                    limit = 5
                    if parse.group('limit') == u'전체':
                        limit = None
                    elif parse.group('limit') != None:
                        limit = int(parse.group('limit').decode('utf-8'))
                    for work in worklist[:limit]:
                        sendmsg(message.channel, '%s' % work)
            if re.match(ur'업무봇\s+(추가|제거|삭제|변경)\s*(.*)', message.msg):
                if message.sender != 'lastone81@175.197.23.22':
                    sendmsg(message.channel, '봇 주인만 업무 관리를 할 수 있습니다')
                else:
                    work_pattern = re.compile(ur'''
                        (?P<due_day>
                                ((다+음|이번)주\s+[월화수목금토일]요일)
                            |   (오늘|내일|모레|\d+일\s*후)
                            |   ((\d+월\s*)?\d+일)
                        )?\s*
                        (?P<due_time>
                                (\d+시\s*((\d+분)|반)?)
                        )?\s*
                        (?P<title>.*)
                        ''', re.VERBOSE)

                    parse = re.match(ur'업무봇\s+추가\s+(?P<content>.*)', message.msg)
                    if parse:
                        work_parse = work_pattern.match(parse.group('content'))
                        print work_parse.group('title')
                        print work_parse.group('due_day')
                        print work_parse.group('due_time')
                        if work_parse:
                            newWork = Work(work_parse.group('title'), work_parse.group('due_day'), work_parse.group('due_time'))
                            dao.add(newWork)
                            try:
                                dao.commit()
                            except exc.SQLAlchemyError:
                                sendmsg(message.channel, '이미 존재하는 업무입니다')
                                dao.rollback()
                            else:
                                sendmsg(message.channel, '%s 추가되었습니다' % newWork)

                    parse = re.match(ur'업무봇\s+(제거|삭제)\s+(?P<content>.*)', message.msg)
                    if parse:
                        work = dao.query(Work).filter(Work.name == parse.group('content'))
                        dao.delete(work)
                        dao.commit()
                        sendmsg(message.channel, '%s 제거되었습니다' % work)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, port))
ircsock = ssl.wrap_socket(s)
ircsock.send('USER ' + (botname + ' ') * 3 + ':' + botnick + '\n') # user authentication
ircsock.send('NICK '+ botnick +'\n')


if __name__ == '__main__':
    init_db()
    from work import dao
    run_bot()
