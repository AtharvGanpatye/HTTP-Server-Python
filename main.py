"""
GET, POST, PUT, HEAD, DELETE, Cookies, Headers, non-persistent connections, Multiple clients
at the same time (with a sepearate program to test this), logging with levels of logging,
handling file permissions;  Server configuration - config file with DocumentRoot,
log file name, max simulateneous connections ; way to stop and restart the server;

Marks: Basic HTTP 5 method = 15 marks; MT = 3 marks; Config file and handling = 3 marks;
cookies = 2 marks; log = 3 marks;  file permissions = 1 marks; Automated Testing = 3 marks.
"""

from socket import *
import sys, os, time

serverSocket = socket(AF_INET, SOCK_STREAM)

# Port number to bind with socket.
serverPort = int(sys.argv[1])

# Binding socket and port.
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5)
print("Server is listening . . . .\n")


# Handle possilbe request headers.
def handle_req_headers(words):
    accept_lang, content_type = None, None
    # Accept-Language header
    if 'Accept-Language:' in words:
        index = words.index('Accept-Language:')
        accept_lang = words[index+1]
        
    if 'Content-Type:' in words:
        index = words.index('Content-Type:')
        content_type = words[index+1]

    return accept_lang, content_type


def handle_codes(words, accept_lang):
    status_code, reason_phrase, btext = None, None, None

    if accept_lang and 'en' not in accept_lang:
        # Server can't respond to language other than english
        status_code, reason_phrase = 406, "Not Acceptable"
        btext = b'Language other than English.\n'

    return status_code, reason_phrase, btext


def convert_to_string(string):
    if '%' not in string:
        return string 
    new = "" 
    i = 0 
    while(i < len(string)): 
        if string[i] != '%': 
            new += string[i] 
            i += 1 
        else: 
            hex_code = string[i+1:i+3] 
            new += bytes.fromhex(hex_code).decode('utf-8') 
            i += 3 
    return new 


# GET Code
def handle_GET(words):

    request = words[1]
    abs_file_path = os.getcwd() + request

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    if status_code == 406:
        return status_code, reason_phrase, "text/html", btext

    elif words[1] == "/favicon.ico":
        return -1,-1,-1,-1

    elif words[1] == '/':
        req_file = open("home.html", mode='rb')
        btext = req_file.read()
        status_code, reason_phrase = 200, "OK"
        req_file.close()

    elif os.path.isfile(abs_file_path):
        req_file = open(abs_file_path, mode='rb')
        # Check for permissions needed
        btext = req_file.read()
        status_code, reason_phrase = 200, "OK"
        req_file.close()

    elif not os.path.isfile(abs_file_path):
        btext = "Sorry! Page Not Found\nTry Again!\n".encode()
        status_code, reason_phrase = 404, "Not Found"
        return status_code, reason_phrase, "text/html", btext

    else:
        pass

    # Content-type header
    if '/' == request:
        content_type = 'text/html'
    elif '.html' in request:
        content_type = 'text/html'
    elif '.jpg' in request or '.jpeg' in request:
        content_type = 'image/jpeg'
    elif '.png' in request:
        content_type = 'image/png'
    elif '.gif' in request:
        content_type = 'image/gif'
    elif '.css' in request:
        content_type = 'text/css'
    elif '.txt' in request:
        content_type = 'text/plain'
    else:
        content_type = 'text/html'
        btext = "Sorry, Unknown Data Type !\nTry Again!\n".encode()
        status_code, reason_phrase = 404, "Not Found"

    return status_code, reason_phrase, content_type, btext


# POST Code
def handle_POST(request, dtime):

    words = request.split()
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)
    post_db = open('post-data.txt', 'a')
    flag = 0

    if content_type and 'multipart/form-data' in content_type:
        index = words.index('multipart/form-data;')
        boundary = words[index+1].split("=")[1]
        form_data = request.split(boundary)[2:]
        post_db.write(dtime + "\n")
        status_code, reason_phrase = 200, "OK"

        for line in form_data:
            entry = line.split()
            if 'form-data;' in entry and 'Content-Type:' not in entry:
                key = entry[2].split('"')[1]
                value = entry[3]
                post_db.write(key + ": " + value + "\n")

            elif 'form-data;' in entry and 'Content-Type:' in entry:   
                i = entry.index('Content-Type:')
                file_format = entry[i+1]

                if file_format == 'text/plain':
                    file_name = entry[3].split('"')[1]
                    i = line.index("\r\n\r\n")
                    content = line[i+4:].split('--')[0]
                    abs_file_path = os.getcwd() + "/files/" + file_name
                    f = open(abs_file_path, 'w')
                    f.write(content)
                    f.close()

                else:
                    status_code, reason_phrase = 404, "Not Found"
                    flag = 1
            else:
                pass

        post_db.write("\n")
        post_db.close()
        if flag == 0:
            btext = open('success.html',mode='rb').read()
        else:
            btext = b'Unknown file format of uploaded file !'

    elif content_type and 'application/x-www-form-urlencoded' in content_type:
    # Open record file in append mode
        
        post_db.write(dtime + "\n")
        data = words[-1].split('&')
        for entry in data:
            # Open record file and store in it
            if '+' in entry:
                entry = entry.split('+')
                value = ""
                for e in entry:
                    value += e + " "
                value = convert_to_string(value)
                value = value.split("=")
                post_db.write(value[0] + ": " + value[1])
            else:
                entry = convert_to_string(entry)
                entry = entry.split("=")
                post_db.write(entry[0] + ": " + entry[1])
            
        post_db.write("\n")
        post_db.close()
        btext = open('success.html',mode='rb').read()
        status_code, reason_phrase = 200, "OK"

    else:
        form_data = request.split('\r\n\r\n')[1]
        lines = form_data.split('\r\n')
        for line in lines:
            if '=' not in line:
                post_db.write(line)
            else:
                entry = line.split("=")
                post_db.write(entry[0] + ": " + entry[1] + "\n")
        post_db.close()
        btext = open('success.html',mode='rb').read()
        status_code, reason_phrase = 200, "OK"

    content_type = 'text/html'
    return status_code, reason_phrase, content_type, btext


# PUT Code
def handle_put(request):
    pass

while True:
    connectionSocket, addr = serverSocket.accept()
    #print("New Request Received From : {}".format(addr))
    #print("Connection Socket is: \n{}".format(connectionSocket))

    request = connectionSocket.recv(2048).decode()
    words = request.split()
    print(request) 
    #print(words)
    # Making list of date, time in required format
    dtime = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
    # GET
    # Need to check file existance, permissions, present date
    status_code, reason_phrase, content_type, btext = 0,0,0,'null'

    if words[0] == "GET":
        status_code, reason_phrase, content_type, btext = handle_GET(words)

        if status_code == -1:
            continue

    elif words[0] == "POST":
        status_code, reason_phrase, content_type, btext = handle_POST(request, dtime)

    elif words[0] == "PUT":
        pass

    elif words[0] == "HEAD":
        pass

    elif words[0] == "DELETE":
        pass

    else:
        continue

    string = "HTTP/1.1 {} {}\n".format(status_code, reason_phrase)
    string += "Date: {} \n".format(dtime)
    string += "Server: Atharv's Server/V1.0\n"
    string += "Connection: close\n"
    string += "Content-Type: {}; charset=UTF-8\n".format(content_type)
    string += "Content-Length: {}\n\n".format(len(string.encode() + btext))

    output = string.encode() + btext
    connectionSocket.send(output)

    connectionSocket.close()

serverSocket.close()
