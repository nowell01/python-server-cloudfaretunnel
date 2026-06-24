import socket
import os
import mimetypes
import threading

ROOT = 'dahab'
HOST = '127.0.0.1'
PORT = 2000
MAX_CONNECTIONS = 100  # cap concurrent client threads

# Limits how many handle_client threads can run at once.
connection_slots = threading.BoundedSemaphore(MAX_CONNECTIONS)


def handle_client(client_socket):
    try:
        client_socket.settimeout(10)  # don't let a slow client tie up a thread forever
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            return
        content = load_page_from_get_request(data)
        client_socket.sendall(content)
        client_socket.shutdown(socket.SHUT_WR)
    except (ConnectionError, UnicodeDecodeError, IndexError, socket.timeout, OSError):
        pass
    finally:
        client_socket.close()
        connection_slots.release()


def start_my_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(16)
        print(f'Serving on http://{HOST}:{PORT}/ (Ctrl+C to stop)')
        while True:
            client_socket, address = server.accept()
            # Block here if we're already at MAX_CONNECTIONS; reserve a slot
            # before spawning so we never exceed the cap.
            connection_slots.acquire()
            try:
                thread = threading.Thread(
                    target=handle_client, args=(client_socket,), daemon=True
                )
                thread.start()
            except RuntimeError:
                # Couldn't start the thread (e.g. OS thread limit) — free the
                # slot and drop the connection instead of leaking it.
                connection_slots.release()
                client_socket.close()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
    print('shutting down...')


def load_page_from_get_request(request_data):
    HDRS_404 = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'

    parts = request_data.split(' ')
    if len(parts) < 2:
        return (HDRS_404 + 'Bad request').encode('utf-8')

    path = parts[1].split('?')[0]
    if path == '/':
        path = '/index.html'

    # Resolve the requested file and make sure it stays inside ROOT
    # (prevents path-traversal like /../secret.txt).
    root_abs = os.path.realpath(ROOT)
    target = os.path.realpath(os.path.join(root_abs, path.lstrip('/')))
    if os.path.commonpath([root_abs, target]) != root_abs:
        return (HDRS_404 + 'Forbidden').encode('utf-8')

    try:
        with open(target, 'rb') as file:
            response = file.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        return (HDRS_404 + 'Sorry, not found').encode('utf-8')

    content_type = mimetypes.guess_type(target)[0] or 'application/octet-stream'
    hdrs = (
        'HTTP/1.1 200 OK\r\n'
        f'Content-Type: {content_type}\r\n'
        f'Content-Length: {len(response)}\r\n'
        '\r\n'
    )
    return hdrs.encode('utf-8') + response


if __name__ == '__main__':
    start_my_server()
