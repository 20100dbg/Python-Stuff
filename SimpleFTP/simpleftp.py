import argparse
import datetime
import os
import platform
import random
import socket
import stat
import threading
import time
from pathlib import Path


class SimpleFTP:

    def __init__(self, port=21, root_dir="data", login="anonymous", password="anonymous", debug=False):

        if debug:
            print(f"Starting FTP server on port {port}")

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(1)

        if root_dir[0] == "/":
            self.root_dir = Path(root_dir)
        else:
            self.root_dir = Path(os.getcwd() + "/" + root_dir)

        if debug:
            print(f"Root dir is {self.root_dir}")
        
        self.current_dir = self.root_dir
        self.valid_creds = [login, password]
        self.current_creds = ["", ""]
        self.data_type = "ascii"
        self.debug = debug

        self.listener()
        

    def start_data_listener(self, port):

        if self.debug:
            print(f"Starting FTP-DATA server on port {port}")

        server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_data.bind(('0.0.0.0', port))
        server_data.listen(1)

        self.client_data, client_address = server_data.accept()

        while True:
            if not self.client_data:
                break


    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
        

    def handle(self, client, msg_received):

        if self.debug:
            print(f"Received command : {msg_received}")

        if " " in msg_received:
            cmd, arg = msg_received.split(' ', maxsplit=2)
        else:
            cmd = msg_received
            arg = None

        if cmd == "USER":
            self.current_creds[0] = arg
            client.send("331 Please specify password.\n".encode())
        
        elif cmd == "PASS":
            self.current_creds[1] = arg

            if self.valid_creds == ["anonymous", "anonymous"] or \
                (self.valid_creds[0] == self.current_creds[0] and \
                self.valid_creds[1] == self.current_creds[1]):
                client.send("230 Login successful.\n".encode())

                if self.debug:
                    print(f"Login successful for {self.current_creds[0]}")

            else:
                client.send("530 Login incorrect.\n".encode())

                if self.debug:
                    print(f"Login incorrect for {self.current_creds[0]}")


        elif cmd == "SYST":
            client.send(f"215 {platform.system()}\n".encode())


        elif cmd == "FEAT":
            client.send("211-Features:\n".encode())
            client.send("EPSV\n".encode())
            client.send("211 End\n".encode())


        elif cmd == "EPSV":
            passive_port = random.randint(10000,65000)

            t = threading.Thread(target=self.start_data_listener,args=[passive_port])
            t.start()
            time.sleep(0.1)
            client.send(f"229 Entering Extended Passive Mode (|||{passive_port}|)\n".encode())


        elif cmd == "LIST":

            client.send(f"150 Here comes the directory listing.\n".encode())

            output = ""
            for entry in os.scandir(self.current_dir):
                file_info = os.stat(self.current_dir / entry.name)
                permissions = stat.filemode(file_info.st_mode)

                last_modification = datetime.datetime.fromtimestamp(file_info.st_mtime)
                last_modification = last_modification.strftime("%b %d %Y")

                output += f"{permissions}\t{file_info.st_nlink}\t{file_info.st_uid}\t{file_info.st_gid}\t{file_info.st_size}\t{last_modification}\t{entry.name}\r\n"

            self.client_data.send(output.encode())
            self.client_data.close()
            self.client_data = None
            client.send(f"226 Directory send OK.\n".encode())

        elif cmd == "NLST":

            client.send(f"150 Here comes the directory listing.\n".encode())

            output = ""
            for entry in os.scandir(self.current_dir):
                output += f"{entry.name}\r\n"

            self.client_data.send(output.encode())
            self.client_data.close()
            self.client_data = None
            client.send(f"226 Directory send OK.\n".encode())


        elif cmd == "CWD":

            new_path = self.current_dir / arg
            new_path = new_path.resolve()

            if self.debug:
                print(f"new path : {new_path}")

            #Force to stay in FTP root dir
            if new_path.is_relative_to(self.root_dir):
                self.current_dir = new_path
                client.send("250 Directory successfully changed.\n".encode())
            else:
                client.send("550 Failed to change directory.\n".encode())


        elif cmd == "TYPE":

            if arg == "I":
                self.data_type = "bin"
                client.send("200 Switching to Binary mode.\n".encode())
            
            elif arg == "A":
                self.data_type = "ascii"
                client.send("200 Switching to ASCII mode.\n".encode())
        

        elif cmd == "SIZE":
            arg = self.current_dir / arg
            client.send(f"212 {os.path.getsize(arg)}\n".encode())


        elif cmd == "MDTM":
            arg = self.current_dir / arg
            file_info = os.stat(path / entry.name)
            client.send(f"213 {file_info.st_mtime}\n".encode())


        elif cmd == "RETR":

            filename = arg
            filepath = self.current_dir / filename
            filepath = filepath.resolve()

            if filepath.is_relative_to(self.root_dir) and os.path.isfile(filepath):

                filemode = 'r'
                if self.data_type == "bin":
                    filemode = 'rb'

                client.send(f"150 Opening {self.data_type} mode data connection for {filename} ({os.path.getsize(filepath)} bytes).\n".encode())                

                with open(filepath, filemode) as f:
                    self.client_data.send(f.read())
                    self.client_data.close()
                    self.client_data = None
                    client.send("226 Transfer complete.\n".encode())
                    
            else:
                client.send("535 Failed security check. \n".encode())


        elif cmd == "STOR":

            filename = arg
            filepath = self.current_dir / filename
            filepath = filepath.resolve()

            if filepath.is_relative_to(self.root_dir) and os.path.isfile(filepath):

                client.send("150 Ok to send data.\n".encode())

                filemode = 'w'
                if self.data_type == "bin":
                    filemode = 'wb'

                with open(filepath, filemode) as f:
                    while True:
                        data = self.client_data.recv(1024)
                        f.write(data)
                        if not data:
                            break

                self.client_data.close()
                self.client_data = None

                client.send("226 Transfer complete.\n".encode())
            else:
                client.send("535 Failed security check. \n".encode())


        elif cmd == "QUIT":
            client.send(f"221 Goodbye.\n".encode())
            client.close()

        else:
            client.send(f"502 Command not implemented.\n".encode())



    def listener(self):

        while True:
            client, client_address = self.server.accept()

            try:
                print(f"Connected to client: {client_address}")
                
                client.send("220 SimpleFTP 0.1\n".encode())

                while True:
                    data = client.recv(1024)
                    
                    if data:
                        data = data.decode('utf-8').strip()
                        self.handle(client, data)

                        if data == "QUIT":
                            break

            except Exception as e:
                print(f"Exception : {e}")
            finally:
                client.close()


parser = argparse.ArgumentParser(description='')

group1 = parser.add_argument_group('Basic options')
group1.add_argument('-p', '--port', metavar='', type=int, default=21, required=False, help='Port to listen')
group1.add_argument('-r', '--root-dir', metavar='', default="data", required=False, help='FTP root directory')
group1.add_argument('-l', '--login', metavar='', default="anonymous", required=False, help='Login')
group1.add_argument('-a', '--password', metavar='', default="anonymous", required=False, help='Password')
group1.add_argument('-d', '--debug', action='store_true', required=False, help='Output debug informations')
args = parser.parse_args()



ftp = SimpleFTP(port=args.port, root_dir=args.root_dir, login=args.login, password=args.password, debug=args.debug)
