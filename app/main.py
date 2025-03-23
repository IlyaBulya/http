import socket
import threading
import os
import sys


def handle_client(client_socket, directory):
    """Handle a client connection in a separate thread."""
    try:
        request = client_socket.recv(4096).decode()
        
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
        
        elif path.startswith("/files/"):
            filename = path[len("/files/"):]
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                # File exists, read its contents
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                
                content_length = len(file_content)
                headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {content_length}\r\n"
                    "\r\n"
                )
                
                # Send headers as text and file content as binary
                client_socket.sendall(headers.encode())
                client_socket.sendall(file_content)
                return  # Early return to avoid sending response again
            else:
                # File doesn't exist
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response.encode())
    finally:
        client_socket.close()


def main():
    # Parse command line arguments
    directory = None
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "--directory" and i + 1 < len(sys.argv):
            directory = sys.argv[i + 1]
            break
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client, _ = server_socket.accept()
        
        # Create a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(client, directory))
        client_thread.daemon = True  # Set as daemon so it exits when the main thread exits
        client_thread.start()


if __name__ == "__main__":
    main()
