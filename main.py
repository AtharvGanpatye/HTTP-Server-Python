"""
GET, POST, PUT, HEAD, DELETE, Cookies, Headers, non-persistent connections, Multiple clients
at the same time (with a sepearate program to test this), logging with levels of logging,
handling file permissions;  Server configuration - config file with DocumentRoot,
log file name, max simulateneous connections ; way to stop and restart the server;

Marks: Basic HTTP 5 method = 15 marks; MT = 3 marks; Config file and handling = 3 marks;
Cookies = 2 marks; Log = 3 marks;  File Permissions = 1 marks; Automated Testing = 3 marks.
"""

import socket
import sys
import os
import time
import threading
import random, logging

if len(sys.argv) < 2:
    print("Bad Arguments !\nGive Port Number As Well.")
    sys.exit(0)

files_dir = os.getcwd() + "/post-files/"

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Port number to bind with socket.
serverPort = int(sys.argv[1])

# Binding socket and port.
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5)
print("Server is listening . . . .\n")

# Access Log
logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
h1 = logging.FileHandler("log/access_log")
f1 = logging.Formatter('%(ip_add)s - %(asctime)s "%(request)s" %(status)s %(len)s %(message)s', datefmt='[%d/%b/%Y:%H:%M:%S %z]')
h1.setFormatter(f1)
logger.addHandler(h1)

# Error Log
logger_2 = logging.getLogger("error")
logger_2.setLevel(logging.ERROR)
h2 = logging.FileHandler("log/error_log")
f2 = logging.Formatter('%(asctime)s [error] [client %(ip_add)s]  %(message)s', datefmt='[%a %b %d %H:%M:%S %Y]')
h2.setFormatter(f2)
logger_2.addHandler(h2)

# Cookie Generator Function
def cookie_gen():
    f = open("cookiefile.txt", "r+")
    value = ''.join(random.choices(("abcdefghijklmnopqrstuvwxyz") + ("0123456789"), k = 10))
    if not value in f.read():
        f.write(value)
        f.write("\n")
    else:
        value = cookie_gen()
    return value

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

    requested_file = words[1]
    abs_file_path = os.getcwd() + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    # Content-Type Header
    charset = None
    if '/' == requested_file:
        content_type = 'text/html'
        charset = 'UTF-8'
    elif '.html' in requested_file:
        content_type = 'text/html'
        charset = 'UTF-8'
    elif '.jpg' in requested_file or '.jpeg' in requested_file:
        content_type = 'image/jpeg'
    elif '.png' in requested_file:
        content_type = 'image/png'
    elif '.gif' in requested_file:
        content_type = 'image/gif'
    elif '.css' in requested_file:
        content_type = 'text/css'
        charset = 'UTF-8'
    elif '.txt' in requested_file:
        content_type = 'text/plain'
        charset = 'UTF-8'
    else:
        content_type = 'text/html'
        charset = 'UTF-8'
        btext = "Sorry, Unknown Data Type !\nTry Again!\n".encode()
        status_code, reason_phrase = 404, "Not Found"

    if status_code == 406:
        return 'UTF-8',status_code, reason_phrase, "text/html", btext

    elif words[1] == "/favicon.ico":
        return -1,-1,-1,-1,-1

    elif words[1] == '/':
        req_file = open("home.html", mode='rb')
        btext = req_file.read()
        status_code, reason_phrase = 200, "OK"
        req_file.close()

    else:
        if not os.access(abs_file_path, os.F_OK):
            btext = "Sorry! Page Not Found\nTry Again!\n".encode()
            status_code, reason_phrase = 404, "Not Found"

        elif os.access(abs_file_path, os.R_OK):
            req_file = open(abs_file_path, mode='rb')
            btext = req_file.read()
            status_code, reason_phrase = 200, "OK"
            req_file.close()

        else:
            #btext = "File Doesn't Have Read Permissions !\n".encode()
            content_type = None
            status_code, reason_phrase = 403, "Forbidden"

    return charset, status_code, reason_phrase, content_type, btext


