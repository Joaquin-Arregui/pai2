from Crypto.Random import get_random_bytes
from datetime import datetime
import threading
import random
import socket
import hmac
import time

def create_message():
    sender = random.randint(1000,9999)
    destination = random.randint(1000,9999)
    amount = random.randint(0,9999)
    nonce = get_random_bytes(32).hex()
    date = datetime.now().strftime('%d/%m/%Y-%H:%M')
    msg = str(sender) + ' ' + str(destination) + ' ' + str(amount) + ' ' + str(date) + ' ' + str(nonce)
    return msg

def create_mac_with_key(msg):
    key = b'\\x1e\\n\\xb9\\x08\\x9dZ^\\xc1EZ\\xe3\\xb1\\\\\\xa6d\\x11\\tj\\x10\\x96\\xc8\\x9dA\\xb6\\xb4HX\\xb2\\x86)^\\x90'
    mac = hmac.new(key, msg.encode('utf-8'), digestmod='sha256')
    return mac

def create_mac_without_key(msg):
    mac = hmac.new(msg.encode('utf-8'), digestmod='sha256')
    return mac

def test_correct():
    HOST = "127.0.0.1"
    PORT = 3030
    
    print("Correct message")
    msg = create_message()
    mac = create_mac_with_key(msg)
    mac_hex = mac.digest().hex()
    data_sent = msg + ' --|-- ' + mac_hex
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data_sent.encode('utf-8'))
        data_recv = s.recv(1024).decode('utf-8')
    print(f"Sent: {data_sent!r}")
    print(f"Received: {data_recv!r}")

def test_change_message():
    HOST = "127.0.0.1"
    PORT = 3030

    print('Change message')
    msg = create_message()
    mac = create_mac_with_key(msg)
    msg2 = create_message()
    mac_hex = mac.digest().hex()
    data_correct = msg + ' --|-- ' + mac_hex
    data_sent = msg2 + ' --|-- ' + mac_hex
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data_sent.encode('utf-8'))
        data_recv = s.recv(1024).decode('utf-8')
    print(f"Correct message: {data_correct!r}")
    print(f"Sent: {data_sent!r}")
    print(f"Received: {data_recv!r}")
    
def test_change_mac():
    HOST = "127.0.0.1"
    PORT = 3030
    
    print('Change mac')
    msg = create_message()
    mac = create_mac_with_key(msg)
    mac_hex = mac.digest().hex()
    data_correct = msg + ' --|-- ' + mac_hex
    data_sent = data_correct + '1234'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data_sent.encode('utf-8'))
        data_recv = s.recv(1024).decode('utf-8')
    print(f"Correct message: {data_correct!r}")
    print(f"Sent: {data_sent!r}")
    print(f"Received: {data_recv!r}")
    
def test_retain_message():
    HOST = "127.0.0.1"
    PORT = 3030
    
    print('Retained message')
    msg = create_message()
    mac = create_mac_with_key(msg)
    mac_hex = mac.digest().hex()
    data_sent = msg + ' --|-- ' + mac_hex
    time.sleep(60)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data_sent.encode('utf-8'))
        data_recv = s.recv(1024).decode('utf-8')
    print(f"Sent: {data_sent!r}")
    print(f"Received: {data_recv!r}")
    
def test_replay_message():
    HOST = "127.0.0.1"
    PORT = 3030
    
    print('Replay attack. sent 5 times')
    msg = create_message()
    mac = create_mac_with_key(msg)
    mac_hex = mac.digest().hex()
    data_sent = msg + ' --|-- ' + mac_hex
    for _ in range(5):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(data_sent.encode('utf-8'))
            data_recv = s.recv(1024).decode('utf-8')
        print(f"Sent: {data_sent!r}")
        print(f"Received: {data_recv!r}")

def test():
    def correct():
        while True:
            test_correct()
            time.sleep(30)

    def attack():
        while True:
            time.sleep(30)
            for function in [test_change_message, test_change_mac, 'skip', test_replay_message]:
                if not function == 'skip':
                    function()
                    if function == test_change_mac:
                        test_retain_message()
                time.sleep(60)

    correct_thread = threading.Thread(target=correct)
    attack_thread = threading.Thread(target=attack)

    correct_thread.start()
    attack_thread.start()
    
    correct_thread.join()
    attack_thread.join()

if __name__ == "__main__":
    test()