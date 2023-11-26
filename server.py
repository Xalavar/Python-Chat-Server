# server.py

# CSC138 Section 6
# Course Code: 86863
# Date: 11/26/2023

# Group Members:
"""Alex Fedorov
Jeffrey Melendez
Nicholas Minor
Danny Phan
Angelo Ventura"""


# Description:
# This program acts as a chat server
# The code sets up a TCP socket and accepts client connections
# For each client that connects, a thread is spawned to handle that client
# The server responds to specific client messages


import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously
import threading  # importing threading to handle child client processes

currentUsers = {}  # object to save usernames (for printing names)
registered_clients = {}  # object to save sockets (for sending messages to client)


# custom function to send a message to all registered clients other than the client address specified in the parameters
def sendToAll(cli_address, message):
    # for each registered client, send a message if they are not the cli_address
    for addr, socket in registered_clients.items():
        if addr != cli_address:
            try:
                socket.sendall(message.encode())
            except socket.error:
                print("socket error")
                pass


# client thread that is spawned for each client that connects to the server
def handleChildClientConnection(client, client_address):
    while True:
        try:
            message = client.recv(1024).decode()  # recieve message from client

            request = message.split(" ")[0]  # extract the request type

            # checking if the request has an input string (everything after request)
            # makes it easier for parsing chat messages faster
            message_array = message.split(
                " ", 1
            )  # breaking up the request type and contents

            # this if statement makes sure that they do not have access to other requests if they are not registered
            if (
                request in ["LIST", "MESG", "BCST"]
                and client_address not in registered_clients
            ):
                continue  # do not let them do the request
            else:
                # if the message has more contents than just 2, then make the message array the rest of the message
                if len(message_array) > 1:
                    message_array = message_array[1]

                # if the request is JOIN
                if request == "JOIN":
                    # if they did not write anything after JOIN
                    if len(message.split(" ")) <= 1:
                        client.send("Please specify a username.".encode())
                    # if there are already 10 (max) users, do not add them, send a custom message
                    elif len(currentUsers) >= 10:
                        sys.stdout.flush()  # Flush the output buffer
                        print("Too many users. Client cannot join.")
                        client.send("Too Many Users".encode())
                    # if they are already registered, do not register them again
                    elif client_address in registered_clients:
                        print("Client already joined.")
                        client.send("You have already joined.".encode())
                    else:
                        # they are new, save their username
                        new_user = message_array.split(" ")[0]
                        # add an entry into the current users object
                        currentUsers[client_address] = new_user
                        sys.stdout.flush()  # Flush the output buffer
                        print(f"{new_user} has joined the ChatRoom!")
                        # add an entry into the registered users object
                        registered_clients[client_address] = client
                        server_msg = "You have joined! Connected to server!"
                        # send the client a message
                        client.send(server_msg.encode())
                        # send all registered users a message that a new user has joined
                        sendToAll(client_address, f"{new_user} joined!")
                elif request == "LIST":
                    sys.stdout.flush()  # Flush the output buffer
                    list_of_users = (
                        ""  # create empty string and populate it later with the users
                    )
                    print(f"Current Users: ")
                    for key in currentUsers:
                        # for each user in current users, add them to list of users string
                        print(currentUsers[key])
                        list_of_users += currentUsers[key] + ", "
                    list_of_users = list_of_users[
                        :-2
                    ]  # remove the trailing space and comma
                    # send the client the list of users
                    client.send(list_of_users.encode())
                elif request == "BCST":
                    sys.stdout.flush()  # Flush the output buffer
                    # Making sure the user sends an actual message
                    if len(message_array) == 1:
                        server_msg = "Usage: BCST <your message>"
                        client.send(server_msg.encode())
                    else:
                        server_msg = f"You ({currentUsers[client_address]}) are sending a broadcast."
                        sys.stdout.flush()  # Flush the output buffer
                        # print to server screen that someone is broadcasting a message
                        print(
                            f"{currentUsers[client_address]} is sending a BCST: {message_array}"
                        )
                        # send to client that they are sending a broadcast
                        client.send(server_msg.encode())
                        client.send(
                            f"{currentUsers[client_address]}: BCST {message_array}".encode()
                        )
                        # send to client their broadcasted message
                        chat_msg = (
                            f"{currentUsers[client_address]}: BCST {message_array}"
                        )
                        # send to all registered clients the broadcast
                        sendToAll(client_address, chat_msg)
                elif request == "MESG":
                    sys.stdout.flush()  # Flush the output buffer
                    # check if message request is correct
                    if len(message_array) < 2:
                        server_msg = "Usage: MESG <user> <your message>"
                        client.send(server_msg.encode())
                    else:
                        private_msg_contents = message_array.split(" ", 1)
                        # Checking if the specified username is in the list of registered clients
                        found = False
                        for address, name in currentUsers.items():
                            if private_msg_contents[0] == name:
                                # set found to true, we found a name match
                                found = True
                                chat_msg = f"[PM] {name}: {private_msg_contents[1]}"
                                registered_clients[address].send(
                                    chat_msg.encode()
                                )  # send message to that client
                                print(
                                    f"{currentUsers[client_address]} is sending a MESG to {name}: {private_msg_contents[1]}"
                                )  # print on the server screen the message recipient and contents
                        if not found:
                            # if the recipient was not found, tell the client that they are unknown
                            client.send("Unknown Recipient.".encode())
                elif request == "QUIT":
                    sys.stdout.flush()  # Flush the output buffer
                    # if client is registered, print their name
                    # else, just print their address
                    if client_address in currentUsers:
                        print(f"{currentUsers[client_address]} left the chat.")
                    else:
                        print(f"{client_address} disconnected.")
                    # send a message to the client that they are leaving the chat
                    client.send("You are leaving the chat".encode())
                    # send a message to all registered clients that a user has left
                    server_msg = f"{currentUsers[client_address]} left."
                    sendToAll(client_address, server_msg)
                    sys.stdout.flush()  # Flush the output buffer
                    # remove the user from currentUsers and registered users
                    del registered_clients[client_address]
                    del currentUsers[client_address]
                    # close the client connection
                    client.close()
                    break
                else:
                    print(f"Message not understood")
                    # message was not understood, send a message to the client
                    client.send("Unknown Message.".encode())
            sys.stdout.flush()  # Flush the output buffer
        except Exception as e:
            sys.stdout.flush()  # Flush the output buffer
            # if the user was registered, print their name and that they disconnected
            if client_address in currentUsers:
                print(f"{currentUsers[client_address]} disconnected.")
            sys.stdout.flush()  # Flush the output buffer
            # if the user was registered, delete them from both user objects
            if client_address in registered_clients:
                del registered_clients[client_address]
            if client_address in currentUsers:
                del currentUsers[client_address]
            # close client connection
            client.close()
            break


