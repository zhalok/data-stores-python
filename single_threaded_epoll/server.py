import socket
import select

# Global in-memory store
store = {}

def process_command(payload):
    commands = payload.strip().split()
    if not commands:
        return "invalid commands"
    cmd = commands[0].lower()
    if cmd == "set":
        if len(commands) < 3:
            return "not enough arguments"
        key, value = commands[1], commands[2]
        store[key] = value
        return f"stored {key} with value {value}"
    elif cmd == "get":
        if len(commands) < 2:
            return "not enough arguments"
        key = commands[1]
        value = store.get(key)
        return value if value is not None else f"not found {key}"
    elif cmd == "delete":
        if len(commands) < 2:
            return "not enough arguments"
        key = commands[1]
        if key in store:
            del store[key]
            return f"deleted {key}"
        else:
            return f"not found {key}"
    else:
        return "unknown command"

def main():
    host = '0.0.0.0'
    port = 3000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1000)
    print(f"[*] Listening on {host}:{port}")

    clients = {}
    buffers = {}
    addresses = {}

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    try:
        while True:
            events = epoll.poll(1)
            for fd, event in events:
                if fd == server.fileno():
                    conn, addr = server.accept()
                    epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLRDHUP | select.EPOLLHUP)
                    clients[conn.fileno()] = conn
                    buffers[conn.fileno()] = ""
                    addresses[conn.fileno()] = addr
                    print(f"Accepted connection from {addr}")
                elif event == select.EPOLLRDHUP or event == select.EPOLLHUP:
                    epoll.unregister(fd)
                    addr = addresses[fd]
                    del clients[fd]
                    del buffers[fd]
                    print(f"closing connection from address {addr}")
                elif event == select.EPOLLIN:
                    conn = clients[fd]
                    data = conn.recv(1024)
                    buffers[fd] += data.decode()
                    while "\n" in buffers[fd]:
                        line, buffers[fd] = buffers[fd].split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        print(f"[{conn}] Received: {line}")
                        response = process_command(line)
                        try:
                            conn.sendall((response + "\n").encode())
                            print(f"Response sent to {conn}")
                        except:
                            print("error sending response")
                    # try:
                    #     data = conn.recv(1024)
                    # except ConnectionResetError:
                    #     data = None
                    # if not data:
                    #     epoll.unregister(fd)
                    #     conn.close()
                    #     del clients[fd]
                    #     del buffers[fd]
                    # else:
                    #     if fd not in buffers:
                    #         buffers[fd] = ""
                    #     buffers[fd] += data.decode()
                    #     while "\n" in buffers[fd]:
                    #         line, buffers[fd] = buffers[fd].split("\n", 1)
                    #         line = line.strip()
                    #         if not line:
                    #             continue
                    #         print(f"[{conn}] Received: {line}")
                    #         response = process_command(line)
                    #         try:
                    #             conn.sendall((response + "\n").encode())
                    #             print(f"Response sent to {conn}")
                    #         except:
                    #             print("error sending response")

    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        for conn in clients.values():
            conn.close()
        server.close()

if __name__ == "__main__":
    main()
