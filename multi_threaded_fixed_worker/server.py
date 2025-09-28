import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

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
    try:
        while True:
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

    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Connection {addr} closed")

def main():
    host = '0.0.0.0'
    port = 3003
    max_workers = 3  # Adjust based on your needs


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port} with {max_workers} worker threads")

    # Create thread pool
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ClientHandler")
    
    def signal_handler(signum, frame):
        print("\n[!] Shutting down server...")
        server.close()
        executor.shutdown(wait=True, cancel_futures=True)
        print("[!] Server shut down complete")
        sys.exit(0)

    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    try:
        while True:
            try:
                conn, addr = server.accept()
                conn.send("connection received!!!\n".encode())
                
                # Submit client handling to thread pool
                future = executor.submit(handle_client, conn, addr)
                
                # Optional: You can add a callback to handle any exceptions
                def handle_future_exception(fut):
                    try:
                        fut.result()  # This will raise any exception that occurred
                    except Exception as e:
                        print(f"[!] Exception in client handler: {e}")
                
                future.add_done_callback(handle_future_exception)
                
            except OSError:
                # Socket was closed, likely due to shutdown
                break
                
    except KeyboardInterrupt:
        print("\n[!] Server shutting down")
    finally:
        server.close()
        executor.shutdown(wait=True)
        print("[!] All threads finished")

if __name__ == "__main__":
    main()