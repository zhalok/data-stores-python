import socket
import time

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

    try:
        while True:
            # Accept new connections (non-blocking)
            try:
                conn, addr = server.accept()
                conn.send("connection recieved!!!\n".encode())
                conn.setblocking(False)
                clients[conn] = addr
                buffers[conn] = ""
                print(f"[+] New connection from {addr}")
            except BlockingIOError:
                pass

            to_remove = []

            # Iterate through all clients
            for conn in list(clients.keys()):
                try:
                    data = conn.recv(1024)
                    if not data:
                        # Connection closed
                        to_remove.append(conn)
                        continue

                    buffers[conn] += data.decode()

                    # Process complete lines
                    while "\n" in buffers[conn]:
                        line, buffers[conn] = buffers[conn].split("\n",1)
                        line = line.strip()
                        if not line:
                            continue

                        print(f"[{clients[conn]}] Received: {line}")
                        response = process_command(line)
                        response_msg = f"{response}\n"
                        try:
                            conn.sendall(response_msg.encode())
                            print(f"response sent to connection {clients[conn]}")
                        except:
                            print("faced error on response writing in the connection")

                    

                except BlockingIOError:
                    # No data to read right now
                    pass
                except Exception as e:
                    print(f"[!] Error with {clients[conn]}: {e}")
                    to_remove.append(conn)

            # Clean up closed connections
            for conn in to_remove:
                print(f"[-] Connection {clients[conn]} closed")
                conn.close()
                del clients[conn]
                del buffers[conn]

            time.sleep(0.001)  # Small sleep to prevent busy loop

    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        for conn in clients.keys():
            conn.close()
        server.close()

if __name__ == "__main__":
    main()
