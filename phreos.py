#!/usr/bin/python2

import sys
import socket
import datetime
import threading
import subprocess 

version = "0.0.1"
#version = version.split(".")
port = 2308
maxClients = 100

class cups_LP:
	def __init__(self):
		#Vars
		self.spool = "/var/spool/cups/"
		self.printer = "Virtual_PDF_Printer"
		self.lpq = []
		
	#Translates cups-job-num to lpq-index-num
	def _get_job_num(self, num):
		for index, job in enumerate(self.lpq):
			if job[3] == str(num) :
				return index

		print "ERROR: not a valid job number!"
		return -1

	def query_printers(self):
		lpq = subprocess.Popen("lpq -P "+self.printer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
		#subprocess.Popen("lp -i "+self.printer+"-"+self.lpq[num][3]+" -H immediate", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True
		
	def cancel_job(self, num):
		num = self._get_job_num(num)
		if num < 0:
			return False
		print "canceling job num "+self.lpq[num][3]
		#subprocess.Popen("cancel "+self.printer+" "+self.lpq[num][3], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True
		
class logger:
	def __init__(self, filename):
		self.logFile = open(filename,'a')
	
	def add(self, entry):
		self.logFile.write(str(datetime.datetime.today())+" : "+entry+"\n")
		
class service:
	def __init__(self):
		self.backend = cups_LP()
		self.log = logger("phreos_print.log")		
		
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
					
			except Exception as x:
				print "ERROR:",x
				break
		
		##Gracefully disconnect

	def serviceLoop(self, servSock):
		while 1:
			try:
				print "Waiting for next client..."
				(clientSock, address) = servSock.accept()
				print "Client Connected, Creating Thread"
				threading.Thread(target=self.handleClient, args=(clientSock, address)).start()
			except Exception as x:
				print "ERROR:",x,"\nExiting Service."
				servSock.close()
				break	
		
	def start(self):
		print "Starting Server ("+version+")"
		servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		servSock.bind(('', port))
		servSock.listen(maxClients)
		self.serviceLoop(servSock)

def main_simple_CLI():
	backend = cups_LP()
	printer_list = backend.query_printers()
	for p in printer_list:
		print p
	
	print "print which one:"
	sin = int(sys.stdin.readline())-1
	
	backend.release_job(sin)

if __name__ == "__main__":
	#main_simple_CLI()
	serv = service()
	serv.start()
