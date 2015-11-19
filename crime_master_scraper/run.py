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
clients = list()

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
        #try:
            #print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            #while True:
                #data = connection.recv(100)
                #print >>sys.stderr, 'received "%s"' % data
                #if data:
                    #print >>sys.stderr, 'sending data back to the client'
                    #connection.sendall(data)
                #else:
                    #print >>sys.stderr, 'no more data from', client_address
                    #break
                
        #finally:
            # Clean up the connection
        # Create a TCP/IP socket

def send_clients():
     links = list()
     print("in send clients")
     with open('links.csv') as f:
        content = f.readlines()
#    for line in content:
#	print line
     print(content)
     #with open('links.csv', 'r') as csvfile:
     #   read_file = csv.reader(csvfile, delimeter=",")
     for row in content:
         if row.strip() != 'link':
             links.append(row)
         #print(row)
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
	
    

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('template.html')


@app.route('/submit/', methods=['POST'])
def submit():
    page=request.form['webpage']
    num_pages_to_crawl=1
    print('reached below crawl')
    command = "scrapy crawl crime_master -a start_url="+page+" -a num_pages_to_crawl=" + str(num_pages_to_crawl) + " -o links.csv -t csv"
    print(command)
    os.system(command)
    send_clients()
    headers = ['A','B','C']
    numbers = ['3','2','4']
    headersPages = {'headers':headers,'numbers':numbers}
    missingpagesList = [	{'headerName':'A','pages':['example.com/a','example.com/b','wassup.com/hello']},
    						{'headerName':'B','pages':['example.com/a','wassup.com/hi']},
    						{'headerName':'C','pages':['example.com/a','example.com/b','wassup.com/hello','wassup.com/hi']}
    					]
    return render_template('result.html', page=page, headersPages=headersPages, missingpagesList=missingpagesList)

if __name__ == "__main__":
    thread.start_new_thread(add_client, () )
    app.run()
