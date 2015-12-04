#-*- coding: utf-8 -*-
import time
import os
import sys
import re
import locale
import curses
import datetime
from stat import *

TITLEHEIGHT = 4
DATELEN = 6 
HLEN = 10
WLEN = 10

class Message:
	def __init__(self, hostname, tword, message, start):
		self.hostname = hostname
		self.tword = tword
		self.message = message
		self.date = datetime.datetime.today()
		self.start = start

class HOST:
	def __init__(self, hostname, filename):
		self.hostname = hostname 
		self.file = open(filename,'r')
    		st_results = os.stat(filename)
    		st_size = st_results[ST_SIZE]
    		self.file.seek(st_size)
		self.fpos = self.file.tell()
	
	def check(self, targetwords):
		messages = []
		self.fpos = self.file.tell()
        	line = self.file.readline()
		line = line.rstrip("\n")
        	if not line:
            		self.file.seek(self.fpos)
        	else:
			for tword in targetwords: 
				if re.search(tword, line, flags=re.IGNORECASE) != None: 
					messages.append(Message(self.hostname, tword, line, re.search(tword, line, flags = re.IGNORECASE).start()))
					break
		messages.reverse()
		return messages


class Monitor:
	def __init__(self, configfile):
		self.targetwords, self.targethosts = self.gettarget(configfile)
		self.cur = CursesCtrl()

	def gettarget(self, confifile):
		words = []
		hosts = []
		for line in open(configfile, 'r'):
			if(len(line) <= 2):
				continue
			line = line.rstrip("\n")
			if("," in line):
				words = line.split(",")
			else:
				hosts.append(HOST(line.split(" ")[0], line.split(" ")[1]))
		return words, hosts

	def run(self):
		messages = []
		while True:
			for host in self.targethosts:
				messages =  host.check(self.targetwords) + messages
				self.cur.update_info(messages)
				time.sleep(0.1)


class CursesCtrl:
	def __init__(self):
		self.scr = curses.initscr() 
		curses.noecho()

	def erase_win(self):
		space = ""
		for i in range(self.x):
			space += " "
		for i in range(self.y - 1):
			self.scr.addstr(i, 0, space)

	def write_title(self):
		self.scr.addstr(TITLEHEIGHT - 1, 0, "DATE")
		if(self.x > DATELEN-2):
			self.scr.addstr(TITLEHEIGHT - 1, DATELEN, "HOSTNAME")
		if(self.x > 10-2):
			self.scr.addstr(TITLEHEIGHT - 1, DATELEN + HLEN, "WORD")
		if(self.x > 20-2):
			self.scr.addstr(TITLEHEIGHT - 1, DATELEN + HLEN + WLEN, "MESSAGE")

	def write_message(self, messages):
		yid = TITLEHEIGHT
	 	for message in messages:
			self.scr.addstr(yid, 0, "%s:%s" %(message.date.hour,  message.date.minute))
                        self.scr.addstr(yid, DATELEN, message.hostname)
                        self.scr.addstr(yid, DATELEN + HLEN, message.tword)
			if (yid + int(len(message.message)/self.x+TITLEHEIGHT) >= self.y-1):
				break
			mh = 0
			while True:
				if (len(message.message) < (mh+1)*(self.x - HLEN - WLEN - DATELEN)):
					self.scr.addstr(yid, DATELEN + HLEN + WLEN, message.message[mh*(self.x-HLEN - WLEN - DATELEN):])
					yid += 1
					break
				else:
					self.scr.addstr(yid, DATELEN + HLEN + WLEN, message.message[mh*(self.x-HLEN - WLEN - DATELEN):(mh+1)*(self.x-HLEN -WLEN - DATELEN)])
				yid += 1
				mh += 1

	def update_info(self, messages):
		self.y, self.x = self.scr.getmaxyx()
		self.erase_win()
		try:
			self.write_title()
			self.write_message(messages)
		except Exception as e:
			pass
		self.scr.move(0,0)
		self.scr.refresh()

if __name__ == '__main__':
    configfile = sys.argv[1]
    Monitor(configfile).run()

