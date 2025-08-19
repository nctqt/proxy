import socket

# flow is: request -> proxy_request to destination -> response -> proxy_response to client

DEBUG_MODE = True

def dprint(message):
    if DEBUG_MODE:
        print(message)
print("\n")

# TCP socket server (single-threaded)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 7654)
server_socket.bind(server_address)
server_socket.listen(1)
print(f"Server listening on {server_address[0]}:{server_address[1]}")

# client socket
client_socket, client_address = server_socket.accept()
print(f"Accepted connection from {client_address}")

# read data
request_data = b""
while b"\r\n\r\n" not in request_data:
    chunk = client_socket.recv(1024)
    if not chunk:
        break
    request_data += chunk

# parse data
dprint(f"Request data: {request_data}")
first_line = request_data.split(b'\r\n', 1)[0]
dprint(f"first line: {first_line}")
split_line = first_line.split(b' ')
method, url, version = split_line[0], split_line[1], split_line[2]
dprint(f"Method: {method.decode()} URL: {url.decode()} Version: {version.decode()}")

# craft new request
proxy_request = request_data

# send new request
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = url.decode().lstrip("http://www.").rstrip("/")
dprint(hostname)
ip_address = socket.gethostbyname(hostname)
dest_address = (ip_address, 80)
proxy_socket.connect(dest_address)
proxy_socket.sendall(proxy_request)

# receive response
response = b""
while True:
    chunk = proxy_socket.recv(4096)
    if not chunk:
        break
    response += chunk

proxy_socket.close()

# manipulate response
proxy_response = response

# proxy response
client_socket.sendall(proxy_response)

# close
client_socket.close()
server_socket.close()

