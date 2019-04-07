# Proxy_Server
A multithreaded HTTP proxy server, which can handle and serve many requests, using sockets
A proxy server implemented via python socket programming with caching, blacklisting, authentication functionality

### Files :
      proxy.py is the main proxy file
      Proxy runs on some specific ports, some ports are reserved for clients and some for servers
      
      Client keeps asking any file [1-5].data from server by GET or POST method
      
      Server listens to specified port and serves any file as asked
      Proxy works as middleman between the server and client.

      run server in server directory
      python server.py port_num to run server on port port_num

      curl request can be sent as client request and get the response.
      curl --request GET --proxy 127.0.0.1:20000 --local-port 20001-20010 127.0.0.1:19999/1.txt
      This request will ask 1.txt file from server 127.0.0.1/19999 by GET request via proxy 127.0.0.1/20000 using one of the ports in range 20001-20010 on localhost.

      Valid username and password should be provided to access blacklisted servers.
      curl --request GET -u user:pass --proxy 127.0.0.1:20000 --local-port 20001-20010 127.0.0.1:19998/1.txt

      python client.py 20001-20010 20000 19995-19999
      This above commands will run a client which asks, after every 10 seconds, any file from any server in range 19995-19999, using any port in range 20001-20010, via proxy at port 20000
      

### Features -
        Ports in range 20101-20200 are outside servers which must not be accessed
        Threaded Proxy server
        The proxy keeps a count of the requests that are made. If a URL is requested more than 3 times in 5 minutes, the response from the server is cached. In case of any further requests for the same, the proxy utilises the “If Modified Since” header to check if any updates have been made, and if not, then it serves the response from the cache. The cache has a memory limit of 3 responses.
        The proxy supports blacklisting of certain outside domains. These addresses should be stored in “black-list.txt”. If the request wants a page that belongs to one of these, then, it returns an error page.
        Proxy handles authentication using Basic Access Authentication and appropriate headers to allow access to black-listed sites as well. The authentication is username/password based, and can be assumed to be stored on the proxy server.





