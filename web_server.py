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
import threading
import os
import base64
import zlib

# Path to the pdf file
FILEPATH = "pdf.pdf"

# Login credentials
USER = "admin"
PASSWORD = "programmazionedireti"

# Value for the choice of compression
USE_GZIP_COMPRESSION = False

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


class ServerHandler(http.server.SimpleHTTPRequestHandler):

    # Method of compressing using GZIP
    @staticmethod
    def gzip_encode(content):
        gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        data = gzip_compress.compress(content) + gzip_compress.flush()
        return data
        
    # Method for verifying credentials using base64
    @staticmethod
    def check_credentials(auth_header):
        token = auth_header.split(" ")[1]
        data = USER + ":" + PASSWORD
        encoded_bytes = base64.b64encode(data.encode("utf-8"))
        encoded_str = str(encoded_bytes)
        return token == encoded_str

    def do_GET(self):
        auth_header = self.headers.get('Authorization')
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
                    raw_content_length = fs.st_size
                    content = f.read()
                    if USE_GZIP_COMPRESSION:
                        print("Download del documento compresso con GZIP")
                        self.send_header("Content-Encoding", "gzip")
                        content = self.gzip_encode(content)
                        compressed_content_length = len(content)
                        self.send_header("Content-Length",
                                         compressed_content_length)
                    else:
                        print("Download del documento non compresso")
                        self.send_header("Content-Length", raw_content_length)
                    self.end_headers()
                    self.wfile.write(content)
            else:
                http.server.SimpleHTTPRequestHandler.do_GET(self)


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
