import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client, _ = server_socket.accept()
        request = client.recv(4096).decode()
        path = request.split(" ")[1]

        if path == "/":
            client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        else:
            client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        client.close()


if __name__ == "__main__":
    main()
