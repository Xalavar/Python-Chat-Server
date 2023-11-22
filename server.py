import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously
import threading

currentUsers = []


def handleChildClientConnection(client):
    while True:
        try:
            message = client.recv(1024).decode()
            # message can be JOIN, LIST, etc...

            # pretend message was a JOIN request
            # add them to users
            message_array = message.split(" ")
            request = message_array[0]
            if request == "JOIN":
                currentUsers.append(message_array[1])
                print(f"{message_array[1]} has joined!")
            if request == "LIST":
                for user in currentUsers:
                    print(user)
            if request == "QUIT":
                # remove the user from currentUsers
                currentUsers.remove(message_array[1])
                message = message_array[1] + " left" 

	    # still need to figure out how to show someone left on other connected client's ui

            sys.stdout.flush()  # Flush the output buffer
            sys.stdout.flush()  # Flush the output buffer
            client.send(message.encode())
        except:
            sys.stdout.flush()  # Flush the output buffer
            print("\nClient terminated.")
            sys.stdout.flush()  # Flush the output buffer
            client.close()
            break


def main():
    signal.signal(
        signal.SIGINT, signal.SIG_DFL
    )  # allowing SIGNIN which terminates on Ctrl+C, SIG_DFL performs the default function for the signal

    # Verify that there are 2 command line arguments (file, port)
    if len(sys.argv) != 2:
        print("Usage: python3 pingsvr.py <port>")
        sys.exit(1)  # terminate program

    # Set up the server socket
    svr_port = int(
        sys.argv[1]
    )  # use the port number from the command line arguments, cast as integer

    svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svr_sock.bind(("ecs-codingx.csus.edu", svr_port))  # bind socket to the server port

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
                target=handleChildClientConnection, args=(connectionSocket,)
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
