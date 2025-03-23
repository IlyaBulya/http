import socket
import threading
import os
import sys


def handle_client(client_socket, directory):
    """Handle a client connection in a separate thread."""
    try:
        # Receive the initial request data
        request_data = client_socket.recv(4096)
        request = request_data.decode('utf-8', errors='replace')
        
        # Parse the request
        request_lines = request.split("\r\n")
        request_line = request_lines[0].split(" ")
        method = request_line[0]  # GET, POST, etc.
        path = request_line[1]
        
        # Parse headers
        headers = {}
        header_end_index = 0
        for i, line in enumerate(request_lines[1:], 1):
            if not line:  # Empty line marks the end of headers
                header_end_index = i
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        
        # Handle different endpoints
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
            client_socket.sendall(response.encode())

        elif path.startswith("/echo/"):
            echo_str = path[len("/echo/"):]
            content_length = len(echo_str.encode())
            
            # Check if client supports gzip compression
            accept_encoding = headers.get("accept-encoding", "")
            # Split by comma and strip whitespace from each encoding
            supported_encodings = [encoding.strip() for encoding in accept_encoding.split(",")]
            supports_gzip = "gzip" in supported_encodings
            
            # Build response headers
            response_headers = [
                "HTTP/1.1 200 OK",
                "Content-Type: text/plain",
            ]
            
            # Add Content-Encoding header if client supports gzip
            if supports_gzip:
                response_headers.append("Content-Encoding: gzip")
                
            response_headers.append(f"Content-Length: {content_length}")
            response_headers.append("")  # Empty line before body
            response_headers.append(echo_str)
            
            # Join headers with CRLF
            response = "\r\n".join(response_headers)
            client_socket.sendall(response.encode())

        elif path == "/user-agent":
            user_agent = headers.get("user-agent", "")
            content_length = len(user_agent.encode())
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{user_agent}"
            )
            client_socket.sendall(response.encode())
        
        elif path.startswith("/files/"):
            filename = path[len("/files/"):]
            file_path = os.path.join(directory, filename)
            
            if method == "GET":
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
                else:
                    # File doesn't exist
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    client_socket.sendall(response.encode())
            
            elif method == "POST":
                # Get content length from headers
                content_length = int(headers.get("content-length", 0))
                
                # Calculate how much of the body we've already received
                header_end = request.find("\r\n\r\n") + 4
                body_received = len(request_data) - header_end
                
                # Read the request body
                body = request_data[header_end:]
                
                # If we haven't received the full body yet, read the rest
                while body_received < content_length:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    body += chunk
                    body_received += len(chunk)
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write the body to the file
                with open(file_path, 'wb') as file:
                    file.write(body)
                
                # Send 201 Created response
                response = "HTTP/1.1 201 Created\r\n\r\n"
                client_socket.sendall(response.encode())
            
            else:
                # Method not supported
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
                client_socket.sendall(response.encode())

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
