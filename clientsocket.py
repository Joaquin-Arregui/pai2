from Crypto.Random import get_random_bytes
from datetime import datetime
import socket
import hmac

def ask_sender():
    try:
        sender = int(input('Please enter the origin account: '))
    except ValueError:
        print('You must enter a whole number')
        return ask_sender()
    return sender

def ask_destination():
    try:
        destination = int(input('Please enter the destination account: '))
    except ValueError:
        print('You must enter a whole number')
        return ask_destination()
    return destination

def ask_amount():
    try:
        amount = float(input("Please enter the amount to send(Separated by '.'): "))
    except ValueError:
        print('You must enter a number, example: XX.Y')
        return ask_amount()
    return amount


def create_message():
    sender = ask_sender()
    destination = ask_destination()
    if sender == destination:
        print('The destination account must be different to the origin account')
        return create_message()
    amount = ask_amount()
    if amount <= 0:
        print('The amount must be positive')
        amount = ask_amount()
    nonce = get_random_bytes(32).hex()
    date = datetime.now().strftime('%d/%m/%Y-%H:%M')
    msg = str(sender) + ' ' + str(destination) + ' ' + str(amount) + ' ' + str(date) + ' ' + str(nonce)
    return msg

def create_mac(msg):
    key = b'\\x1e\\n\\xb9\\x08\\x9dZ^\\xc1EZ\\xe3\\xb1\\\\\\xa6d\\x11\\tj\\x10\\x96\\xc8\\x9dA\\xb6\\xb4HX\\xb2\\x86)^\\x90'
    mac = hmac.new(key, msg.encode('utf-8'), digestmod='sha256')
    return mac

def client():
    HOST = "127.0.0.1"
    PORT = 3030
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = create_message()
        mac = create_mac(msg)
        mac_hex = mac.digest().hex()
        data = msg + ' --|-- ' + mac_hex
        s.sendall(data.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
    
    print(f"Received\n{data!r}")

if __name__ == "__main__":
    client()