from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import threading
import smtplib
import socket
import hmac
import time

def create_mac(msg):
    key = b'\\x1e\\n\\xb9\\x08\\x9dZ^\\xc1EZ\\xe3\\xb1\\\\\\xa6d\\x11\\tj\\x10\\x96\\xc8\\x9dA\\xb6\\xb4HX\\xb2\\x86)^\\x90'
    mac = hmac.new(key, msg.encode('utf-8'), digestmod='sha256')
    return mac

def get_nonce():
    with open('nonces.txt', 'r') as f:
        content = f.read()
    return content.split('\n')

def add_log(text):
    date = datetime.now()
    logname = date.strftime("%m-%y") + '.log'
    with open('logs/'+logname, 'a') as f:
        if text == 'The data has been recieved succesfully':
            f.write('+ Success\n')
        elif text == 'The data has been manipulated with a Man-in-the-middle Attack':
            f.write('- Man-In-The-Middle\n')
        elif text == 'The data message has been duplicated with a replay attack':
            f.write('- Replay\n')
            
def send_report():
    date = datetime.now()
    logname = date.strftime("%m-%y") + '.log'
    with open('logs/'+logname, 'r') as f:
        content = f.readlines()
    success = 0
    mitm_attack = 0
    r_attack = 0
    for c in content:
        if c.split()[0] == '+':
            success += 1
        else:
            if c.split()[1] == 'Man-In-The-Middle':
                mitm_attack += 1
            elif c.split()[1] == 'Replay':
                r_attack += 1
    
    
    total_messages = mitm_attack + r_attack + success
    success_percentage = (success / total_messages) if total_messages > 0 else 0
    sender_email = "insegus.ssii4@hotmail.com"
    receiver_email = 'joaarrdia@alum.us.es'
    password = "Insegus4@"
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    date = datetime.now()
    message['Subject'] = date.strftime("%B") + "'s monthly report from Insegus."
    body = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                    }
                    h2 {
                        color: #333333;
                    }
                    p {
                        margin-bottom: 10px;
                    }
                </style>
            </head>
            <body>
                <p>Total Messages Received: """ + str(total_messages) + """</p>
                <p>Successful Verifications: """ + str(success) + """</p>
                <p>Man-In-The-Middle Attacks: """ + str(mitm_attack) + """</p>
                <p>Replay Attacks: """ + str(r_attack) + """</p>
                <p>Ratio of Success (KPI): """ + "{:.2f}".format(success_percentage) + """</p>
            </body>
        </html>
        """
    message.attach(MIMEText(body, 'html'))
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
                 

def server():
    HOST = "127.0.0.1"
    PORT = 3030
    nonce_list = get_nonce()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    
                    if data:
                        data_string = data.decode('utf-8')
                        msg = data_string.split(' --|-- ')[0]
                        mac = data_string.split(' --|-- ')[-1]
                        nonce = msg.split()[-1]
                        date = msg.split()[-2]
                        date_check = datetime.now().strftime('%d/%m/%Y-%H:%M')
                        mac_check = create_mac(msg).digest().hex()
                        res = ''
                        
                        if date == date_check:
                            if nonce not in nonce_list:
                                with open('nonces.txt', 'a') as f:
                                    f.write(nonce + '\n')
                                    nonce_list.append(nonce)
                                if mac == mac_check:
                                    res = 'The data has been recieved succesfully'
                                else:
                                    res = 'The data has been manipulated with a Man-in-the-middle Attack'
                            else:
                                res = 'The data message has been duplicated with a replay attack'
                        else:
                            res = 'The data has been retained with a Man-in-the-middle Attack'
                        add_log(res)
                        conn.sendall(res.encode('utf-8'))
                        break

def main():
    def report_scheduler():
        while True:
            send_report()
            time.sleep(60)

    server_thread = threading.Thread(target=server)
    report_thread = threading.Thread(target=report_scheduler)

    server_thread.start()
    report_thread.start()
    
    server_thread.join()
    report_thread.join()

if __name__ == "__main__":
    main()