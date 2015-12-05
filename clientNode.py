#Code to extract headers from HTTP Response
import urllib2
import datetime
import sys
import socket
import thread
from threading import Thread, Lock
from threading import Condition
import cPickle as pickle
from bs4 import BeautifulSoup
import math
from collections import Counter

queue = []
condition = Condition()

#Function to send client response to server
def server_send(response):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        print "connected to server" 
        #print >>sys.stderr, 'starting up on %s port %s' % client_address
        
        sock.connect(server_address)  
        data_string = pickle.dumps(response, -1)
        print "Final send to the server"
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
              obj = UrlHeader(url)
              obj = obj.sendRequest(opener)

              if obj!=None:
                obj.checkForNonces()
                listObjs.append(obj)

            result = headerCount ()
            if len(listObjs)!=0:
              result.accumulateResults(listObjs)
            else:
              print("Consumed but didnt get relevant results")
            #print("Consumed" + str (request.ip_addr))
            #logger.info(" Got Request from Server IP = " + str(request.ip_addr) + " Type = " + str(request.type))
            condition.release()
            #print >>sys.stderr, 'received "%s"' % request.ip_addr
            print("Sending to the server")
            server_send(result)  
################################################################################
logDir = "./"
logFilePath = ""
entropyThreshold = 3.0

def entropy(s):
  p, lns = Counter(s), float(len(s))
  return -sum( count/lns * math.log(count/lns, 2) for count in p.values())


class UrlHeader(object):
  def __init__(self,url):
    self.redirectFlag = False
    self.url = url.strip().lower()
    self.headers = {}
    self.redirectUrl = ""
    self.requiredNonce = False
    self.nonceSatisfied = False
    self.infile  = None

  def sendRequest(self,opener):
    fp = open(logFilePath,"a")
    try:
      self.infile = opener.open(self.url)
    except Exception, e:
      errorMessage = str(datetime.datetime.now())+"--"+e.message+"\n"
      fp.write(errorMessage)
      return None

    self.redirectUrl = self.infile.geturl()
    if self.redirectUrl!=self.url:
      self.redirectFlag = True
      self.redirectUrl = self.redirectUrl.lower()

    self.headers = self.infile.headers.dict
    return self

  def checkForNonces(self):
    page = self.infile.read()
    soup = BeautifulSoup(page)
    listOfForms = soup.findAll('form')
    for form in listOfForms:
      self.requiredNonce = True
      inputTags  = form.findAll('input',type="hidden")
      for inputTag in inputTags:
        if inputTag.has_attr('value'):
          nonceValue = inputTag['value'].strip()
          entropyValue = entropy(nonceValue)
          if entropyValue>entropyThreshold:
            self.nonceSatisfied = True

  def checkAnticlickJacking(self):
    stdValues = ['sameorigin','deny','allow-from']
    headerValue = self.headers['x-frame-options'].strip().lower()
    return any(x in headerValue for x in stdValues)
  
  def checkSecureCookies(self):
    stdValues = ['httponly','secure']
    headerValue = self.headers['set-cookie'].strip().lower()
    return all(x in headerValue for x in stdValues)

  def checkStrictTransportPolicy(self):
    headerValue = self.headers['strict-transport-security'].strip().lower()

    if 'includesubdomains' not in headerValue:
      return False
    
    maxAgePresent = False
    values = headerValue.split(';')
    for val in values:
      val = val.strip()
      if 'max-age' in val:
        maxAgePresent = True
        numericValues = val.split('=')
        if len(numericValues)<2:
          return False
        
        try:
          seconds = float(numericValues[1].strip())
        except Exception,e:
          print "Not able to parse max-age in strict transport policy: ",e.message
          return False
        
        if seconds<=0:
          return False
        else:
          break
        

    return maxAgePresent 
  
  def checkContentSecurityPolicy(self):
    headerValue = self.headers['content-security-policy'].strip().lower()  
    print headerValue
    stdValues = ['none','self','https']

    values = headerValue.split(';')
    for val in values:
      if 'default-src' in val:
        return any(x in val for x in stdValues)
        
    return False          
        


class headerCount(object):
  def __init__(self):
    self.standardHeaders={}
    self.otherHeaders={}
    self.exceptions={}

    self.redirectCount =0
    self.stdHeaderNames =set( ['x-frame-options','strict-transport-security','x-content-type-options','content-type','x-xss-protection','cache-control','pragma','expires','x-permitted-cross-domain-policies','content-security-policy','set-cookie'])
    self.countNonces = 0
    self.noNoncesUrls = []


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

      if obj.requiredNonce:
        if obj.nonceSatisfied:
          self.countNonces+=1
        else:
          self.noNoncesUrls.append(obj.url)
        

      stdHeaderNamesExist = set()
      cookieRequired = False
 
      for key in obj.headers.keys():
        headerName = key.strip().lower()
        if headerName in self.standardHeaders:
          if headerName == 'x-frame-options':
            #check for anticlick jacking
            if not obj.checkAnticlickJacking():
              continue

          if headerName =='set-cookie':
            #check for secure cookies
            cookieRequired = True
            if not obj.checkSecureCookies():
              continue

          if headerName == 'strict-transport-security':
            #check for strict transport policy
            if not obj.checkStrictTransportPolicy():
              continue

          if headerName == 'content-security-policy':
            #check for content security policy
            if not obj.checkContentSecurityPolicy():
              continue

          stdHeaderNamesExist.add(headerName)
          self.standardHeaders[headerName]+=1
        else:
          if headerName in self.otherHeaders:
            self.otherHeaders[headerName]+=1
          else:
            self.otherHeaders[headerName]=1

      for name in self.stdHeaderNames-stdHeaderNamesExist:
        if name=='set-cookie' and not cookieRequired:
          continue
        self.exceptions[name].append(obj.url.strip())
      
  
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
    resultString.append("~~~~~~~~~~~~~~~~NONCES REQUIRED ~~~~~~~~~~~~~")
    resultString.append(str(self.countNonces))
    resultString.append("~~~~~~~~~~~~~~~URLS Not satisfying Nonces~~~~~~~~~~~~~~")
    resultString.append(str(self.noNoncesUrls))

    return '\n'.join(resultString)
  
def getUserAgent():
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  return opener




    
    
    
    
    
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
    thread.start_new_thread(client_listen, ())                                ## Producer thread !!
    ConsumerThread().start()

  except:
    print("unable to start thread")
  while 1:
    pass


