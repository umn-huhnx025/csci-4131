#!/usr/bin/env python3

## NOTES ##
# - My favorite places HTML file is called places.html
# - In my form, the additional info URL field is named additionalinfotext and
#    the additional info text field is named additionalinfo
# - The root directory of the web server can be changed with the ROOT variable

## BONUS FEATURES ##
# - PUT requests
# - DELETE requests
# - Support for serving binary files

import datetime
import os
import signal
import socket
import sys
import threading
import urllib.parse

from stat import ST_MODE, S_IROTH, S_IWOTH

DEFAULT_PORT = 9001

# How many bytes to read from the socket at a time
RECV_SIZE = 1024

# Location of files to be served
ROOT = '.'

# Allowed methods for OPTIONS requests
file_options = {
    'places.html': ['OPTIONS', 'GET', 'HEAD'],
    'form.html': ['OPTIONS', 'GET', 'HEAD', 'POST'],
    '': ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE'],
}

# HTTP codes and messages
status_message = {
    200: 'OK',
    201: 'Created',
    301: 'Moved Permanantly',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
}


def main():
    MAX_CONN = 10
    host = ''

    # Use port from command line, or default if none was provided
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    except ValueError:
        # Couldn't parse arg as int
        port = DEFAULT_PORT

    # Set up socket
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((host, port))
    except Exception:
        print('Failed to create socket')
        raise

    serversocket.listen(MAX_CONN)
    print('Listening on port', port)

    def int_handler(signum, frame):
        '''Close server socket on SIGINT before exiting'''
        print('\b\bShutting down server')
        serversocket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, int_handler)

    os.chdir(ROOT)

    while True:
        (clientsocket, address) = serversocket.accept()
        server = threading.Thread(target=serve_http, args=[
            clientsocket, address])
        server.daemon = True
        server.start()


def serve_http(clientsocket, address):
    '''Entrypoint for each new HTTP request'''
    ip = address[0]
    port = address[1]

    try:
        time = datetime.datetime.now()
        time = time.strftime('%d/%b/%Y:%X')

        # Read request
        raw_request = b''
        while True:
            chunk = clientsocket.recv(RECV_SIZE)
            raw_request += chunk
            if len(chunk) < RECV_SIZE:
                break
        raw_request = raw_request.decode()

        # Parse fields
        request_lines = raw_request.split('\r\n')
        request = request_lines[0]
        request_fields = request.split()
        method = request_fields[0]
        uri = request_fields[1]
        version = request_fields[2]
        body_index = request_lines.index('') + 1
        request_headers_list = request_lines[1:body_index-1]
        request_headers = {}
        for el in request_headers_list:
            s = el.split(':')
            k = s[0]
            v = ':'.join(s[1:])[1:]
            request_headers[k] = v

        request_body = '\r\n'.join(request_lines[body_index:])

        # Read requested file
        rel_path = uri[1:].split('?')[0]
        if rel_path.split('/')[-1] == 'csumn':
            content = ''
            status = 301
            headers = 'Location: https://www.cs.umn.edu'
        else:
            try:
                # Call the appropriate HTTP method
                content, status, headers = methods[method](
                    rel_path, request_body)
            except KeyError:
                # Method not allowed
                content, status, headers = error(405)

        if not acceptable(request_headers, rel_path):
            content, status, headers = error(406)

        # Format response
        response = '{} {} {}\r\n'.format(
            version, status, status_message[status])
        response += headers + '\r\n'
        response = response.encode()
        try:
            content = content.encode()
        except AttributeError:
            # Content is binary, already encoded
            pass
        response += content

        # Log request
        print('{}:{} - - [{}] "{}" {} {}'.format(ip,
                                                 port, time, request, status, len(response)))

        # Respond to client
        clientsocket.send(response)

    finally:
        clientsocket.close()


################################################################################
#############################     HTTP METHODS     #############################
################################################################################


def get(path, data):
    # HTTP GET method
    headers = ''

    # Read requested file
    if not os.path.exists(path):
        # File does not exist
        return error(404)
    elif os.path.exists(path) and not others_can_read(path):
        # Permissions don't allow this file to be read by others
        return error(403)
    else:
        # Everything should be OK
        status = 200
        try:
            with open(path, 'r') as f:
                content = f.read()
        except UnicodeDecodeError:
            # File is binary
            with open(path, 'rb') as f:
                content = f.read()
        return content, status, headers


def head(path, data):
    _, status, headers = get(path, data)
    return '', status, headers


