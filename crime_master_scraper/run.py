from flask import Flask, render_template, request, url_for
import os
import csv
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi
import socket
import sys
import thread
from threading import Thread, Lock
from threading import Condition
import csv
import cPickle as pickle
import sys, os
import time
sys.path.append(os.path.abspath(".."))
from clientNode import headerCount
import validators

clients = list()
counter = 0  #This variable will hold the number of nodes/clients to which data for processing was sent.
waitfor = 0  #This variable will hold the number of responses it has received till now.
response_queue = []
queue = []

condition = Condition()
condition_response = Condition()

resultData = None

def add_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
        
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    sock.listen(5)
    while True:
        # Wait for a connection
        #print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        clients.append(client_address)
	#logger.info("New Client added : " + str(client_address))
        print(client_address)
        connection.close()

def client_listen():
    global waitfor
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock1.bind(server_address)
    print "thread started in client_listen" 
    sock1.listen(5)
    while True:
        # Wait for a connection
        connection, client_address = sock1.accept()
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            data = connection.recv(11000)
	    response = pickle.loads(data)
	    #print >>sys.stderr, 'received "%s"' % response.result_dict
            print " Got Response "
            #print response
            waitfor = waitfor + 1
	    ProducerResponse(response);
                
        finally:
            # Clean up the connection
            connection.close()


def send_clients():
     links = list()
     global counter
     global waitfor
     global resultData
     counter = 0
     waitfor = 0
     resultData = headerCount()
     print("in send clients")
     with open('links.csv') as f:
        content = f.readlines()
     print(content)
     for row in content:
         if row.strip() != 'link':
             links.append(row)
     print links
     if len(clients) == 0:
         print('No clients available')
         return
     if len(links) != 1:
       x = len(links)/len(clients)
     else:
       x = 1
     z = 0
     for client in clients:
       print client
       counter = counter + 1
       data = []
       for i in range(z,min(z+x,len(links))):
         data.append(links[i])
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       print(client)
       sock.connect(client)
       data_strings = pickle.dumps(data,-1)
       print("Pickle dumps created")
       sock.sendall(data_strings)
       print("Data sent") 
       sock.close()
       z = z+x
       if z >= len(links):
         break


################################################################################
 
def Producer(request):
    global queue
    print "in produver"   
    condition.acquire()
    length = len(queue)
    queue.append(request)
    print "Produced", request 
    if length == 0:
        print "Notifying"
        condition.notify()
    condition.release()

class ConsumerResponseThread(Thread):
    def run(self):
        global response_queue
        while True:
            condition_response.acquire()
            if not response_queue:
                print "Nothing in queue, consumer is waiting"
                condition_response.wait()
                print "Producer added something to queue and notified the consumer"
            response = response_queue.pop(0)
            print 'In consumer thread run method \n\n\n\n\n'
            print response
            self.addToResultData(response)
	    condition_response.release()
            time.sleep(1)

    def addToResultData(self,response):
        global resultData
        print '\n\n\n\n'
        print response
        for key,value in response.standardHeaders.iteritems():
            resultData.standardHeaders[key]+=value
        
        for key,value in response.otherHeaders.iteritems():
            if resultData.otherHeaders.has_key(key):
              resultData.otherHeaders[key]+=value
            else:
              resultData.otherHeaders[key]=value

        for key,value in response.exceptions.iteritems():
            resultData.exceptions[key].extend(value)

        resultData.redirectCount+=response.redirectCount

        resultData.countNonces+=response.countNonces

        resultData.noNoncesUrls.extend(response.noNoncesUrls)


    
def ProducerResponse(response):
    global response_queue   
    condition_response.acquire()
    length = len(response_queue)
    response_queue.append(response)
    #print "Produced_response", response 
    if length == 0:
        print "Notifying"
        condition_response.notify()
    condition_response.release() 

#currently we need to add code for creation of queue and manipulating it.

####################################################################################	
    

app = Flask(__name__)

@app.route('/')
def form():
    error = None
    return render_template('template.html',error=error)


@app.route('/submit/', methods=['POST'])
def submit():
    global waitfor
    global counter
    global resultData
    page=request.form['webpage']
    num_pages_to_crawl=request.form['configPage']
    if not validators.url(page):
        error = 'Please enter valid URL';
        return render_template('template.html',error=error)
    if num_pages_to_crawl == '' or int(num_pages_to_crawl) <= 0 :
        error = 'Please enter valid number of pages'
        return render_template('template.html',error=error)
    print('reached below crawl')
    os.system('rm links.csv')
    command = "scrapy crawl crime_master -a start_url="+page+" -a num_pages_to_crawl=" + str(num_pages_to_crawl) + " -o links.csv -t csv"
    print(command)
    os.system(command)
    counter = 0
    waitfor = 0
    send_clients()
    while counter != waitfor:
        #print counter
        #print waitfor
	continue
    print 'printing result data'
    print resultData

    headers = ['A','B','C']
    numbers = ['3','2','4']
    headersPages = {'headers':headers,'numbers':numbers}
    missingpagesList = [	{'headerName':'A','pages':['example.com/a','example.com/b','wassup.com/hello']},
    						{'headerName':'B','pages':['example.com/a','wassup.com/hi']},
    						{'headerName':'C','pages':['example.com/a','example.com/b','wassup.com/hello','wassup.com/hi']}
    					]
    print "Standard Headers"
    print resultData.standardHeaders

    #resultList = [result.as_dict() for result in resultData]

    #print "Result List"
    #print resultList
    try:
        return render_template('result.html', page=page, headersPages=resultData.standardHeaders, otherHeaders=resultData.otherHeaders, missingpagesList=resultData.exceptions)
    except Exception as e:
        print "Error" + str(e)
        return render_template("result.html", error=str(e))

    #return render_template('result.html',page=page)

if __name__ == "__main__":
    thread.start_new_thread(add_client, () )
    thread.start_new_thread(client_listen, ())
    ConsumerResponseThread().start()
    app.run()
