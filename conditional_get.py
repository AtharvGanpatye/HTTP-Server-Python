import sys, socket, os
import mimetypes
from multiprocessing import Pool
import threading
from socket import *

if len(sys.argv) != 2:
    print("Bad Arguments, Enter Port Number")
    sys.exit()

serverip = '127.0.0.1'
serverport = int(sys.argv[1])

msgs = []

headers3="HEAD /index.html HTTP/1.1\r\n"
headers3+=f"Host: {serverip}:8000\r\n"
headers3+="Content-Type: text/html\r\n"
headers3+="User-Agent: Mozilla\r\n"
headers3+="Accept-Language: en-US\r\n"
headers3+="Accept-Encoding: */*\r\n"
headers3+="If-Modified-Since: Sun, 12 Nov 2020 20:00:00\r\n\r\n"
headers3 = bytes(headers3, "utf-8")
message3=headers3

msgs.append(message3)

def sendmsg(message):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((serverip, serverport))
    clientsocket.send(message)
    resp = clientsocket.recv(2048)
    try:
        print(resp.decode())
    except:
        print(resp)
    clientsocket.close()

with Pool(1) as p:
    p.map(sendmsg, msgs)
