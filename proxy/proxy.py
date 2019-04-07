import socket
import time
import base64
import os
import csv
import threading
from thread import *
import sys
import httplib


HOST_ADD = "127.0.0.1"
BIND_PORT_ADD = 20100
USERS_FILE = open("users.csv", "r")
USERS = csv.reader(USERS_FILE)
time_limit = 5
CACHE = {}
REQUESTS_TIMES = {}
REQUESTS_TIME_SERVER = {}
REQUESTS_TIME_P = {}
BLACK = open('blacklist.txt', 'r')
BLACKLIST = BLACK.readlines()
BLACK.close()
BLACKLIST = [i.strip('\n') for i in BLACKLIST]

AUTH_USERS = []
for row in USERS :
    AUTH_USERS.append(base64.b64encode(row[0]+":"+row[1]))
USERS_FILE.close()


class ProxyServer:
    def __init__(self):
        self.ACCESS = False
        self.start = True
        self.con_set = False
        self.outside = True
        self.SERVER_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a TCP socket
        self.SERVER_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.SERVER_Socket.bind((HOST_ADD, BIND_PORT_ADD)) # bind the socket to a public host, and a port
        self.SERVER_Socket.listen(time_limit)    # become a server socket


    def proxy(self, conn, clientAddress):
        if clientAddress[1] > 20100 and clientAddress[1] <= 20200:
            self.outside = True
        else:
            self.outside = False
        request = conn.recv(4096)   # get the request from browser
        temp =request
        if self.start == True : 
            requestLine1 = temp.split('\n')[0]                   # parse the first line
            requestType = requestLine1.split(' ')[0]
            url = requestLine1.split(' ')[1]                        # get url
            requestLine3 = request.split('\n')[2]
        authentication = requestLine3.replace("Authorization: Basic","").strip()
        if authentication not in AUTH_USERS :
            print "not"
            self.ACCESS = False
        else :
            self.ACCESS = True
        url = url.strip()
        http = True
        if "https" not in url:
            http = True
        else :
        	http = False

        slashPos = url.find("//")          # find pos of //
        if (slashPos == -1):
            print "no change"
        else :
            index = slashPos+2
            url = url[index:]       # get the rest of url

        portPos = url.find(":")           # find the port pos (if any)
        host = url[:portPos]

        portEndPos = url.find("/")
        hostPort = int(url[portPos+1 : portEndPos])
        file = url[portEndPos :]

        if url not in REQUESTS_TIMES :
            REQUESTS_TIMES [url] = 1
            REQUESTS_TIME_SERVER [url] = time.time()
        else :
            REQUESTS_TIMES [url] += 1
            REQUESTS_TIME_P [url] = time.time()

        domain = "%s:%s" % (host, hostPort)
        try:
            blocked = False
            if domain in BLACKLIST:
                if not self.ACCESS :
                    print "Your request %s was blocked" %domain
                    blocked = True

            if not http :
                serve = httplib.HTTPSConnection(host, hostPort)
            else :
                serve = httplib.HTTPConnection(host, hostPort)

            
            if domain in BLACKLIST:
                if self.ACCESS:
            	   print "Request to "+domain+" is blacklisted but you are authorized to access it"
                   self.ACCESS=False
                else :
                    conn.send("Wrong credentials\n")
                    conn.close()
                    serve.close()
            elif blocked :
                conn.send("%s has been blacklisted\n" % domain)
                conn.close()
                serve.close()
            
            if self.outside :
                conn.send("%s is not allowed[OUTSIDE ADDDRESS]\n" % clientAddress[1])
                conn.close()
                server.close()

            serve.putrequest(requestType, file)
            if url not in CACHE :
                print "no cache"
            else :
                serve.putheader("If-Modified-Since", time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime(REQUESTS_TIME_P [url])))

            serve.putheader("User-Agent", "Mozilla/5.0 (X11; Linux x86_64)")
            serve.endheaders()

            serverResponse = serve.getresponse()
            status = serverResponse.status

            if status != 304 :
                print "url is not present in caching"
            else:
                print "in there cash"
                conn.send(CACHE [url])
                serve.close()
                conn.close()

            headers = serverResponse.getheaders()
            data = serverResponse.read()          # receive data from web server

            
            if url in REQUESTS_TIMES and url not in CACHE and len(CACHE) > 3 :
            	   maxTime = 0
            	   for key,value in REQUESTS_TIME_P :
            	       if value >= maxTime :
            	           maxURL = key
            	   del CACHE [maxURL]

        
            if url in REQUESTS_TIMES and url not in CACHE :
                if REQUESTS_TIMES [url] >= 2 and (REQUESTS_TIME_P [url] - REQUESTS_TIME_SERVER [url] <= 300) :
                    REQUESTS_TIME_SERVER [url] = REQUESTS_TIME_P [url]	
                    CACHE [url] = data        
                    REQUESTS_TIME_P [url] = time.time()
        
            if not (data) :
                conn.send("No data has been returned from the server\n")
            else :
                conn.send(data+"\n")              # sending to browser
            # else :
                
            serve.close()
            conn.close()
        except socket.error as error_msg:
            if serve :
                serve.close()
            if conn :
                conn.close()
    def listenToClient(self):
        if self.con_set == False :
            while True:
                clientSocketInfo = self.SERVER_Socket.accept()   # Establish the connection
                start_new_thread(self.proxy, clientSocketInfo)

proxyserver = ProxyServer()
proxyserver.listenToClient()
