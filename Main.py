"""
GET, POST, PUT, HEAD, DELETE, Cookies, Headers, non-persistent connections, Multiple clients
at the same time (with a sepearate program to test this), logging with levels of logging,
handling file permissions;  Server configuration - config file with DocumentRoot,
log file name, max simulateneous connections ; way to stop and restart the server;

Marks: Basic HTTP 5 method = 15 marks; MT = 3 marks; Config file and handling = 3 marks;
Cookies = 2 marks; Log = 3 marks;  File Permissions = 1 marks; Automated Testing = 3 marks.
"""
import datetime
import socket
import sys
import os
import time
import threading
import random, logging
import shutil
import mimetypes
from configparser import ConfigParser

if len(sys.argv) < 2:
    print("Bad Arguments !\nGive Port Number As Well.")
    sys.exit(0)

#Read config.ini file
conf = ConfigParser()
conf.read("server.ini")

default = conf["SERVERCONFIG"]
logs = conf["LOGS"]
info = conf["DATA"]
uploads = conf["FILES"]

# Variables for paths
doc_root = default["DocumentRoot"]
server_addr = default["server_addr"]
access_log_path = logs["access_log"]
error_log_path = logs["error_log"]
files_dir = uploads["uploaded"]
cookie_file_path = info["cookies"]
post_file_path = info["post"]
trash_path = info["trash"]

# Creating server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Port number to bind with socket.
serverPort = int(sys.argv[1])

# Binding socket and port.
serverSocket.bind((server_addr, serverPort))
serverSocket.listen(5)
print("Server is listening . . . .\n")

# Access Log
logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
h1 = logging.FileHandler(access_log_path)
f1 = logging.Formatter('%(ip_add)s - %(asctime)s "%(request)s" \t %(status)s %(len)s %(message)s', datefmt='[%d/%b/%Y:%H:%M:%S %z]')
h1.setFormatter(f1)
logger.addHandler(h1)

# Error Log
logger_2 = logging.getLogger("error")
logger_2.setLevel(logging.ERROR)
h2 = logging.FileHandler(error_log_path)
f2 = logging.Formatter('%(asctime)s [error] [client %(ip_add)s]  %(message)s', datefmt='[%a %b %d %H:%M:%S %Y]')
h2.setFormatter(f2)
logger_2.addHandler(h2)

# Cookie Generator Function
def cookie_gen():
    f = open(cookie_file_path, "r+")
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

# Dictionary to convert month to its decimal
month = { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }

# For checking last modified
def check_modified(date_req, file_path):
    date = date_req.split()
    dd = int(date[1])
    mm = month[date[2]]
    yy = int(date[3])
    t = date[4].split(':')
    hr = int(t[0])
    mn = int(t[1])
    ss = int(t[2])
    t_check = datetime.datetime(yy, mm, dd, hr, mn, ss) 

    date = time.ctime(os.path.getmtime(file_path)).split()
    dd = int(date[2])
    mm = month[date[1]]
    yy = int(date[4])
    t = date[3].split(':')
    hr = int(t[0])
    mn = int(t[1])
    ss = int(t[2])
    t_mod = datetime.datetime(yy, mm, dd, hr, mn, ss)

    if t_check < t_mod:
        return True
    else:
        return False  


def handle_codes(words, accept_lang):
    status_code, reason_phrase, btext = None, None, None

    if accept_lang and 'en' not in accept_lang:
        # Server can't respond to language other than English
        status_code, reason_phrase = 406, "Not Acceptable"
        btext = b'<h1>Language other than English.</h1>'

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

    if words[1] == "/":
        requested_file = "index.html"
    else:
        requested_file = words[1][1:]
        
    file_path = doc_root + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    if status_code == 406:
        return 'UTF-8',status_code, reason_phrase, "text/html", btext
        
    # Checking
    if words[1] == "/favicon.ico":
        return -1,-1,-1,-1,-1

    else:
        if not os.access(file_path, os.F_OK):
            btext = "<h1>Sorry! Page Not Found! Try Again!!</h1>".encode()
            content_type = 'text/html'
            charset = 'UTF-8'
            status_code, reason_phrase = 404, "Not Found"

        elif os.access(file_path, os.R_OK):

            if 'If-Modified-Since:' in words:
                i = words.index('If-Modified-Since:')
                date = words[i+1] + " " + words[i+2] + " " + words[i+3] + " " + words[i+4] + " " + words[i+5]
                check = check_modified(date, file_path)

            if check:
                req_file = open(file_path, mode='rb')
                btext = req_file.read()
                status_code, reason_phrase = 200, "OK"
                req_file.close()
                # Content-Type Header
                content_type = mimetypes.guess_type(file_path)[0]
                if not content_type:
                    content_type = 'text/html'
                    charset = 'UTF-8'
                    btext = "<h1>Sorry, Unknown Data Type !</h1>".encode()
                    status_code, reason_phrase = 404, "Not Found"

                elif 'text' in content_type:
                    charset = "UTF-8"
                
                else:
                    charset = None

            else:
                charset = None
                content_type = 'text/html'
                status_code, reason_phrase = 304, "Not Modified" 

        else:
            btext = "<h1>File Doesn't Have Read Permissions !</h1>".encode()
            content_type = "text/html"
            charset = 'UTF-8'
            status_code, reason_phrase = 403, "Forbidden"

    return charset, status_code, reason_phrase, content_type, btext


