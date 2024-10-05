from colorama import Fore, Style, init
import socket
import threading
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PORT = 60000
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!Disconnect"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "chanhengmenh@gmail.com"  # Your Gmail email
SMTP_PASSWORD = "fwrz ugqv nqar dfwu"  # Your Gmail app password

USERNAME = "Chanheng Menh"  # Fixed username

def send_email(send_email, receive_email, subject, message):
    """Sends an email using SMTP."""
    try:
        # Set up SMTP server connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(send_email, SMTP_PASSWORD)

        # Prepare email content
        msg = MIMEMultipart()
        msg['From'] = send_email
        msg['To'] = receive_email
        msg['Subject'] = subject

        body = f"Subject: {subject}\n\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(send_email, receive_email, msg.as_string())
        server.quit()

        # Success message in green
        print(f"{Fore.GREEN}Email sent to {receive_email}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error occurred: {e}{Style.RESET_ALL}")

def connect():
    """Establish connection to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print(f"{Fore.CYAN}Connected to server at {ADDR}{Style.RESET_ALL}")
        return client
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Unable to connect to server: {e}{Style.RESET_ALL}")
        return None

def receive(client):
    """Continuously receives messages from the server."""
    while True:
        try:
            message = client.recv(HEADER).decode(FORMAT)
            if message:
                sys.stdout.write("\r" + f"{Fore.RED}{message}{Style.NORMAL}\nYou: ")
                sys.stdout.flush()
            else:
                break
        except Exception:
            break

def handle_input(client):
    """Handles user input and sends it to the server."""
    send(client, USERNAME)  # Send fixed username as the first message
    while True:
        msg = input(f"{Fore.MAGENTA}{USERNAME}: {Style.RESET_ALL}")
        if msg == '!!':
            break
        send(client, f"{Fore.MAGENTA}{USERNAME}: {msg}{Style.RESET_ALL}")

def send(client, msg):
    """Send message to server."""
    try:
        client.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to send message: {e}{Style.RESET_ALL}")

def prompt_for_email_details():
    """Prompt the user for email details (recipient, subject, and text)."""
    # Input recipient email in cyan
    recipient_email = input(f"{Fore.CYAN}You wanna send mail to (email): {Style.RESET_ALL}")

    # Input email subject in green
    subject = input(f"{Fore.GREEN}Email Subject: {Style.RESET_ALL}")

    # Input email text in blue
    email_text = input(f"{Fore.BLUE}Email Text: {Style.RESET_ALL}")

    return recipient_email, subject, email_text

def start():
    """Main function to run the client."""
    init()

    connection = connect()
    if not connection:
        return

    # Start thread to receive messages
    threading.Thread(target=receive, args=(connection,), daemon=True).start()

    while True:
        # Prompt for email details with different colors
        recipient_email, subject, email_text = prompt_for_email_details()

        # Send email
        send_email(SMTP_EMAIL, recipient_email, subject, email_text)

        # Optional: check if the user wants to send another email
        continue_sending = input(f"{Fore.YELLOW}Do you want to send another email? (y/n): {Style.RESET_ALL}").lower()
        if continue_sending != 'y':
            break

    send(connection, DISCONNECT_MESSAGE)
    connection.close()
    print('Disconnected')

start()
