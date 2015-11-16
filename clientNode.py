#Code to extract headers from HTTP Response
import urllib2
import datetime
import sys

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
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  return opener

def sendRequest(opener,url):
  fp = open(logFilePath,"a")
  try:
    infile = opener.open(url)
  except Exception, e:
    errorMessage = str(datetime.datetime.now())+"--"+e.message+"\n"
    fp.write(errorMessage)
    return None

  headerObj  = UrlHeader(url)
  redirectUrl = infile.geturl()
  if redirectUrl!=url:
    headerObj.redirectFlag = True
    headerObj.redirectUrl = redirectUrl.lower()

  headerObj.headers = infile.headers.dict
  return headerObj


    
    
    
    
    
if __name__=="__main__":
  if len(sys.argv)<2:
    print "Error, Usage: extract_headers.py clientId"
    sys.exit(2)
  logFilePath = "logClient%s"%sys.argv[1]
  opener = getUserAgent()
  a = sendRequest(opener,"https://www.google.com")
  c=sendRequest(opener,"https://cricket.yahoo.com")
  l = [a,c]
  b = headerCount ()
  b.accumulateResults(l)
  print b

