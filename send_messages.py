# send_messages.py
import socket
import time

def send_message_to_node(host, port, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
            print(f"Sent message to {host}:{port}")
    except Exception as e:
        print(f"Failed to send message to {host}:{port} - {e}")

if __name__ == "__main__":
    # List of nodes to send messages to
    nodes = [
        ('127.0.0.1', 5000),
        ('127.0.0.1', 5001),
        ('127.0.0.1', 5002)
    ]

    message = "Test message for differential privacy"

    for host, port in nodes:
        send_message_to_node(host, port, message)
        time.sleep(1)  # Delay between messages to avoid overwhelming the network