# HEAD Code
def handle_HEAD(words):

    requested_file = words[1]
    abs_file_path = os.getcwd() + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    if status_code == 406:
        return 'UTF-8', status_code, reason_phrase, "text/html", btext

    elif words[1] == "/favicon.ico":
        return -1,-1,-1,-1,-1

    elif words[1] == '/':
        if not os.access('home.html', os.F_OK):
            status_code, reason_phrase = 404, "Not Found"
        elif os.access('home.html', os.R_OK):
            status_code, reason_phrase = 200, "OK"
        else:
            status_code, reason_phrase = 403, "Forbidden"

    else:
        if not os.access(abs_file_path, os.F_OK):
            #btext = "Sorry! Page Not Found\nTry Again!\n".encode()
            status_code, reason_phrase = 404, "Not Found"

        elif os.access(abs_file_path, os.R_OK):
            status_code, reason_phrase = 200, "OK"

        else:
            #btext = "File Doesn't Have Read Permissions !\n".encode()
            status_code, reason_phrase = 403, "Forbidden"

    # Content-type header
    charset = None
    if '/' == requested_file:
        content_type = 'text/html'
        charset = 'UTF-8'
    elif '.html' in requested_file:
        content_type = 'text/html'
        charset = 'UTF-8'
    elif '.jpg' in requested_file or '.jpeg' in requested_file:
        content_type = 'image/jpeg'
    elif '.png' in requested_file:
        content_type = 'image/png'
    elif '.gif' in requested_file:
        content_type = 'image/gif'
    elif '.css' in requested_file:
        content_type = 'text/css'
        charset = 'UTF-8'
    elif '.txt' in requested_file:
        content_type = 'text/plain'
        charset = 'UTF-8'
    else:
        content_type = 'text/html'
        charset = 'UTF-8'
        btext = "Sorry, Unknown Data Type !\nTry Again!\n".encode()
        status_code, reason_phrase = 404, "Not Found"

    return charset, status_code, reason_phrase, content_type, btext


# DELETE Code
def handle_DELETE(words):
    requested_file = words[1]
    abs_file_path = os.getcwd() + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    content_type = 'text/html'
    if status_code == 406:
        return 'UTF-8', status_code, reason_phrase, "text/html", btext

    if os.access(abs_file_path, os.F_OK):
        os.remove(abs_file_path)
        btext = 'File Deleted Successfully !'.encode()
        status_code, reason_phrase = 200, "OK"
    
    else:
        btext = 'File Not Present On The Server !'.encode()
        status_code, reason_phrase = 200, "OK"

    return 'UTF-8',status_code, reason_phrase, content_type, btext


# POST Code
def handle_POST(bin_request, dtime, content_length_flag):

    bin_words = bin_request.split()

    btext = "Didn't Do Anything!".encode()
    status_code, reason_phrase = 200, "OK"
    try:
        i = bin_words.index(b'Content-Type:')
        content_type = bin_words[i+1].decode()
    except:
        content_type = None

    if not content_length_flag:        
        request = bin_request.decode()
    
    post_db = open('post-data.txt', 'a')
    
    if content_type and 'multipart/form-data' in content_type:
        
        i = bin_words.index(b'multipart/form-data;') 
        boundary = bin_words[i+1].split(b"=")[1]
        form_data = bin_request.split(boundary)[2:-1]
        post_db.write(dtime + "\n")
        for entry in form_data:
            if b'Content-Type:' in entry:
                # Handle for file
                i = entry.index(b'\r\n\r\n')
                file_name = entry[:i].split()[3].split(b'"')[1].decode()
                file_data = entry[i+4:]
                try:
                    f = open(files_dir + file_name, 'wb')
                    f.write(file_data)
                    f.close()
                    btext = "Record Saved Successfully ! Files Uploaded Successfully !!".encode()
                    status_code, reason_phrase = 200, "OK"
                except:
                    btext = "Some Error Occurred !".encode()
                    status_code, reason_phrase = 200, "OK"
            else:
                temp_data = entry.decode().split()
                name = temp_data[2].split('"')[1] + ": "
                # Writing One Form Element 
                for i in range(3,len(temp_data) - 1):
                    name += temp_data[i] + " "
                try:
                    post_db.write(name + "\n")
                    btext = "Record Saved Successfully !".encode()
                    status_code, reason_phrase = 200, "OK"
                except:
                    btext = "Some Error Occurred !".encode()
                    status_code, reason_phrase = 200, "OK"

    elif content_type and 'application/x-www-form-urlencoded' in content_type:
        
        words = request.split()
        # Open record file in append mode
        post_db.write(dtime + "\n")
        data = words[-1].split('&')
        print("Data of form: ", data)
        for entry in data:
            # Open record file and store in it
            if '+' in entry:
                entry = entry.split('+')
                value = ""
                for e in entry:
                    value += e + " "
                value = convert_to_string(value)
                value = value.split("=")
                post_db.write(value[0] + ": " + value[1] + "\n")
            else:
                entry = convert_to_string(entry)
                entry = entry.split("=")
                post_db.write(entry[0] + ": " + entry[1] + "\n")
            
        post_db.write("\n")
        post_db.close()
        btext = open('success.html',mode='rb').read()
        status_code, reason_phrase = 200, "OK"

    else:
        
        words = request.split()
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
    return 'UTF-8',status_code, reason_phrase, content_type, btext


