'''
 Elaborato Programmazione di Reti
            a.a. 2020/2021
            Valerio Di Zio
            Matricola: 942637
            Traccia 2
Web Server in Python per una azienda ospedaliera
'''


import sys, signal
import http.server
import socketserver
import threading 

#Accepting port number from standard input, else set default value
if sys.argv[1:]:
  port = int(sys.argv[1])
else:
  port = 8080


class ServerHandler(http.server.SimpleHTTPRequestHandler):        
    def do_GET(self):
        print(self.path)
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        

# ThreadingTCPServer allows many concurrent requests
server = socketserver.ThreadingTCPServer(('127.0.0.1',port), ServerHandler)


def main():
    #Indicates whether or not the server should wait for thread termination
    server.daemon_threads = True 
    #Rebind existing port number
    server.allow_reuse_address = True  
    #intercept CTRL+C
    #####signal.signal(signal.SIGINT, signal_handler)
    try:
      while True:
        server.serve_forever()
    except KeyboardInterrupt:
      pass
    server.server_close()

if __name__ == "__main__":
    main()