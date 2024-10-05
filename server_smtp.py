from colorama import Fore, Style, init
import threading
import socket
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PORT = 60000
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!Disconnect"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "chanhengmenh@gmail.com"  
SMTP_PASSWORD = "fwrz ugqv nqar dfwu"

def send_email_notification(sender_email, recipient_email, subject, message_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        body = f"Subject: {subject}\n\n{message_content}"
        msg.attach(MIMEText(body, 'plain'))

        smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_server.starttls()
        smtp_server.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        smtp_server.quit()

        print(f"[INFO] Notification email sent to {recipient_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email notification: {e}")

def handle_client(conn, addr):
    print(f"[New Connection] {addr} connected.")
    try:
        username = conn.recv(HEADER).decode(FORMAT)
        print(f"[New User] {username} connected.")
        broadcast(f"{Fore.YELLOW}{username} has joined the chat.{Style.NORMAL}".encode(FORMAT), conn)
        while True:
            msg = conn.recv(HEADER).decode(FORMAT)
            if not msg or msg == DISCONNECT_MESSAGE:
                break
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            broadcast(msg.encode(FORMAT), conn)
            print(f"\r[{timestamp}] {msg}")
    finally:
        with clients_lock:
            clients.remove(conn)
        broadcast(f"{Fore.RED}{username} has left the chat.{Style.NORMAL}".encode(FORMAT))
        conn.close()

def broadcast(message, sender=None):
    with clients_lock:
        for client in clients.copy():
            if client != sender:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"[ERROR] Unable to send message: {e}")
                    clients.remove(client)

def start():
    init()
    print(f"[Listening] Server is listening on {SERVER}")
    server.listen()
    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.add(conn)
        threading.Thread(target=handle_client, args=(conn, addr)).start()

print("[Starting] Server started...")
start()
