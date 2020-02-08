import json
import socket
import socketserver

from core.envs import UnityEnv, env_unity


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


class ParseBytes:
    pass


class TcpHandlerStream(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, *args, **kwargs):
        self.data = None
        super().__init__(*args, **kwargs)

    def handle(self):
        env_unity.request = self.wfile
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.rfile.readline().strip()
            self.data = json.loads(self.data)
            env_unity.data = self.data
            env_unity.client_address = self.client_address[0]
            if not self.data:
                break

    def finish(self):
        print("FECHOU!")
        super().finish()


class TcpHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, *args, **kwargs):
        self.data = None
        super().__init__(*args, **kwargs)

    def handle(self):
        env_unity.request = self.request
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            print("EU ESTOU TROLANDO VOCÊS")
            env_unity.data = self.data
            env_unity.client_address = self.client_address[0]
            if not self.data:
                break

    def finish(self):
        super().finish()


def tcp_server(host, port):
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((host, port), TcpHandlerStream) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print(f"TCP Server running on {host}:{port}")
        server.serve_forever()
    return True