def put(path, data):
    dirname = os.path.dirname(path)
    # Directory must be world readable and writeable to put files in it
    if os.path.exists(dirname) and not (others_can_read(dirname) and others_can_write(dirname)):
        return error(403)

    if os.path.exists(path) and not others_can_read(path):
        return error(403)

    content = ''
    status = 200 if os.path.exists(path) else 201
    headers = 'Content-Location: {}'.format(path)
    try:
        with open(path, 'w') as f:
            f.write(data)
    except PermissionError:
        return error(403)
    return content, status, headers


def post(path, data):
    # Parse form data
    data_list = data.split('&')

    # Dictionary of all form data keys and values
    data = {}

    for el in data_list:
        try:
            k, v = el.split('=')
        except ValueError:
            continue

        # Bring back escaped characters
        v = urllib.parse.unquote_plus(v)

        data[k] = v

    if path == '':
        # Coming from form.html
        try:
            # Extract values
            placename = data['placename']
            addr1 = data['addressline1']
            addr2 = data['addressline2']
            open_time = data['opentime']
            close_time = data['closetime']
            info_text = data['additionalinfotext']
            info_url = data['additionalinfo']
        except KeyError:
            # Some parameter was ommitted
            return error(400)

        # Response
        status = 200
        headers = ''
        content = '\n'.join((
            "<html>",
            "<body>",
            "<h2> Following Form Data Submitted Successfully </h2>",
            "<p> Place Name: {} <p>",
            "<p> Address Line1:  {} <p>",
            "<p> Address Line2: {} <p>",
            "<p> Open Time: {} <p>",
            "<p> Close Time: {} <p>",
            "<p> Additional Info Text: {} <p>",
            "<p> Additional Info URL: <a href=\"{}\">{}</a> <p>",
            "</body>",
            "</html>",
        )).format(placename, addr1, addr2, open_time, close_time, info_text, info_url, info_url)
        return content, status, headers
    elif os.path.exists(path):
        if not others_can_read(path):
            return error(403)
        else:
            return error(405)
    else:
        return error(404)


def delete(path, data):
    if os.path.exists(path):
        dirname = os.path.dirname(path)
        # Directory must be world readable and writeable to delete files in it
        if not (others_can_read(dirname) and others_can_write(dirname)):
            return error(403)

        # File must be world readable and writeable to delete
        if not (others_can_read(path) and others_can_write(path)):
            return error(403)
        else:
            os.remove(path)
            headers = ''
            content = ''
            status = 200
            return content, status, headers
    else:
        return error(404)


def options(path, data):
    try:
        m = ', '.join(file_options[path])
    except KeyError:
        return error(400)

    status = 200
    headers = 'Allow: {}'.format(m)
    content = ''
    return content, status, headers


# Map HTTP request methods to their corresponding functions
methods = {
    'GET': get,
    'HEAD': head,
    'POST': post,
    'PUT': put,
    'DELETE': delete,
    'OPTIONS': options,
}

################################################################################
###########################     HELPER FUNCTIONS     ###########################
################################################################################


def others_can_read(path):
    return os.stat(path)[ST_MODE] & S_IROTH


def others_can_write(path):
    return os.stat(path)[ST_MODE] & S_IWOTH


def error(status):
    '''Make a response from an error code'''
    if status == 403 or status == 404 or status == 405:
        headers = 'Connection: close'
    else:
        headers = ''
    try:
        with open(str(status) + '.html', 'r') as f:
            content = f.read()
    except IOError:
        content = '{} - {}'.format(status, status_message[status])
    return content, status, headers


def acceptable(request_headers, path):
    '''Check if the request's acceptable types match the requested resource'''
    if 'Accept' not in request_headers:
        return True

    accept = request_headers['Accept'].split(',')
    for i in list(range(len(accept))):
        accept[i] = accept[i].split(';')[0]

    if '*/*' in accept:
        return True

    ext = path.split('.')[-1]
    if ext == 'html' or ext == 'htm':
        return 'text/*' in accept or 'text/html' in accept
    elif ext == 'js':
        return 'text/*' in accept or 'text/javascript' in accept
    elif ext == 'css':
        return 'text/*' in accept or 'text/css' in accept
    elif ext == 'css':
        return 'image/*' in accept or 'image/png' in accept
    elif ext == 'jpg' or ext == 'jpeg':
        return 'image/*' in accept or 'image/jpeg' in accept
    elif ext == 'gif':
        return 'image/*' in accept or 'image/gif' in accept
    else:
        return False


if __name__ == '__main__':
    main()
