import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client, _ = server_socket.accept()
        request = client.recv(4096).decode()
        path = request.split(" ")[1]

        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            # Получаем текст после "/echo/"
            echo_str = path[len("/echo/"):]
            content_length = len(echo_str.encode())  # учитываем байты, не только символы
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{echo_str}"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client.sendall(response.encode())
        client.close()


if __name__ == "__main__":
    main()