# PUT Code
def handle_PUT(bin_request):

    i = bin_request.index(b'\r\n\r\n')
    words = bin_request[:i].split()
    data = bin_request[i+4:]
    
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    if status_code == 406:
        return 'UTF-8',status_code, reason_phrase, "text/html", btext
    
    file_name = words[1].decode()[1:]
    abs_file_path = files_dir + file_name
    if os.path.isfile(abs_file_path):
        f = open(abs_file_path, 'wb')
        f.write(data)
        f.close()
        btext = b'File Updated Successfully !'
        status_code, reason_phrase = 200, "OK"
    else:
        f = open(abs_file_path, 'wb')
        f.write(data)
        f.close()
        btext = b'File Created Successfully !'
        status_code, reason_phrase = 201, "Created"

    return 'UTF-8',status_code, reason_phrase, content_type, btext


# Handle Each Request
def handle_request(connectionSocket, addr):

    bin_request = b""
    buffer_size = 4096
    bin_request = connectionSocket.recv(buffer_size)
    bin_words = bin_request.split()
    content_length_flag = False
    if b'Content-Length:' in bin_words and len(bin_request) >= buffer_size * 0.80:
        content_length_flag = True
        while True:
            data = connectionSocket.recv(buffer_size)
            bin_request += data
            if len(data) < buffer_size * 0.80:
                break

    print("Request:")
    print(f"Thread ID: {threading.get_ident()}, Total Threads: {threading.active_count()}")
    print(bin_request)
    print("\n")

    method = bin_words[0].decode()
    temp = bin_request.splitlines()
    # Making list of date, time in required format
    dtime = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
    # GET
    # Need to check file existance, permissions, present date
    status_code, reason_phrase, content_type, btext = 0, 0, 0, b'null'

    if method == "GET":
        request =  bin_request.decode()
        words = request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_GET(words)

        if status_code == -1:
            connectionSocket.close()
            return


    elif method == "POST":
        bin_words = bin_request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_POST(bin_request, dtime, content_length_flag)


    elif method == "PUT":
        charset, status_code, reason_phrase, content_type, btext = handle_PUT(bin_request)


    elif method == "HEAD":
        request =  bin_request.decode()
        words = request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_HEAD(words)


    elif method == "DELETE":
        request =  bin_request.decode()
        words = request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_DELETE(words)


    else:
        status_code, reason_phrase = 400, "Bad Request"
        content_type = 'text/html'
        btext = 'Request Other Than GET, POST, PUT, DELETE, HEAD'.encode()

    # Response Headers
    string = "HTTP/1.1 {} {}\n".format(status_code, reason_phrase)
    string += "Date: {} \n".format(dtime)
    string += "Server: Atharv's Server/V1.0\n"
    string += "Connection: close\n"

    # Writing Into Log Files
    if status_code//100 == 4 or status_code//100 == 5:
        extra = {'ip_add': addr[0]}
        logger_2 = logging.LoggerAdapter(logger_2, extra)
        if status_code == 404:
            logger_2.error('File Not Found')
        elif status_code == 400:
            logger_2.error('Bad Request')
        elif status_code == 406:
            logger_2.error('Language Not Supported')
        else:
            # Need for some other status codes
            pass
    
    if len(btext) != 0:
        extra = {'ip_add': addr[0], 'request': temp[0].decode(), 'status': str(status_code), 'len': str(len(btext))}
    else:
        extra = {'ip_add': addr[0], 'request': temp[0].decode(), 'status': str(status_code), 'len': '-'}

    logger_ = logging.LoggerAdapter(logger, extra)
    logger_.info('Recieved request.')

    if not b'Cookie:' in bin_words:
        value = cookie_gen()
        value += "\n"
        temp = "Set-Cookie: HttpSession=" + value
        string += temp

    # Check content-type, charset.
    if charset:
        string += "Content-Type: {}; charset=UTF-8\n".format(content_type)
    if content_type:
        string += "Content-Type: {};\n".format(content_type)
    
    # Checking if content is present or not.
    if btext:
        string += "Content-Length: {}\n\n".format(len(btext))
        output = string.encode() + btext
    else:
        string += "Content-Length: {}\n\n".format(len(string.encode()))
        output = string.encode()

    connectionSocket.send(output)
    connectionSocket.close()
    return

# Accept Request
try:
    while True:
        connectionSocket, addr = serverSocket.accept()
        print("New Request Received From : {}".format(addr))
        print("Connection Socket is: \n{}".format(connectionSocket))
        # Create A Thread For Each Request
        th = threading.Thread(target=handle_request, args=(connectionSocket,addr))
        th.start()
except KeyboardInterrupt:
    print("Server Closed !")
    serverSocket.close()
