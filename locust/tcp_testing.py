import random
import socket
import time
from locust import User, task, between
import uuid
import os

SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

def get_command():
    commands = ["set","get","delete"]
    cmd = random.choice(commands)
    key = f"key-{random.randint(1,100000)}"
    if cmd == "set":
        value = f"value-{random.randint(1,100000)}"
        command_str = f"{cmd} {key} {value}\n"
    else:
        command_str = f"{cmd} {key}\n"
    return command_str.encode("utf-8")

class TCPLoadUser(User):
    wait_time = between(1, 2)

    @task
    def send_1000_commands(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))  # Change to your server's address and port
            print(f"Connected to TCP server")

            for i in range(1000):
                command = get_command()
                start_time = time.time()
                try:
                    print("command", command)
                    sock.sendall(command)
                    response = sock.recv(1024)
                    total_time = (time.time() - start_time) * 1000  # milliseconds
                    
                    self.environment.events.request.fire(
                        request_type="TCP",
                        name="send_command",
                        response_time=total_time,
                        response_length=len(response),
                        exception=None
                    )
                except Exception as e:
                    print("error",e)
                    self.environment.events.request.fire(
                        request_type="TCP",
                        name="send_command",
                        response_time=total_time,
                        response_length=0,
                        exception=e
                    )

                    break  # stop sending commands on error

            sock.close()
            print(f"Connection closed after 1000 commands")

        except Exception as e:
            print(f"Failed to connect: {e}")
