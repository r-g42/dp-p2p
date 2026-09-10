import socket
import threading
import os
from cryptography.fernet import Fernet
import numpy as np
import time

def gaussian_mechanism(value, sensitivity, epsilon):
    delta = 1
    stddev = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon
    noise = np.random.normal(0, stddev)
    return value + noise

class PeerNode:
    def __init__(self, host, port, key, epsilon=1.0):
        self.host = host
        self.port = port
        self.peers = []
        self.key = key
        self.cipher_suite = Fernet(self.key)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.epsilon = epsilon
        print(f"[+] Node started on {self.host}:{self.port}")

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[+] Connected to {addr}")
            self.peers.append(client_socket)
            threading.Thread(target=self.handle_peer, args=(client_socket,)).start()

    def handle_peer(self, client_socket):
        while True:
            try:
                encrypted_message = client_socket.recv(4096)
                if encrypted_message:
                    message = self.cipher_suite.decrypt(encrypted_message).decode('utf-8')
                    print(f"[+] Received: {message}")
            except Exception as e:
                print(f"[-] Error handling peer: {e}")
                client_socket.close()
                self.peers.remove(client_socket)
                break

    def send_message(self, message):
        encrypted_message = self.cipher_suite.encrypt(message.encode('utf-8'))
        for peer in self.peers:
            try:
                peer.send(encrypted_message)
            except Exception as e:
                print(f"[-] Failed to send message to peer: {e}")
                peer.close()
                self.peers.remove(peer)

    def share_file(self, file_path):
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            metadata = f"{os.path.basename(file_path)}:{file_size}"
            self.send_message(metadata)
            with open(file_path, 'rb') as f:
                while (chunk := f.read(4096)):
                    noisy_chunk = gaussian_mechanism(chunk, sensitivity=1.0, epsilon=self.epsilon)
                    encrypted_chunk = self.cipher_suite.encrypt(noisy_chunk)
                    for peer in self.peers:
                        try:
                            peer.send(encrypted_chunk)
                        except Exception as e:
                            print(f"[-] Failed to send file chunk to peer: {e}")
                            peer.close()
                            self.peers.remove(peer)
        else:
            print("[-] File not found")

    def connect_to_tracker(self, tracker_host, tracker_port):
        try:
            print(f"Connecting to tracker at {tracker_host}:{tracker_port}")
            tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tracker_socket.connect((tracker_host, tracker_port))
            
            # Register with the tracker
            registration_message = f"REGISTER {self.host}:{self.port}\n"
            tracker_socket.send(registration_message.encode('utf-8'))
            print(f"Sent registration message: {registration_message.strip()}")

            # Allow some time for registration to be processed
            time.sleep(2)

            # Request peer list
            tracker_socket.send("GET_PEERS\n".encode('utf-8'))
            peer_list = tracker_socket.recv(1024).decode('utf-8').split(",")
            print("Received peer list from tracker:", peer_list)
            for peer in peer_list:
                ip, port = peer.split(":")
                self.connect_to_peer(ip, int(port))
            tracker_socket.close()
        except Exception as e:
            print(f"Failed to connect to tracker at {tracker_host}:{tracker_port} - {e}")

    def connect_to_peer(self, host, port, retries=3, delay=2):
        for attempt in range(retries):
            try:
                print(f"Attempting to connect to peer: {host}:{port} (Attempt {attempt+1}/{retries})")
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((host, port))
                self.peers.append(peer_socket)
                threading.Thread(target=self.handle_peer, args=(peer_socket,)).start()
                print(f"[+] Connected to peer {host}:{port}")
                return
            except ConnectionRefusedError:
                print(f"[-] Connection refused by peer {host}:{port}")
            except Exception as e:
                print(f"[-] Unexpected error connecting to peer {host}:{port} - {e}")
            time.sleep(delay)
        print(f"[-] Failed to connect to peer {host}:{port} after {retries} attempts")

if __name__ == "__main__":
    key = Fernet.generate_key()
    ports = [5003, 5004, 5005]
    nodes = []

    for port in ports:
        node = PeerNode('127.0.0.1', port, key)
        nodes.append(node)
        threading.Thread(target=node.accept_connections).start()

    time.sleep(2)
    tracker_host = '127.0.0.1'
    tracker_port = 8000
    nodes[0].connect_to_tracker(tracker_host, tracker_port)

    while True:
        command = input("Enter command (message/file): ")
        if command == "message":
            msg = input("Enter message: ")
            nodes[0].send_message(msg)
        elif command == "file":
            file_path = input("Enter file path: ")
            nodes[0].share_file(file_path)
