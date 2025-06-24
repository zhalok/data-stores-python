import socket
import time
import os
import multiprocessing

store = {}

def process_command(payload):
    print(f"payload: {payload}")
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
        return value if value else f"not found {key}"

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

def server_worker(port):
    host = '0.0.0.0'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Required to allow multiple processes to bind to the same port
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # Only on Linux/macOS
    server.bind((host, port))
    server.listen()
    server.setblocking(False)

    print(f"[PID {os.getpid()}] Listening on {host}:{port}")

    clients = {}
    buffers = {}

    try:
        while True:
            try:
                conn, addr = server.accept()
                conn.setblocking(False)
                clients[conn] = addr
                buffers[conn] = ""
                print(f"[PID {os.getpid()}] New connection from {addr}")
            except BlockingIOError:
                pass

            to_remove = []

            for conn in list(clients.keys()):
                try:
                    data = conn.recv(1024)
                    if not data:
                        to_remove.append(conn)
                        continue

                    buffers[conn] += data.decode()

                    while "\n" in buffers[conn]:
                        line, buffers[conn] = buffers[conn].split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue

                        print(f"[PID {os.getpid()}] [{clients[conn]}] Received: {line}")
                        response = process_command(line)
                        conn.sendall(f"{response}\n".encode())

                except BlockingIOError:
                    pass
                except Exception as e:
                    print(f"[!] Error with {clients[conn]}: {e}")
                    to_remove.append(conn)

            for conn in to_remove:
                print(f"[-] Connection {clients[conn]} closed")
                conn.close()
                del clients[conn]
                del buffers[conn]

            time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\n[PID {os.getpid()}] Server shutting down")
    finally:
        for conn in clients:
            conn.close()
        server.close()

def main():
    port = 3002
    num_workers = multiprocessing.cpu_count()
    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=server_worker, args=(port,))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Main process shutting down...")
        for p in processes:
            p.terminate()
            p.join()

if __name__ == "__main__":
    main()
