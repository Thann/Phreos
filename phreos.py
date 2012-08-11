#!/usr/bin/python2

import sys
import subprocess 

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
			spool_num = int(lpq[index][2])
			spool_num = "d%05.0f-001" % (spool_num)
			page_num = subprocess.Popen("pkpgcounter "+self.spool+spool_num, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			page_num = int(page_num.stdout.readline())
			lpq[index].insert(1,page_num)
			lpq[index] = lpq[index][:-2]
		self.lpq = lpq
		return self.lpq

	def release_job(self, num):
		print "NUM = "+str(num)
		if num >= len(self.lpq) or num < 0 :
			print "ERROR: not a valid job number!"
			return
		print "releaseing job num "+self.lpq[num][3]
		#subprocess.Popen("lp -i "+self.printer+"-"+self.lpq[num][3]+" -H immediate", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
	def cancel_job(self, num):
		print "NUM = "+str(num)
		if num >= len(self.lpq) or num < 0 :
			print "ERROR: not a valid job number!"
			return
		print "canceling job num "+self.lpq[num][3]
		subprocess.Popen("cancel "+self.printer+" "+self.lpq[num][3], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		

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
