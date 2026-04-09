"""HTTP server utilities for serving map tile files to the Qt web view."""

import os
import threading
import time
import urllib
import urllib.request
from http.server import HTTPServer as BaseHTTPServer
from http.server import SimpleHTTPRequestHandler
from typing import Any, Optional, Tuple, Type


# Custom Exception Class
class MyException(Exception):
    """Raised when a server thread encounters an error."""

    pass


class QuietHandler(SimpleHTTPRequestHandler):
    """HTTP request handler that suppresses all log output."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress logging.

        Parameters
        ----------
        format : str
            Log format string (unused).
        *args : Any
            Log arguments (unused).
        """
        pass


class ServerThread(threading.Thread):
    """Daemon thread that runs a local HTTP server.

    Parameters
    ----------
    server_path : str
        Directory to serve files from.
    server_port : int
        Port number for the HTTP server.
    """

    def __init__(self, server_path: str, server_port: int) -> None:
        super().__init__(daemon=True)
        self.server_path: str = server_path
        self.server_port: int = server_port
        self.exc: Optional[BaseException] = None

    def run_server(self) -> None:
        """Start the HTTP server and serve forever.

        Raises
        ------
        MyException
            Always raised after ``serve_forever`` returns (should not happen
            under normal operation).
        """
        print(f"Server path : {self.server_path}")
        httpd = HTTPServer(self.server_path, ("", self.server_port))
        httpd.serve_forever()
        name = threading.current_thread().name
        raise MyException(f"An error in thread {name}")

    def run(self) -> None:
        """Execute the server, capturing any exception for later inspection."""
        self.exc = None
        try:
            self.run_server()
        except BaseException as e:
            self.exc = e


class HTTPHandler(SimpleHTTPRequestHandler):
    """Request handler that serves files relative to ``server.base_path``."""

    def translate_path(self, path: str) -> str:
        """Translate a URL path to a filesystem path using the server's base path.

        Parameters
        ----------
        path : str
            URL path from the request.

        Returns
        -------
        str
            Absolute filesystem path.
        """
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def end_headers(self) -> None:
        """Add CORS and cache-control headers before finalising the response."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress logging.

        Parameters
        ----------
        format : str
            Log format string (unused).
        *args : Any
            Log arguments (unused).
        """
        pass


class HTTPServer(BaseHTTPServer):
    """HTTP server that serves files from a configurable base path.

    Parameters
    ----------
    base_path : str
        Root directory to serve files from.
    server_address : Tuple[str, int]
        ``(host, port)`` tuple.
    RequestHandlerClass : Type[SimpleHTTPRequestHandler], optional
        Handler class, by default :class:`HTTPHandler`.
    """

    def __init__(
        self,
        base_path: str,
        server_address: Tuple[str, int],
        RequestHandlerClass: Type[SimpleHTTPRequestHandler] = HTTPHandler,
    ) -> None:
        self.base_path: str = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)


def run_node_server(server_path: str, server_port: int) -> None:
    """Start a Node.js-based HTTP server via a batch script.

    Parameters
    ----------
    server_path : str
        Directory containing the Node.js server files.
    server_port : int
        Port number (currently unused by the batch script).
    """
    print(f"Node server path : {server_path}")
    os.chdir(server_path)
    os.system("run_node_server.bat")


def start_server(
    server_path: str, port: int = 3000, node: bool = False
) -> threading.Thread:
    """Start an HTTP server in a background thread and wait until it is ready.

    Parameters
    ----------
    server_path : str
        Directory to serve files from.
    port : int, optional
        Port number, by default 3000.
    node : bool, optional
        Use a Node.js server if ``True``, otherwise use the built-in Python
        server. By default ``False``.

    Returns
    -------
    threading.Thread
        The background thread running the server.
    """
    if node:
        the = threading.Thread(
            target=run_node_server, args=(server_path, port), daemon=True
        )
        the.start()
        while True:
            try:
                urllib.request.urlcleanup()
                url = f"http://localhost:{port}"
                request = urllib.request.urlopen(url)
                request.close()
                print(f"Found server running at port {port} ...")
                break
            except Exception:
                print("Waiting for server ...")
                time.sleep(1)
        return the
    else:
        the = ServerThread(server_path, port)
        the.start()
        while True:
            try:
                urllib.request.urlcleanup()
                url = f"http://localhost:{port}"
                request = urllib.request.urlopen(url)
                request.close()
                print(f"Found server running at port {port} ...")
                break
            except Exception:
                print("Waiting for server ...")
                time.sleep(1)
        return the
