import socket
import threading
import signal

signal.signal(signal.SIGINT, signal.SIG_IGN)

HOST, PORT = "localhost", 8989
FORMAT = "UTF-8"

running = True
can_run = True

try:
    user_name = input("> Your name: ")
except EOFError:
    quit()

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Error: Server is offline...")
    socket.close()
    quit()


socket.send(user_name.encode(FORMAT))

print("1: Create a session")
print("2: Join a session")

quest = None
while True:

    try:
        quest = input("> ")
        if quest == '1' or quest == '2':
            break
    except EOFError:
        socket.send("disconnected".encode(FORMAT))
        can_run = False
        running = False
        break


if quest == '1':
    try:
        socket.send(quest.encode(FORMAT))
    except ConnectionResetError:
        print("Error: Server has rebooted...")
        running = False
elif quest == '2':
    try:
        socket.send(quest.encode(FORMAT))
    except ConnectionResetError:
        print("Error: Server has rebooted...")
        running = False


while running:

    if quest == '1':

        try:
            id_session = input("> Create an id: ")
            password_session = input("> create a password: ")
        except EOFError:
            break
        except ConnectionResetError:
            print("Error: Server has reboot...")
            socket.close(); quit()

        try:
            socket.send(id_session.encode(FORMAT))
            socket.send(password_session.encode(FORMAT))
        except ConnectionResetError:
            print("Error: Server has reboot...")
            socket.close(); quit()

        response = socket.recv(500).decode(FORMAT)

        if response == id_session:
            break
        else:
            print(f"Server: {response}")

    elif quest == '2':

        try:
            id_session = input("> id: ")
            password_session = input("> password: ")
        except EOFError:
            break
        except ConnectionResetError:
            print("Error: Server has reboot...")
            socket.close(); quit()

        try:
            socket.send(id_session.encode(FORMAT))
            socket.send(password_session.encode(FORMAT))
        except ConnectionResetError:
            print("Error: Server has reboot...")
            socket.close(); quit()

        response = socket.recv(500).decode(FORMAT)

        if response == id_session:
            break
        else:
            print(f"Server: {response}")


def sending():
    while True:

        try:
            message_input = input("").encode(FORMAT)
        except EOFError:
            break

        try:
            socket.send(message_input)
        except OSError:
            print("Error: SERVER OFF or rebooted, message not sent...")
            break

    socket.close()


def recving():
    s_data = ""
    while True:

        try:
            s_data = socket.recv(500).decode(FORMAT)
        except ConnectionAbortedError:
            break
        except ConnectionResetError:
            print("Error: SERVER OFF or rebooted, battery is low...")
            break

        if s_data == "quit":
            print("Error: SERVER OFF, is shutdown")
            break

        print(s_data)

    socket.close()

if can_run != False:
    threading.Thread(target=sending).start()
    threading.Thread(target=recving).start()