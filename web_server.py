'''
 Elaborato Programmazione di Reti
            a.a. 2020/2021
            Valerio Di Zio
            Matricola: 942637
            Traccia 2
Web Server in Python per una azienda ospedaliera
'''

import sys
import signal
import http.server
import socketserver
import shutil
import threading
import os
import base64
from pprint import pprint


FILEPATH = "pdf.pdf"

USER = "admin"
PASSWORD = "programmazionedireti"


# Manage the wait, used for intercept CTRL+C
waiting_refresh = threading.Event()

# Accepting port number from standard input, else set default value
if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080

# Intercept CTRL+C


def signal_handler(signal, frame):
    print(' Exiting http server (Ctrl+C pressed)')
    try:
        if(server):
            server.server_close()
    finally:
        # fermo il thread del refresh senza busy waiting
        waiting_refresh.set()
        sys.exit(0)

# YWRtaW46cHJvZ3JhbW1hemlvbmVkaXJldGk=


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    @staticmethod
    def check_credentials(auth_header):
        token = auth_header.split(" ")[1]
        data = USER + ":" + PASSWORD
        encoded_bytes = base64.b64encode(data.encode("utf-8"))
        encoded_str = str(encoded_bytes, "utf-8")
        return token == encoded_str

    def do_GET(self):
        auth_header = str(self.headers.get('Authorization'))
        if auth_header == None or not self.check_credentials(auth_header):
            self.send_response(401)
            self.send_header('WWW-Authenticate',
                             'Basic realm="Area Riservata"')
            self.end_headers()
        else:
            if(self.path == "/"+FILEPATH):
                print("Download File")
                with open(FILEPATH, 'rb') as f:
                    self.send_response(200)
                    self.send_header("Content-Type", 'application/pdf')
                    self.send_header(
                        "Content-Disposition", 'attachment; filename="{}"'.format(os.path.basename(FILEPATH)))
                    fs = os.fstat(f.fileno())
                    self.send_header("Content-Length", str(fs.st_size))
                    self.end_headers()
                    shutil.copyfileobj(f, self.wfile)
            else:
                http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.end_headers()


# ThreadingTCPServer allows many concurrent requests
server = socketserver.ThreadingTCPServer(('127.0.0.1', port), ServerHandler)


def main():
    print("Running...")
    # Indicates whether or not the server should wait for thread termination
    server.daemon_threads = True
    # Rebind existing port number
    server.allow_reuse_address = True
    # intercept CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
