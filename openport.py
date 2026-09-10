import socket

def test_tracker(host, port):
    try:
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((host, port))
        tracker_socket.send("GET_PEERS".encode('utf-8'))
        response = tracker_socket.recv(1024).decode('utf-8')
        print(f"Response from tracker: {response}")
        tracker_socket.close()
    except Exception as e:
        print(f"[-] Error communicating with tracker: {e}")

if __name__ == "__main__":
    test_tracker('127.0.0.1', 8000)
