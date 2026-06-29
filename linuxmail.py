#!/usr/bin/env python3

import imaplib
import smtplib
import email
import os
import getpass
from email.mime.text import MIMEText

CONFIG_FILE = os.path.expanduser("~/.linuxmail_config")


def link_account():
    print("\n=== Link Email Account ===")
    email_user = input("Email: ")
    password = getpass.getpass("App Password: ")

    print("\nChoose provider:")
    print("1. Gmail")
    print("2. Other")
    choice = input("> ")

    if choice == "1":
        imap_server = "imap.gmail.com"
        smtp_server = "smtp.gmail.com"
        imap_port = 993
        smtp_port = 587
    else:
        imap_server = input("IMAP server: ")
        smtp_server = input("SMTP server: ")
        imap_port = int(input("IMAP port: "))
        smtp_port = int(input("SMTP port: "))

    with open(CONFIG_FILE, "w") as f:
        f.write("\n".join([
            email_user,
            password,
            imap_server,
            smtp_server,
            str(imap_port),
            str(smtp_port)
        ]))

    print("✅ Account saved!")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ No account linked.")
        return None

    with open(CONFIG_FILE, "r") as f:
        data = f.read().splitlines()

    if len(data) < 6:
        print("❌ Config broken. Relink account.")
        return None

    return {
        "email": data[0],
        "password": data[1],
        "imap": data[2],
        "smtp": data[3],
        "imap_port": int(data[4]),
        "smtp_port": int(data[5]),
    }


def inbox():
    config = load_config()
    if not config:
        return

    try:
        mail = imaplib.IMAP4_SSL(config["imap"], config["imap_port"])
        mail.login(config["email"], config["password"])
        mail.select("inbox")

        _, messages = mail.search(None, "ALL")
        ids = messages[0].split()

        print(f"\n📬 Last 10 emails:\n")

        for i in ids[-10:][::-1]:
            _, msg_data = mail.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            print("From:", msg.get("From"))
            print("Subject:", msg.get("Subject"))
            print("-" * 40)

        mail.logout()

    except Exception as e:
        print("❌ Error:", e)


def send_email():
    config = load_config()
    if not config:
        return

    to = input("To: ")
    subject = input("Subject: ")
    body = input("Message: ")

    msg = MIMEText(body)
    msg["From"] = config["email"]
    msg["To"] = to
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP(config["smtp"], config["smtp_port"])
        server.starttls()
        server.login(config["email"], config["password"])
        server.send_message(msg)
        server.quit()

        print("✅ Sent!")

    except Exception as e:
        print("❌ Failed:", e)


def menu():
    while True:
        print("\n1. Inbox")
        print("2. Send")
        print("3. Link account")
        print("4. Exit")

        choice = input("> ")

        if choice == "1":
            inbox()
        elif choice == "2":
            send_email()
        elif choice == "3":
            link_account()
        elif choice == "4":
            break
        else:
            print("Invalid")


if __name__ == "__main__":
    menu()
