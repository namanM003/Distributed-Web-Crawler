#Code to extract headers from HTTP Response
import urllib.request
import datetime
import sys
import socket
import _thread
from threading import Thread, Lock
from threading import Condition
import pickle as pickle
queue = []
condition = Condition()

#Function to send client response to server
def server_send(response):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10000)
        
        #print >>sys.stderr, 'starting up on %s port %s' % client_address
        
        sock.connect(server_address)  
        data_string = pickle.dumps(response, -1)
        print("Final send to the server ")
        sock.sendall(data_string)
    finally:
            #print >>sys.stderr, 'closing socket'
            sock.close()


def client_listen():                                         ### As well as producer code here
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_address = ('localhost', int(sys.argv[1]))
    #print >>sys.stderr, 'starting up on %s port %s' % client_address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(client_address)
    # Listen for incoming connections
    sock.listen(10)
    dict_response = dict()
    while True:
        connection, server_address = sock.accept()
        try:
            #print >>sys.stderr, 'connection from', server_address  
            # Receive the data in small chunks and retransmit it
          
            data = connection.recv(10000)
           
            request = pickle.loads(data)
            condition.acquire()
            
            length = len(queue)
            queue.append(request)
            print("Produced", request)
            
            if length == 0:                                   ### Taking the length just before adding the elements 
              print("Notifying")
              condition.notify()
            
            condition.release()
            
 
        finally:
            # Clean up the connection
            connection.close()
        

class ConsumerThread(Thread):
    def run(self):
        global queue
        while True:
            dict_response = dict()
            condition.acquire()
            if not queue:
                print("Nothing in queue, consumer is waiting")
                condition.wait()
                print("Producer added something to queue and notified the consumer")
            request = queue.pop(0)
            opener = getUserAgent()
            listObjs = []
            for url in request:
              obj = sendRequest(opener,url)
              if obj!=None:
                listObjs.append(obj)
            if len(obj)!=0:
              result = headerCount ()
              result.accumulateResults(listObjs)
            else:
              print("Consumed but didnt get relevant results")
              continue
            print("Consumed" + str (request.ip_addr))
            #logger.info(" Got Request from Server IP = " + str(request.ip_addr) + " Type = " + str(request.type))
            condition.release()
            #print >>sys.stderr, 'received "%s"' % request.ip_addr
            print("Sending to the server")
            server_send(result)  
################################################################################
logDir = "./"
logFilePath = ""

class UrlHeader(object):
  def __init__(self,url):
    self.redirectFlag = False
    self.url = url.lower()
    self.headers = {}
    self.redirectUrl = ""

class headerCount(object):
  def __init__(self):
    self.standardHeaders={}
    self.otherHeaders={}
    self.exceptions={}

    self.redirectCount =0
    self.stdHeaderNames =set( ['x-frame-options','strict-transport-security','x-content-type-options','content-type','x-xss-protection','cache-control','pragma','expires','x-permitted-cross-domain-policies','content-security-policy'])

    self.countInit()
    self.exceptionsInit()

  def countInit(self):
    for name in self.stdHeaderNames:
      self.standardHeaders[name]=0

  def exceptionsInit(self):  
    for name in self.stdHeaderNames:
      self.exceptions[name]=[]

  def accumulateResults(self,UrlHeaderList):
    for obj in UrlHeaderList:
      if obj.redirectFlag:
        if 'http' in obj.url and 'https' in obj.redirectUrl:
          self.redirectCount +=1

      stdHeaderNamesExist = set()
 
      for key in obj.headers.keys():
        headerName = key.lower()
        if headerName in self.standardHeaders:
          stdHeaderNamesExist.add(headerName)
          self.standardHeaders[headerName]+=1
        else:
          if headerName in self.otherHeaders:
            self.otherHeaders[headerName]+=1
          else:
            self.otherHeaders[headerName]=1

      for name in self.stdHeaderNames-stdHeaderNamesExist:
        self.exceptions[name].append(obj.url)

  def __str__(self):
    resultString=[]
    resultString.append("~~~~~~~~~~~~~~~STANDARD HEADERS~~~~~~~~~~~~~~")
    resultString.append(str(self.standardHeaders))
    resultString.append("~~~~~~~~~~~~~~~OTHER HEADERS ~~~~~~~~~~~~~~~~~~~")
    resultString.append(str(self.otherHeaders))
    resultString.append("~~~~~~~~~~~~~~~EXCEPTIONS ~~~~~~~~~~~~~~~~~~~~")
    resultString.append(str(self.exceptions))
    resultString.append("~~~~~~~~~~~~~~~~REDIRECTS ~~~~~~~~~~~~~~~~~~~")
    resultString.append(str(self.redirectCount))
    return '\n'.join(resultString)

def getUserAgent():
  opener = urllib.request.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  return opener

def sendRequest(opener,url):
  fp = open(logFilePath,"a")
  try:
    infile = opener.open(url)
  except Exception as e:
    errorMessage = str(datetime.datetime.now())+"--"+e.message+"\n"
    fp.write(errorMessage)
    return None

  headerObj  = UrlHeader(url)
  redirectUrl = infile.geturl()
  if redirectUrl!=url:
    headerObj.redirectFlag = True
    headerObj.redirectUrl = redirectUrl.lower()

  for k,v in infile.headers._headers:
    headerObj.headers[k]=v
  return headerObj


    
    
    
    
    
if __name__=="__main__":
  if len(sys.argv)<3:
    print("Error, Usage: extract_headers.py clientId")
    sys.exit(2)

  logFilePath = "logClient%s"%sys.argv[2]
  
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_address = ('localhost', int(sys.argv[1]))
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(client_address)
  # Connect the socket to the port where the server is listening
  server_address = ('localhost', 10000)
  #print >>sys.stderr, 'connecting to %s port %s' % server_address
  sock.connect(server_address)
  try:
    _thread.start_new_thread(client_listen, ())                                ## Producer thread !!
    ConsumerThread().start()

  except:
    print("unable to start thread")
  while 1:
    pass