def main():
    signal.signal(
        signal.SIGINT, signal.SIG_DFL
    )  # allowing SIGNIN which terminates on Ctrl+C, SIG_DFL performs the default function for the signal

    # Verify that there are 2 command line arguments (file, port)
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <port>")
        sys.exit(1)  # terminate program

    # Set up the server socket
    svr_port = int(
        sys.argv[1]
    )  # use the port number from the command line arguments, cast as integer

    svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket
    svr_sock.bind(("", svr_port))  # bind socket to the server port

    svr_sock.listen(1)  # listen to connection requests

    sys.stdout.flush()  # Flush the output buffer (wouldn't show print statements unless I added this)
    print(
        "The Chat Server Started"
    )  # print statement to verify that the server is listening
    sys.stdout.flush()  # Flush the output buffer
    while True:
        try:
            (
                connectionSocket,
                addr,
            ) = svr_sock.accept()  # acccept connections to the socket
            sys.stdout.flush()  # Flush the output buffer
            print(
                f"Connected with {addr}"
            )  # once a client connects, show connection message
            # Spawn a new thread to handle the client
            client_handler = threading.Thread(
                target=handleChildClientConnection, args=(connectionSocket, addr)
            )
            # start the thread
            client_handler.start()
        except KeyboardInterrupt:
            # if the user enters Ctrl+c, close the socket and terminate the program
            print("\nServer terminated.")
            sys.stdout.flush()  # Flush the output buffer
            svr_sock.close()  # close the socket
            sys.exit(0)  # exit the program


# trick to check if current python module is being run as the main program or imported as a module
if __name__ == "__main__":
    main()
