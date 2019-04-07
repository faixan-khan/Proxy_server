import sys
import os
import time
import SocketServer
import SimpleHTTPServer

if len(sys.argv) < 2:
    print "Invalid format:Enter the Port number as argument"
    print "Example python server.py 19999"
    raise SystemExit

class HTTPCacheRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def send_head(self):
        flag = self.headers.get('If-Modified-Since', None)
        if flag:
            filename = self.path.strip("/")
            if self.command != "POST" and os.path.isfile(filename):
                x = os.path.getmtime(filename)
                a = time.strptime(time.ctime(x), "%a %b %d %H:%M:%S %Y")
                b = time.strptime(flag, "%a %b  %d %H:%M:%S %Z %Y")
                if a < b:
                    self.send_response(304)
                    self.end_headers()
                    return None
        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)


    def do_POST(self):
        print("This is Post request")
        self.send_response(200)
        self.send_header('Cache-control', 'no-cache')
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def end_headers(self):
        self.send_header('Cache-control', 'must-revalidate')
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

PORT = int(sys.argv[1])
s = SocketServer.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)
s.allow_reuse_address = True

print "Starting Server on PORT", PORT
s.serve_forever()
