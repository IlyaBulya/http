import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client, _ = server_socket.accept()
        request = client.recv(4096).decode()

        # Получаем первую строку запроса и путь
        lines = request.split("\r\n")
        path = lines[0].split(" ")[1]

        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"

        elif path.startswith("/echo/"):
            echo_str = path[len("/echo/"):]
            content_length = len(echo_str.encode())
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{echo_str}"
            )

        elif path == "/user-agent":
            # Ищем строку с User-Agent
            user_agent = ""
            for line in lines:
                if line.lower().startswith("user-agent:"):
                    user_agent = line.split(":", 1)[1].strip()
                    break

            content_length = len(user_agent.encode())
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{user_agent}"
            )

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client.sendall(response.encode())
        client.close()


if __name__ == "__main__":
    main()
