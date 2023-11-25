# client.py

# ID: 301762851
# Name: Alex Fedorov
# Section: 6
# Course Code: 86863
# Date: 11/26/2023

# Description:
# This program acts as a chat client
# The client attempts to connect to a server at a specified host and port
# The client issues requests to the server and may ask the server to handle requests
# The client can choose to disconnect from the server


import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously
import threading  # importing threading to handle recieving server nessages


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()  # recieve server message
            if not data:  # if message is blank, ignore
                break
            sys.stdout.flush()  # Flush the output buffer
            print(f"{data}")  # print server response
            sys.stdout.flush()  # Flush the output buffer
        except socket.error as e:
            break


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Verify that there are 3 command line arguments (file, hostname, port)
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)  # terminate program

    # Grab details from the command line arguments
    svr_host = sys.argv[1]  # use host name from command line arguments index 1
    svr_port = int(
        sys.argv[2]
    )  # use server port number from command line arguments index 2, cast as integer

    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket
    try:
        cli_sock.connect((svr_host, svr_port))  # connect to server

        # spawn thread to handle server messages
        receive_thread = threading.Thread(target=receive_messages, args=(cli_sock,))
        receive_thread.start()

        already_registered = False  # to check if client is registered in the chat room
        username = ""  # to store username value

        while True:
            try:
                if not already_registered:
                    # show this message to motivate the client to join the chat room if they are not yet registered
                    message = str(
                        input(
                            "You are not a registered user. Enter JOIN followed by your username: "
                        )
                    )
                else:
                    # else, we can just print a blank space and wait for client input, because they are registered
                    message = input()

                # strip message from whitespace
                message = message.strip()
                message_array = message.split(" ")  # split the message into its parts

                cli_sock.sendall(message.encode())  # send the message to the server

                request = message_array[
                    0
                ]  # the first element of message array will be the request

                # this if statement checks if it is the client's first time joining
                if (
                    request == "JOIN"
                    and not already_registered
                    and len(message_array) > 1
                ):
                    # set registered to true, save username
                    already_registered = True
                    username = message.split(" ", 1)[1]

                # if the client wants to quit
                if request == "QUIT":
                    # check if username was created (if the client joined)
                    if username:
                        print(f"{username} is quitting the chat server")
                    # exit program
                    sys.exit(0)

            except KeyboardInterrupt:
                sys.stdout.flush()  # Flush the output buffer
                print("\Client terminated by user (Ctrl-C).")
                cli_sock.close()
                sys.exit(0)
    except socket.error as e:
        # on socket error, close the connection
        sys.stdout.flush()  # Flush the output buffer
        print(f"Error connecting to server: {e}")
        cli_sock.close()
        sys.exit(0)


# trick to check if current python module is being run as the main program or imported as a module
if __name__ == "__main__":
    main()
