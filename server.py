import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously
import threading

currentUsers = {}
registered_clients = {}

def handleChildClientConnection(client, client_address):
    while True:
        try:
            message = client.recv(1024).decode()
            # message can be JOIN, LIST, etc...

            #message_array = message.split(" ")
            request = message.split(" ")[0]
            
            # checking if the request has an input string (everything after request)
            # makes it easier for parsing chat messages faster
            message_array = message.split(" ", 1) # breaking up the request type and contents
            if len(message_array) > 1:
                message_array = message_array[1]
            
            if request == "JOIN":
                if len(currentUsers) >= 10:
                    sys.stdout.flush()  # Flush the output buffer
                    print("Too many users.")
                else:
                    currentUsers[client_address] = message_array.split(" ")[0]
                    sys.stdout.flush()  # Flush the output buffer
                    print(f"{message_array.split(' ')[0]} has joined!")
                    registered_clients[client_address] = client
                    server_msg = "You have joined."
                    client.send(server_msg.encode())
            elif request == "LIST":
                sys.stdout.flush()  # Flush the output buffer
                list_of_users = ''
                #list_of_users = ', '.join(list(currentUsers.keys()))
                print(f"Current Users: ")
                for key in currentUsers:
                    print(currentUsers[key])
                    list_of_users += currentUsers[key] + ", "
                list_of_users = list_of_users[:-2]
                client.send(list_of_users.encode())
            elif request == "BCST":
                sys.stdout.flush()  # Flush the output buffer
                # Making sure the user sends an actual message
                if len(message_array) == 1:
                    server_msg = "Usage: BCST <your message>"
                    client.send(server_msg.encode())
                else:
                    server_msg = "You're sending a broadcast."
                    client.send(server_msg.encode())
                    for ip in registered_clients.values():
                        chat_msg = f"{currentUsers[client_address]}: {message_array}"
                        ip.send(chat_msg.encode())
            elif request == "MESG":
                sys.stdout.flush()  # Flush the output buffer
                private_msg_contents = message_array.split(" ", 1)
                if len(message_array) < 2:
                    server_msg = "Usage: MESG <user> <your message>"
                    client.send(server_msg.encode())
                #targeted_user = message_array.split(" ")[0];
                # Checking if the specified username is in the list of registered clients
                elif private_msg_contents[0] in registered_clients.values():
                    chat_msg = f"[PM] {currentUsers[client_address]}: {private_msg_contents[1]}"
                    pm_target = registered_clients.values()[private_msg_contents[0]]
                    pm_target.send(chat_msg.encode())
                else: 
                    server_msg = "Error: Invalid username!"
                    client.send(server_msg.encode())
            elif request == "QUIT":
                # remove the user from currentUsers
                sys.stdout.flush()  # Flush the output buffer
                if currentUsers[client_address]:
                    print(f"\n{currentUsers[client_address]} left the chat.")
                sys.stdout.flush()  # Flush the output buffer
                del registered_clients[client_address]
                del currentUsers[client_address]
                client.close()
                break
            else:
                print(f"message not understood")
            sys.stdout.flush()  # Flush the output buffer
        except Exception as e:
            sys.stdout.flush()  # Flush the output buffer
            if currentUsers[client_address]:
                print(f"\n{currentUsers[client_address]} left the chat.")
            sys.stdout.flush()  # Flush the output buffer
            del registered_clients[client_address]
            del currentUsers[client_address]
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

    svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svr_sock.bind(("", svr_port))  # bind socket to the server port

    svr_sock.listen(1)

    sys.stdout.flush()  # Flush the output buffer (wouldn't show print statements unless I added this)
    print(
        "The Chat Server Started"
    )  # print statement to verify that the server is listening
    sys.stdout.flush()  # Flush the output buffer
    while True:
        try:
            connectionSocket, addr = svr_sock.accept()
            sys.stdout.flush()  # Flush the output buffer
            print(f"Connected with {addr}")
            sys.stdout.flush()  # Flush the output buffer
            # Spawn a new thread to handle the client
            client_handler = threading.Thread(
                target=handleChildClientConnection, args=(connectionSocket, addr)
            )
            client_handler.start()
            # handleChildClientConnection(connectionSocket)
        except KeyboardInterrupt:
            # if the user enters Ctrl+c, close the socket and terminate the program
            print("\nServer terminated.")
            sys.stdout.flush()  # Flush the output buffer
            svr_sock.close()  # close the socket
            sys.exit(0)  # exit the program


# trick to check if current python module is being run as the main program or imported as a module
if __name__ == "__main__":
    main()
