#!/usr/bin/python2

import sys
import socket

version = "0.0.1"
port = 2308
serverAddress = "127.0.0.1"

class server_connection:
	def __init__(self):
		self.sock = socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		self.sock.settimeout(3)
		try: 
			self.sock.connect((serverAddress , port))
		except Exception as x:
			print "Error: Could not connect to server."
		
	def auth_user(self, user, passwd):
		self.sock.send("authuser="+username+":"+passwd+"~")
	
	def query_printers(self):
		return ["NOT YET IMPLEMENTED"]
		
	def release_job(self, num):
		pass
	def cancel_job(self, num):
		pass

def main_simple_CLI():
	print "print which one:"
	
	con = cups_LP()
	con.auth_user("jon","tester")
	printer_list = con.query_printers()
	for p in printer_list:
		print p
	
	print "print which one:"
	sin = int(sys.stdin.readline())-1
	
	backend.release_job(sin)

if __name__ == "__main__":
	main_simple_CLI()
