import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously
import threading


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            sys.stdout.flush()  # Flush the output buffer
            print(f"{data}") # server response
            sys.stdout.flush()  # Flush the output buffer
        except socket.error as e:
            sys.stdout.flush()  # Flush the output buffer
            # print(f"Error receiving data: {e}")
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

    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cli_sock.connect((svr_host, svr_port))

        receive_thread = threading.Thread(target=receive_messages, args=(cli_sock,))
        receive_thread.start()

        # ask user to join server with username & store username data
        join_prompt = str(input("Enter JOIN followed by your username: "))
        username = join_prompt.split(" ", 1)
        cli_sock.send(join_prompt.encode())

        while True:
            try:
                message = input()
                # to get client's request type
                request = message.split(" ")[0]
                
                # checking if the request has an input string (everything after request)
                message_array = message.split(" ", 1)
                if len(message_array) > 1:
                    message_array = message_array[1]

                cli_sock.sendall(message.encode())

                if request == "QUIT":
                    print(f"{username} is quitting the chat server")
                    cli_sock.close()
                    sys.exit(0)

                # still need to figure out how to show someone left on other connected client's ui

            except KeyboardInterrupt:
                sys.stdout.flush()  # Flush the output buffer
                print("\Client terminated by user (Ctrl-C).")
                cli_sock.close()
    except socket.error as e:
        sys.stdout.flush()  # Flush the output buffer
        print(f"Error connecting to server: {e}")
        cli_sock.close()


# trick to check if current python module is being run as the main program or imported as a module
if __name__ == "__main__":
    main()
