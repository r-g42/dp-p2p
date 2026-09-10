import socket
import threading

class TrackerServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[+] Tracker started on {self.host}:{self.port}")

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[+] Peer connected: {addr}")
            threading.Thread(target=self.handle_peer, args=(client_socket,)).start()

    def handle_peer(self, client_socket):
        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.startswith("REGISTER"):
                        _, peer_info = message.split(" ", 1)
                        peer_addr = tuple(peer_info.split(":"))
                        if peer_addr not in self.peers:
                            self.peers.append(peer_addr)
                            print(f"Registered new peer: {peer_addr}")
                        else:
                            print(f"Peer already registered: {peer_addr}")
                    elif message == "GET_PEERS":
                        peer_list = ",".join([f"{p[0]}:{p[1]}" for p in self.peers])
                        client_socket.send(peer_list.encode('utf-8'))
            except Exception as e:
                print(f"[-] Error handling peer: {e}")
                client_socket.close()
                break

if __name__ == "__main__":
    tracker = TrackerServer('127.0.0.1', 8000)
    tracker.accept_connections()
