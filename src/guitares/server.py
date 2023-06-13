from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import threading
import os
import time
import urllib

# Custom Exception Class
class MyException(Exception):
    pass
 
# Custom Thread Class
class ServerThread(threading.Thread):
    def __init__(self, server_path, server_port):
        super().__init__(daemon=True)
        self.server_path = server_path
        self.server_port = server_port
     
  # Function that raises the custom exception
    def run_server(self):
        print("Server path : " + self.server_path)
        httpd = HTTPServer(self.server_path, ("", self.server_port))
        httpd.serve_forever()
        name = threading.current_thread().name
        raise MyException("An error in thread " + name)
 
    def run(self):       
        # Variable that stores the exception, if raised by run_server
        self.exc = None           
        try:
            self.run_server()
        except BaseException as e:
            self.exc = e
       
    # def join(self):
    #     threading.Thread.join(self)
    #     # Since join() returns in caller thread
    #     # we re-raise the caught exception
    #     # if any was caught
    #     if self.exc:
    #         raise self.exc
        
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

# def run_server(server_path, server_port):
#     print("Server path : " + server_path)
#     httpd = HTTPServer(server_path, ("", server_port))
#     httpd.serve_forever()

def run_node_server(server_path, server_port):
    print("Node server path : " + server_path)
    os.chdir(server_path)
    os.system("run_node_server.bat")

def start_server(server_path, port=3000, node=False):
    if node:
        thr = threading.Thread(target=run_node_server, args=(server_path, port), daemon=True)
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
    else:
#        thr = threading.Thread(target=run_server, args=(server_path, port), daemon=True)
        thr = ServerThread(server_path, port)
        thr.start()
        # # Exception handled in Caller thread
        # try:
        #     thr.join()
        # except Exception as e:
        #     print("Exception Handled in Main, Details of the Exception:", e)
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
