import socket
import time
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
        key = commands[1]
        value = commands[2]
        store[key] = value
        return f"stored {key} with value {value}"

    elif cmd == "get":
        if len(commands) < 2:
            return "not enough arguments"
        key = commands[1]
        value = store.get(key)
        if value is not None:
            return value
        else:
            return f"not found {key}"

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
    server.setblocking(False)

    server.bind((host, port))
    print(f"[*] Listening on {host}:{port}")

    server.listen()


    clients = {}
    buffers = {}

    kq = select.kqueue()
    event = select.kevent(server.fileno(),filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
    kq.control([event],0,None)
    try:
        while True:
            events = kq.control(None,10,1)
            for event in events:
                ""
                fd = event.ident
                if fd == server.fileno():
                    conn, addr = server.accept()
                    connection_fd = conn.fileno()
                    print(f"accepting connection from {addr}")
                    connection_event = select.kevent(connection_fd,filter=select.KQ_FILTER_READ,flags=select.KQ_EV_ADD)
                    kq.control([connection_event],0,None)
                    clients[connection_fd] = conn
                    buffers[connection_fd] = ""
                elif event.filter == select.KQ_FILTER_READ:
                    
                    connection_fd = event.ident
                    connection_socket = clients[connection_fd]
                    data = connection_socket.recv(1024)
                    if not data:
                        delete_event = select.kevent(connection_fd,filter=select.KQ_FILTER_READ,flags=select.KQ_EV_DELETE)
                        kq.control([delete_event],0,None)
                    else:
                        buffers[connection_fd] += data.decode()

                        while "\n" in buffers[connection_fd]:
                            line, buffers[connection_fd] = buffers[connection_fd].split("\n",1)
                            line = line.strip()
                            if not line:
                                continue

                            print(f"[{clients[connection_fd]}] Received: {line}")
                            response = process_command(line)
                            response_msg = f"{response}\n"
                            connection_socket.sendall(response_msg.encode())
                            print(f"response sent to connection {clients[connection_fd]}")



    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        for conn in clients.keys():
            conn.close()
        server.close()

if __name__ == "__main__":
    main()
