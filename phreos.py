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
	
	def query_printers(self):
		lpq = subprocess.Popen("lpq -P "+self.printer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lpq = lpq.stdout.readlines()[2:]

		for index in xrange(len(lpq)):
			lpq[index] = lpq[index].strip().split()
			spoolNum = int(lpq[index][2])
			spoolNum = "d%05.0f-001" % (spoolNum)
			pageNum = subprocess.Popen("pkpgcounter "+self.spool+spoolNum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			pageNum = int(pageNum.stdout.readline())
			lpq[index].insert(1,pageNum)
			lpq[index] = lpq[index][:-2]
		self.lpq = lpq
		return self.lpq

	def release_job(self, num):
		print "NUM = "+str(num)
		if num >= len(self.lpq) or num < 0 :
			print "ERROR: not a valid job number!"
			return False
		print "releaseing job num "+self.lpq[num][3]
		subprocess.Popen("lp -i "+self.printer+"-"+self.lpq[num][3]+" -H immediate", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True
		
	def cancel_job(self, num):
		print "NUM = "+str(num)
		if num >= len(self.lpq) or num < 0 :
			print "ERROR: not a valid job number!"
			return False
		print "canceling job num "+self.lpq[num][3]
		subprocess.Popen("cancel "+self.printer+" "+self.lpq[num][3], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		return True
		
class logger:
	def __init__(self, filename):
		self.logFile = open(filename,'a')
	
	def add(self, entry):
		logFile.write(datetime.datetime+" : "+entry)
		
class service:
	def __init__(self):
		backend = cups_LP()
		log = logger("phreos_print.log")		
		
	def handleClient( clientSock, address ):
		authInfo = []
		while (string != "kill"):
			try:
				string = clientSock.recv(1024)
				print "received: ", string
				
				if (string[:9] == "authuser=")
					authInfo = string[9:].split(":")
				
				elif (string == "request_list"):
					jobs = backend.query_printers()
					for line in jobs
						s = ";".join(line)
						clientSock.send(s)
					clientSock.send("done")
					
				elif (string[:8] == "release="):
					if len(authInfo):
						backend.release_job(int(string[8:]))
						log.add(user+" printed job# "+string[8:])
					else:
						print "ERROR: tried to print before Auth."
						string = "kill"
				
				else:
					print "received bad string: "+string
					string = "kill"
			except Exception as x:
				print "ERROR: "+x
				string = "kill"
		
		##Gracefully disconnect
	
	def serviceLoop(servSock):
		while 1:
			try:
				print "Waiting for next client..."
				(clientSock, address) = servSock.accept()
				print "Client Connected, Creating Thread"
				threading.Thread(target=handleClient, args=(clientSock, address)).start()
			except Exception as x:
				print "Exiting Service."
				servSock.close()
				break	
		
	def start(self):
		print "Starting Server ("+version+")"
		servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		servSock.bind(('', port))
		servSock.listen(maxClients)
		serviceLoop(servSock)

def main_simple_CLI():
	backend = cups_LP()
	printer_list = backend.query_printers()
	for p in printer_list:
		print p
	
	print "print which one:"
	sin = int(sys.stdin.readline())-1
	
	backend.release_job(sin)

if __name__ == "__main__":
	main_simple_CLI()
