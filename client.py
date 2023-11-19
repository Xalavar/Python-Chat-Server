import socket  # importing socket library for creating a socket
import sys  # importing sys library for program termination
import signal  # importing signal which allows keyboard interrupt exceptions asynchronously


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  #
    # Verify that there are 3 command line arguments (file, hostname, port)
    if len(sys.argv) != 3:
        print("Usage: python3 pingcli.py <hostname> <port>")
        sys.exit(1)  # terminate program

    # Grab details from the command line arguments
    svr_host = sys.argv[1]  # use host name from command line arguments index 1
    svr_port = int(
        sys.argv[2]
    )  # use server port number from command line arguments index 2, cast as integer

    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_sock.connect((svr_host, svr_port))

    while True:
        try:
            message = input()

            cli_sock.send(message.encode())

            response = cli_sock.recv(1024)

            print("From server: ", response.decode())

        except KeyboardInterrupt:
            print("\Client terminated by user (Ctrl-C).")
            cli_sock.close()


# trick to check if current python module is being run as the main program or imported as a module
if __name__ == "__main__":
    main()
