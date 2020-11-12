
import socket, sys, requests, threading, time

serverName = '127.0.0.1'
serverPort = int(sys.argv[1])

count = 0

def handle_connection():
    global count
    count += 1
    r = requests.get(f"http://{serverName}:{serverPort}")
    print(f"Response: {r.status_code}, Thread Count: {threading.active_count()}")
    r.close()
    
    
for i in range(100):
    th = threading.Thread(target=handle_connection)
    th.start()

print(count)