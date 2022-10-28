import socket
import threading
import os

from session import Session

HOST, PORT = "localhost", 8989
FORMAT = "UTF-8"

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    socket.bind((HOST, PORT))
except OSError:
    print("Error: Server already ON.")
    socket.close()
    quit()

socket.listen()

os.system("cls")
print("> Server ON <")

session = Session()

global sessions
server_on = True
stop_thread = False
sessions = [[["main_session", "any"]]]
instructions = """
0: Shutdown server
1: Number of sessions
2: Number of clients
3 <username>: remove a client
4: List of connected clients
5: List of sessions ON
"""

def handling(user_name, s_client, h_client, stop_thread):

    can_run = True
    running = True

    id_session = ""
    password_session = ""
    user_in_session = True

    print(f"{user_name} has joined the main session!")

    option = ""
    try:
        option = s_client.recv(24).decode(FORMAT)
    except ConnectionAbortedError:
        running = False
        can_run = False
        user_in_session = False
 

    if option == "" or option == "disconnected":
        print(f"{user_name} has left in options menu...")
        can_run = False
        running = False
        user_in_session = False

    if option == '1':

        while running:

            try:
                id_session = s_client.recv(24).decode(FORMAT)
                password_session = s_client.recv(24).decode(FORMAT)
            except ConnectionAbortedError:
                print(f"{user_name} disconnected on creating a session...")
                can_run = False
                user_in_session = False
                break
            except ConnectionResetError:
                print(f"{user_name} disconnected on joining a session...")
                can_run = False
                user_in_session = False
                break

            if id_session == "" or password_session == "":
                can_run = False
                break


            if not session.id_is_already(id_session):
                s_client.send(id_session.encode(FORMAT))
                session.set_id_and_password(id_session, password_session)
                for i in sessions[0]:
                    if i[1] == s_client:
                        sessions[0].remove(i)
                sessions.append([[id_session, password_session], [user_name, s_client, h_client, stop_thread]])
                running = False
            else:
                s_client.send("already id".encode(FORMAT))

    elif option == '2':
        running = True
        while running:

            try:
                id_session = s_client.recv(24).decode(FORMAT)
                password_session = s_client.recv(24).decode(FORMAT)
            except ConnectionAbortedError:
                print(f"{user_name} disconnected on joining a session...")
                can_run = False
                user_in_session = False
                break
            except ConnectionResetError:
                print(f"{user_name} disconnected on joining a session...")
                can_run = False
                user_in_session = False
                break

            if session.id_is_already(id_session):
                index = 0
                for i in sessions:
                    if i[0][0] == id_session:
                        if i[0][1] == password_session:
                            s_client.send(id_session.encode(FORMAT))
                            for i in sessions[0]:
                                if i[1] == s_client:
                                    sessions[0].remove(i)
                            sessions[index].append([user_name, s_client, h_client, stop_thread])
                            running = False
                            break
                        else:
                            s_client.send("Invalid password...".encode(FORMAT))
                    index+=1
            else:
                s_client.send("id doesn't exist...".encode(FORMAT))

    if can_run:
        running = True
        while running:

            try:
                c_data = s_client.recv(500).decode(FORMAT)
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
                break

            print(f"{user_name}: {c_data}")

            for i in sessions:
                for j in i[1:]:

                    if i[0][0] == id_session:
                        if j[1] == s_client:
                            if j[-1] == True:
                                running = False
                        else:
                            j[1].send(f"{user_name}: {c_data}".encode(FORMAT))

    for i in sessions:
        for j in i[1:]:

            if j[1] != s_client:
                if i[0][0] == id_session:
                    if user_in_session:
                        try:
                            j[1].send(f"Server: {user_name} has left the \"{id_session}\" session...".encode(FORMAT))
                        except OSError:
                            pass

    s_client.close()

    index = 0
    for i in sessions:
        for j in i[1:]:
            if j[1] == s_client:
                j[1].close()
                sessions[index].remove(j)
        index+=1

    for i in sessions:
        if len(i) == 1 and i != [["main_session", "any"]]:
            session.del_id_and_password(i[0])
            sessions.remove(i)

def admin():
    global sessions
    running = True
    while running:

        try:
            user_input = input("")
        except EOFError:
            running = False
            break

        os.system("cls")
        print(instructions)

        if user_input == '0':
            user_input = input("> Are you sure? (Y/n): ").lower()
            if user_input == '' or user_input == 'y' or user_input == 'yes': 
                for i in sessions:
                    for j in i[1:]:
                        j[-1] = True
                    running = False
            else:
                print("> Shutdown is canceled <")

        elif user_input == '1':
            print(f"> {len(sessions)-1} session(s) <")
        
        elif user_input == '2':
            index = 0
            for i in sessions:
                for j in i[1:]:
                    index += 1
            print(f"{index} connected clients")

        elif user_input == f"3 {user_input[2:]}":
            for i in sessions:
                for j in i[1:]:
                    if j[0] == user_input[2:]:
                        j[1].send("Server: Disconnected by admin!".encode(FORMAT))
                        j[1].close()
                        print(f"> {j[0]} is banned! <")

        elif user_input == '4':
            for i in sessions:
                for j in i[1:]:
                    print(j[0])
        
        elif user_input == '5':
            for i in sessions[1:]:
                print(i[0][0])


    socket.close()


threading.Thread(target=admin).start()

print(instructions)

while server_on:

    try:
        s_client, h_client = socket.accept()

    except OSError:
        for i in sessions:
            for j in i[1:]:
                j[1].close()
        print("> Server shutdown... <")
        break

    except KeyboardInterrupt:
        for i in sessions:
            for j in i[1:]:
                j[1].close()
        print("> Server shutdown... <")
        break

    user_name = s_client.recv(24).decode(FORMAT)
    sessions[0].append([user_name, s_client, h_client, stop_thread])
    threading.Thread(target=handling, args=(user_name, s_client, h_client, stop_thread)).start()

print("> Server is OFF <")