# HEAD Code
def handle_HEAD(words):

    if words[1] == "/":
        requested_file = "index.html"
    else:
        requested_file = words[1][1:]

    file_path = doc_root + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    if status_code == 406:
        return 'UTF-8', status_code, reason_phrase, "text/html", btext

    elif words[1] == "/favicon.ico":
        return -1,-1,-1,-1,-1

    else:
        if not os.access(file_path, os.F_OK):
            status_code, reason_phrase = 404, "Not Found"

        elif os.access(file_path, os.R_OK):
            if 'If-Modified-Since:' in words:
                i = words.index('If-Modified-Since:')
                date = words[i+1] + " " + words[i+2] + " " + words[i+3] + " " + words[i+4] + " " + words[i+5]
                print(date)
                check = check_modified(date, file_path)
            
            if check:
                status_code, reason_phrase = 200, "OK"
            else:
                status_code, reason_phrase = 304, "Not Modified"
            # Content-Type Header
            content_type = mimetypes.guess_type(file_path)[0]
            # if 'text' in content_type:
            #     charset = 'UTF-8'
            # else:
            #     charset = None
            content_type = None
            charset = None

        else:
            status_code, reason_phrase = 403, "Forbidden"


    return charset, status_code, reason_phrase, content_type, btext


# DELETE Code
def handle_DELETE(words):

    if words[1] == "/":
        requested_file = "index.html"
    else:
        requested_file = words[1][1:]

    file_path = doc_root + requested_file

    # Status Code, Reason Phrase header
    accept_lang, content_type = handle_req_headers(words)
    status_code, reason_phrase, btext = handle_codes(words, accept_lang)

    content_type = 'text/html'
    charset = 'UTF-8'

    if status_code == 406:
        return charset, status_code, reason_phrase, content_type, btext

    if os.access(file_path, os.F_OK):
        shutil.move(file_path, trash_path)
        btext = '<h1>File Deleted Successfully !</h1>'.encode()
        status_code, reason_phrase = 200, "OK"
    
    else:
        btext = '<h1>File Not Present On The Server !</h1>'.encode()
        status_code, reason_phrase = 200, "OK"

    return charset,status_code, reason_phrase, content_type, btext


# POST Code
def handle_POST(bin_request, dtime, content_length_flag):

    bin_words = bin_request.split()

    btext = "<h1>No Action Taken !</h1>".encode()
    status_code, reason_phrase = 200, "OK"

    try:
        i = bin_words.index(b'Content-Type:')
        content_type = bin_words[i+1].decode()
    except:
        content_type = None

    if not content_length_flag:        
        request = bin_request.decode()
    
    post_db = open(post_file_path, 'a')
    
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
                upload_file_path = files_dir + file_name
                try:
                    f = open(upload_file_path, 'wb')
                    f.write(file_data)
                    f.close()
                    btext = open(doc_root + '/success.html',mode='rb').read()
                    post_db.write("File Uploaded : " + file_name + "\n\n")
                    status_code, reason_phrase = 200, "OK"
                except:
                    btext = "<h1>Some Error Occurred !</h1>".encode()
                    status_code, reason_phrase = 200, "OK"
            else:
                temp_data = entry.decode().split()
                name = temp_data[2].split('"')[1] + ": "
                # Writing One Form Element 
                for i in range(3,len(temp_data) - 1):
                    name += temp_data[i] + " "
                try:
                    post_db.write(name + "\n")
                    btext = open(doc_root + '/success.html',mode='rb').read()
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
        btext = open(doc_root + '/success.html',mode='rb').read()
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
        btext = open(doc_root + '/success.html',mode='rb').read()
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
    buffer_size = 8192
    bin_request = connectionSocket.recv(buffer_size)
    bin_words = bin_request.split()
    content_length_flag = False

    if b'Content-Length:' in bin_words:
        content_length_flag = True
        while True:
            data = connectionSocket.recv(buffer_size)
            bin_request += data
            if len(data) <= buffer_size * 0.80:
                break

    method = bin_words[0].decode()
    temp = bin_request.splitlines()
    # Making list of date, time in required format
    dtime = time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
    # GET
    charset, status_code, reason_phrase, content_type, btext = b'null', 0, 0, 0, b'null'

    if method == "GET":
        
        request =  bin_request.decode()
        words = request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_GET(words)

        print("Request:")
        print(f"Thread ID: {threading.get_ident()}, Total Threads: {threading.active_count()}\n")
        print(request)
        print("\n")

        if status_code == -1:
            connectionSocket.close()
            return


    elif method == "POST":
        print(bin_request)
        bin_words = bin_request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_POST(bin_request, dtime, content_length_flag)


    elif method == "PUT":
        print(bin_request)
        charset, status_code, reason_phrase, content_type, btext = handle_PUT(bin_request)


    elif method == "HEAD":
        request =  bin_request.decode()
        print("Request:")
        print(f"Thread ID: {threading.get_ident()}, Total Threads: {threading.active_count()}\n")
        print(request)
        print("\n")
        words = request.split()
        charset, status_code, reason_phrase, content_type, btext = handle_HEAD(words)


    elif method == "DELETE":
        request =  bin_request.decode()
        print("Request:")
        print(f"Thread ID: {threading.get_ident()}, Total Threads: {threading.active_count()}\n")
        print(request)
        print("\n")
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
        logger_2_ = logging.LoggerAdapter(logger_2, extra)
        if status_code == 404:
            logger_2_.error('File Not Found')
        elif status_code == 400:
            logger_2_.error('Bad Request')
        elif status_code == 406:
            logger_2_.error('Language Not Supported')
        else:
            # Need for some other status codes
            pass
    
    if btext and len(btext) != 0:
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
    if content_type and not charset:
        string += "Content-Type: {};\n".format(content_type)
    
    # Checking if content is present or not.
    if btext:
        string += "Content-Length: {}\n\n".format(len(string.encode() + btext))
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
    print("\nServer Closed !")
    serverSocket.close()
