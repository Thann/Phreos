#!/usr/bin/python2

import sys
import socket

version = "0.0.1"
port = 2308
serverAddress = "127.0.0.1"

class server_connection:
	def __init__(self):
		self.jobs = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(3)
		try: 
			self.sock.connect((serverAddress , port))
		except Exception as x:
			print "Error: Could not connect to server."
			sys.exit(1)
		
	def auth_user(self, user, passwd):
		self.sock.send("authuser="+user+":"+passwd+"~")
		string = self.sock.recv(1024)
		return True if string == "success" else False
	
	def query_printers(self):
		self.sock.send("request_list")
		self.jobs = []
		string = ""
		while(True):
			string = self.sock.recv(1024)
			if string == "done":
				break
			print "receivedQQ: ", string
			self.sock.send("next")
			self.jobs.append(string.split(";"))
		return self.jobs
		
	def release_job(self, num):
		if num >= len(self.jobs):
			print "ERROR: Bad Job number!"
			return False
		num = self.jobs[num][3]
		self.sock.send("release="+str(num))
		string = self.sock.recv(1024)
		return True if string == "success" else False

	def cancel_job(self, num):
		if num >= len(self.jobs):
			print "ERROR: Bad Job number!"
			return False
		num = self.jobs[num][3]
		self.sock.send("cancel="+str(num))
		string = self.sock.recv(1024)
		return True if string == "success" else False
	
	def close(self):
		#self.sock.send("kill")
		self.sock.close()

def main_simple_CLI():
	conn = server_connection()
	conn.auth_user("jon","tester")
	printer_list = conn.query_printers()
	for p in printer_list:
		print p
	#~ print printer_list
	
	print "print which one:"
	sin = int(sys.stdin.readline())-1
	
	#ret = conn.release_job(sin)
	ret = conn.cancel_job(sin)
	print "success?",ret

	conn.close()
	

if __name__ == "__main__":
	main_simple_CLI()
