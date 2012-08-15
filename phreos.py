#!/usr/bin/python2

import os
import sys
import socket
import datetime
import threading
import subprocess
import ConfigParser

version = "0.0.1"

global config
config = ConfigParser.RawConfigParser()
confPath = os.path.abspath(os.path.dirname(__file__)+"/phreos-server.conf") #location of this program
config.read(confPath)

class cups_LP:
	def __init__(self):
		#Default Config Values
		self.spool = "/var/spool/cups/"
		self.printers = "Virtual_PDF_Printer"

		try:
			spool = config.get("CupsConf","SpoolPath")
			printer = config.get("CupsConf","Printers")
		except Exception as x:
			print "Error loading vals from config file:",x
			print "Making a fresh config file with default values!"

			if not config.has_section("CupsConf"):
				config.add_section("CupsConf")

			config.set("CupsConf","SpoolPath",self.spool)
			config.set("CupsConf","Printers",self.printers)

			with open(confPath,'w') as configFile:
				config.write(configFile)

		self.lpq = []

	#Translates cups-job-num to lpq-index-num
	def _get_job_num(self, num):
		for index, job in enumerate(self.lpq):
			if job[3] == str(num) :
				return index

		print "ERROR: not a valid job number!"
		return -1

	def query_printers(self):
		lpq = subprocess.Popen("lpq -P "+self.printers, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lpq = lpq.stdout.readlines()[2:]

		for index in xrange(len(lpq)):
			lpq[index] = lpq[index].strip().split()
			spoolNum = int(lpq[index][2])
			spoolNum = "d%05.0f-001" % (spoolNum)
			pageNum = subprocess.Popen("pkpgcounter "+self.spool+spoolNum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			pageNum = int(pageNum.stdout.readline())
			lpq[index].insert(1,str(pageNum))
			lpq[index] = lpq[index][:-2]
		self.lpq = lpq
		return self.lpq

	def release_job(self, num):
		num = self._get_job_num(num)
		if num < 0:
			return False
		print "releaseing job num "+self.lpq[num][3]
		#subprocess.Popen("lp -i "+self.printers+"-"+self.lpq[num][3]+" -H immediate", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True

	def cancel_job(self, num):
		num = self._get_job_num(num)
		if num < 0:
			return False
		print "canceling job num "+self.lpq[num][3]
		#subprocess.Popen("cancel "+self.printers+" "+self.lpq[num][3], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True

class logger:
	def __init__(self, filename):
		self.logFile = open(filename,'a')

	def add(self, entry):
		self.logFile.write(str(datetime.datetime.today())+" : "+entry+"\n")

class service:
	def __init__(self):
		self.port = 2308
		self.maxClients = 100
		logPath = os.path.abspath(os.path.dirname(__file__)+"/phreos_print.log")

		try:
			self.port = config.getint("PhreosConf","Port")
			self.maxClients = config.getint("PhreosConf","MaxClients")
			logPath = config.get("PhreosConf","LogPath")
		except Exception as x:
			print "Error loading vals from config file:",x
			print "Making a fresh config file with default values!"

			if not config.has_section("PhreosConf"):
				config.add_section("PhreosConf")

			config.set("PhreosConf","Port",self.port)
			config.set("PhreosConf","MaxClients",self.maxClients)
			config.set("PhreosConf","LogPath",logPath)

			with open(confPath,'w') as configFile:
				config.write(configFile)

		self.log = logger(logPath)
		self.backend = cups_LP()

	def handleClient(self, clientSock, address ):
		string = ""
		authInfo = None
		while (string != "kill"):
			try:
				string = clientSock.recv(1024)
				print "received: >"+string+"<"

				if (string[:9] == "authuser="):
					authInfo = dict(zip(["user","passwd"],string[9:].split(":")))
					print authInfo
					clientSock.send("success")

				elif (string == "request_list"):
					jobs = self.backend.query_printers()
					for line in jobs:
						print "LINE:",line
						s = ";".join(line)
						clientSock.send(s)
						clientSock.recv(1024)
					clientSock.send("done")

				elif (string[:8] == "release="):
					if len(authInfo):
						r = self.backend.release_job(int(string[8:]))
						if r:
							self.log.add(authInfo["user"]+" printed job# "+string[8:])
							clientSock.send("success")
						else:
							print "ERROR: Unable to release job."
							clientSock.send("ERROR")
					else:
						print "ERROR: Tried to print before Auth."
						break

				elif (string[:7] == "cancel="):
					if len(authInfo):
						r = self.backend.cancel_job(int(string[7:]))
						if r:
							self.log.add(authInfo["user"]+" canceled job# "+string[7:])
							clientSock.send("success")
						else:
							print "ERROR: Unable to cancel job."
							clientSock.send("ERROR")
					else:
						print "ERROR: Tried to cancel before Auth."
						break

				else:
					print "received bad string: "+string
					break

			except:
				print "ERROR:"
				break

		##Gracefully disconnect

	def serviceLoop(self, servSock):
		while 1:
			try:
				print "Waiting for next client..."
				(clientSock, address) = servSock.accept()
				print "Client Connected, Creating Thread"
				t = threading.Thread(target=self.handleClient, args=(clientSock, address))
				t.daemon = True
				t.start()
			except:
				print "ERROR!\nExiting Service."
				servSock.shutdown(socket.SHUT_RDWR)
				servSock.close()
				break

	def start(self):
		print "Starting Server ("+version+")"
		servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		servSock.bind(('', self.port))
		servSock.listen(self.maxClients)
		self.serviceLoop(servSock)

if __name__ == "__main__":
	serv = service()
	serv.start()
