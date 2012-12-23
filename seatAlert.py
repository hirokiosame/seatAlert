'''
Copyright (C) 2012 by Hiroki Osame

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import os, sys, re, time, smtplib, email, getpass, urllib, urllib2, cookielib

class seatAlert:
	def __init__(self):

		#Inquire Credentials
		self.buUn = urllib.quote_plus(raw_input("BU Username: "))
		self.buPw = urllib.quote_plus(getpass.getpass("BU Password: "))

		#Inquire Courses
		self.courses = []
		url  = "https://www.bu.edu/link/bin/uiscgi_studentlink.pl/?ModuleName=reg%2Fadd%2Fbrowse_schedule.pl&SearchOptionCd=N&KeySem=20134&CurrentCoreInd=N"

		print("Enter your courses in format:\n\tCollege_Department_Course_Section\n\teg. CAS_CS_330_A1");
		for c in range(1, 6):
			course = raw_input("Course "+str(c)+": ")
			if course != "":
				self.courses.append(course)
				crse = course.split("_")
				if len(crse)!=4:
					sys.exit("Error: You must enter courses in the required format!")

				url += "&College"+str(c)+"="+crse[0]
				url += "&Dept"+str(c)+"="+crse[1]
				url += "&Course"+str(c)+"="+crse[2]
				url += "&Section"+str(c)+"="+crse[3]
				print("\tAdded: "+course)
			else:
				break

		if len(self.courses)==0:
			sys.exit("Error: You must enter at least one course to watch!")


		#Prepare Session
		self.cj = cookielib.MozillaCookieJar()

		#Make Connection
		connection = self.httpReq("http://cs-people.bu.edu/hirokio/cafbda07738c5dd81c7729a172bf05f4")
		if connection != "1":
			sys.exit("Error: Cannot connect to the BU server!")		

		#Request
		while(1):
			self.checkData(self.httpReq(url))
			time.sleep(60)


	def login(self):
		print "Logging in..."
		attempt =	self.httpReq(
						"https://weblogin.bu.edu//web@login3",
						"https://weblogin.bu.edu//web@login3",
						"p=&act=up&js=yes&jserror=&c2f=&r2f=&user="+self.buUn+"&pw2="+self.buPw+"&pw="+self.buPw
					)
		if re.search("Weblogin complete; waiting for application.", attempt):
			return "Success!"
		else:
			sys.exit("Error: Login Failed")

	def checkData(self, source):
		if re.search("Weblogin Browser Check", source):
			print self.login()
		else:
			match = re.findall("\<td\>\s+(\d+)\<\/td\>", source)
			print( time.asctime(time.localtime(time.time())) )
			for i, s in enumerate(match):
				print "\t"+self.courses[i]+" has "+s+" seat(s)"
				if 0<int(s) :
					self.alert(self.courses[i]+" has "+s+" seat(s)")

	def alert(self, message):
		msg = email.MIMEMultipart.MIMEMultipart()

		msg['From'] = self.buUn+"@bu.edu"
		msg['To'] = self.buUn+"@bu.edu"
		msg['Subject'] = message
		msg.attach(email.MIMEText.MIMEText(message))

		mailServer = smtplib.SMTP("smtp.gmail.com", 587)
		mailServer.starttls()
		mailServer.login(self.buUn+"@bu.edu", self.buPw)
		mailServer.sendmail(self.buUn+"@bu.edu", msg['To'], msg.as_string())
		mailServer.close()

	def httpReq(self, url, referer=False, post=None):
		handlers = [
			urllib2.HTTPHandler(),
			urllib2.HTTPSHandler(),
			urllib2.HTTPCookieProcessor(self.cj),
		]

		opener = urllib2.build_opener(*handlers)
		urllib2.install_opener(opener)

		#Build Request
		req = urllib2.Request(url, post)

		#Set User Agent
		req.add_header('User-Agent', "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/528.8 (KHTML, like Gecko) Chrome/2.0.156.0 Safari/528.8")

		#Add Referer
		if referer!=False:
			req.add_header('Referer', referer)

		#Add Post
		if post!=None:
			req.add_header('Connection', 'keep-alive')
			req.add_header('Content-type', 'application/x-www-form-urlencoded')

		handle = None

		try:
			handle = urllib2.urlopen(req)
		except IOError, e:
			print 'We failed to open "%s".' % url
			if hasattr(e, 'code'):
				print 'Error code - %s.' % e.code
		else:
			if 'handle' != None:
				try:
					source = handle.read()
				except Exception as e:
					print("Error! "+str(e))
				else:
					return source

seatAlert();