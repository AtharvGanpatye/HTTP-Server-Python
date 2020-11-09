import sys, socket, os

if len(sys.argv) != 4:
    print("Bad Arguments, Enter Port Number")

senderPort = int(sys.argv[1])
file_path = sys.argv[2]
content_type = sys.argv[3]
file_name = file_path.split('/')[-1]

if os.path.isfile(file_path):
    f = open(file_path, 'rb')
    data = f.read()
    f.close()
else:
    print("File Doesn't Exist! Enter Correct File Path")
    sys.exit()

serverName = '127.0.0.1'
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to server......\n")

request = f"PUT /{file_name} HTTP/1.1\r\n"
request += f"Host: {serverName}:{senderPort}\r\n"
request += f"Content-Type: {content_type}\r\n"
request += f"Content-Length: {len(data)}\r\n\r\n"
request = request.encode()
request += data

try:
    senderSocket.connect((serverName, senderPort))
    print("Connected !\n")
except:
    print("Can't connect to server")
    sys.exit()

senderSocket.send(request)
response = senderSocket.recv(1024).decode()
print("Response : ", response)
senderSocket.close()