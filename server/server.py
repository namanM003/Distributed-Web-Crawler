from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import socket

PORT_NUMBER = 8008
clients_list = list()

class myHandler(BaseHTTPRequestHandler):
        def do_GET(self):
                if self.path=="/":
                        self.path = "/index.html"
                else:
                        self.path = "/index.html"
                try:
                        if self.path.endswith(".html"):
                                mimetype = 'text/html'
                                sendReply = True
                        
                        if sendReply:
                                f = open(curdir + sep + self.path)
                                self.send_response(200)
                                self.send_header('Content-type',mimetype)
                                self.end_headers()
                                self.wfile.write(f.read())
                                f.close()
                        return
                except IOError:
                                self.send_error(404, " File not found %s " % self.path)
	def do_POST(self):
		'''
		Define here for POST. Parsing of fields
		'''
try:
	server = HTTPServer(('',8008), myHandler)
	print "Server Started on port ", PORT_NUMBER
	server.serve_forever()
	
except KeyboardInterrupt:
	print "Keyboard Interrupt Encountered. Shutting down webserver"
	server.socket.close();

'''
class myHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path=="/":
			self.path = "/index.html"
		else:
			self.path = "/index.html"
		try:
			if self.path.endswith(".html"):
				mimetype = 'text/html'
				sendReply = True
			
			if sendReply:
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type',mimetype)
                                self.end_headers()
                                self.wfile.write(f.read())
                                f.close()
			return
		except IOError:
				self.send_error(404, " File not found %s " % self.path)
'''
