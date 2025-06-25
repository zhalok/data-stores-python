import socket
import threading

# Global in-memory store + lock
store = {}
store_lock = threading.RLock()

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

        with store_lock:
            store[key] = value

        return f"stored {key} with value {value}"

    elif cmd == "get":
        if len(commands) < 2:
            return "not enough arguments"
        key = commands[1]

        with store_lock:
            value = store.get(key)

        if value is not None:
            return value
        else:
            return f"not found {key}"

    elif cmd == "delete":
        if len(commands) < 2:
            return "not enough arguments"
        key = commands[1]

        with store_lock:
            if key in store:
                del store[key]
                return f"deleted {key}"
            else:
                return f"not found {key}"

    else:
        return "unknown command"

def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")
    buffer = ""
    conn.setblocking(False)
    try:
        while True:
        
            try:
                data = conn.recv(1024)
                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    print(f"[{addr}] Received: {line}")
                    response = process_command(line)
                    response_msg = f"{response}\n"
                    conn.sendall(response_msg.encode())

            except BlockingIOError:
                continue

    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Connection {addr} closed")

def main():
    host = '0.0.0.0'
    port = 3001

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        server.close()

if __name__ == "__main__":
    main()
