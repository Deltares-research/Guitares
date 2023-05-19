from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import threading
import os
import time
import urllib

class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

def run_server(server_path, server_port):
    print("Server path : " + server_path)
    httpd = HTTPServer(server_path, ("", server_port))
    httpd.serve_forever()

def start_server(server_path, port=3000):
    thr = threading.Thread(target=run_server, args=(server_path, port), daemon=True)
    thr.start()
    while True:
        try:        
            print("Finding server ...")        
            urllib.request.urlcleanup()
            url = "http://localhost:" + str(port)
            request = urllib.request.urlopen(url)
            request.close()
            print("Found server running at port " + str(port) + " ...")        
            break        
        except:
            print("Waiting for server ...")
            time.sleep(1)
    return thr       
