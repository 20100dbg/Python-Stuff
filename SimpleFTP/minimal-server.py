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

        self.debug = debug

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(1)

        self.root_dir = os.path.abspath(root_dir)
        self.current_dir = ""
        
        self.valid_creds = [login, password]
        self.current_creds = ["", ""]
        self.data_type = "A"
        self.auth = False

        self.listener()


    def print_debug(self, txt):
        if self.debug:
            print(txt)
        

    def start_data_listener(self, port):

        server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_data.bind(('0.0.0.0', port))
        server_data.listen(1)

        self.socket_data, client_address = server_data.accept()

        while True:
            if not self.socket_data:
                break


    def handle(self, client, msg_received):
        self.print_debug(f"Received : {msg_received}")

        if " " in msg_received:
            cmd, arg = msg_received.split(' ', maxsplit=1)
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
                self.auth = True

            else:
                client.send("530 Login incorrect.\n".encode())


        if cmd == "USER" or cmd == "PASS":
            return None

        elif cmd == "AUTH" or not self.auth:
            client.send("530 Please login with USER and PASS.\n".encode())
            return None

        if cmd == "SYST":
            client.send(f"215 {platform.system()}\n".encode())

        elif cmd == "FEAT":
            client.send("211-Features:\n".encode())
            client.send(" EPSV\n".encode())
            client.send(" MDTM\n".encode())
            client.send(" SIZE\n".encode())
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
            current_path = os.path.join(self.root_dir, self.current_dir)

            if os.path.isdir(current_path):

                for entry in os.scandir(current_path):
                    file_info = os.stat(os.path.join(current_path, entry.name))
                    permissions = stat.filemode(file_info.st_mode)
                    last_modification = datetime.datetime.fromtimestamp(file_info.st_mtime).strftime("%b %d %Y")

                    output += f"{permissions}    {file_info.st_nlink}    {file_info.st_uid}    {file_info.st_gid}    {file_info.st_size}    {last_modification}    {entry.name}\r\n"


                self.socket_data.send(output.encode())
                self.socket_data.close()
                self.socket_data = None

                client.send(f"226 Directory send OK.\n".encode())

            else:
                client.send("550 Directory read failed : not found.\n".encode())


        elif cmd == "NLST":

            client.send(f"150 Here comes the directory listing.\n".encode())

            output = ""
            current_path = os.path.join(self.root_dir, self.current_dir)

            if os.path.isdir(current_path):

                for entry in os.scandir(current_path):
                    output += f"{entry.name}\r\n"

                self.socket_data.send(output.encode())
                self.socket_data.close()
                self.socket_data = None
                client.send(f"226 Directory send OK.\n".encode())
            
            else:
                client.send("550 Directory read failed : not found.\n".encode())


        elif cmd == "PWD":
            client.send(f'257 "/{self.current_dir}" is the current directory\n'.encode())


        elif cmd == "CWD":

            new_path, new_dir = self.get_new_path(arg, self.current_dir)
            new_path = os.path.normpath(new_path)

            #Force to stay in FTP root dir
            if self.path_starts_with(self.root_dir, new_path):
                self.current_dir = new_dir

                client.send("250 Directory successfully changed.\n".encode())
            else:
                client.send("550 Failed to change directory.\n".encode())


        elif cmd == "TYPE":

            self.data_type = arg

            if arg == "I":
                client.send("200 Switching to Binary mode.\n".encode())
            
            elif arg == "A":
                client.send("200 Switching to ASCII mode.\n".encode())
        

        elif cmd == "SIZE":
            filepath, new_dir = self.get_new_path(arg, self.current_dir)

            if os.path.isfile(filepath):
                client.send(f"212 {os.path.getsize(filepath)}\n".encode())

            else:
                client.send(f"550 Failed to open file.\n".encode())


        elif cmd == "MDTM":
            filepath, new_dir = self.get_new_path(arg, self.current_dir)

            file_info = os.stat(filepath)
            date_formated = datetime.datetime.fromtimestamp(file_info.st_mtime)
            date_formated = date_formated.strftime("%Y%m%d%H%M%S")

            client.send(f"213 {date_formated}\n".encode())



        elif cmd == "RETR":

            filepath, new_dir = self.get_new_path(arg, self.current_dir)
            filename = os.path.basename(filepath)

            if self.path_starts_with(self.root_dir, filepath):

                if os.path.isfile(filepath):

                    client.send(f"150 Opening {self.data_type} mode data connection for {filename} ({os.path.getsize(filepath)} bytes).\n".encode())

                    with open(filepath, 'rb') as f:
                        self.socket_data.send(f.read())
                        self.socket_data.close()
                        self.socket_data = None
                        client.send("226 Transfer complete.\n".encode())
                        
                else:
                    client.send(f"550 Failed to open file.\n".encode())

            else:
                client.send("535 Failed security check. \n".encode())


        elif cmd == "STOR":

            filepath, new_dir = self.get_new_path(arg, self.current_dir)

            if self.path_starts_with(self.root_dir, filepath):

                client.send("150 Ok to send data.\n".encode())

                with open(filepath, 'wb') as f:
                    while True:
                        data = self.socket_data.recv(1024)

                        f.write(data)
                        if not data:
                            break

                self.socket_data.close()
                self.socket_data = None

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


    def path_starts_with(self, parent_path, child_path):
        return True
        return child_path[:len(parent_path)] == parent_path


    def get_new_path(self, path, current_dir):
        if path[0] == "/":
            path = path[1:]
            new_path = os.path.join(self.root_dir, path)
            new_dir = path
        else:
            new_path = os.path.join(self.root_dir, current_dir, path)
            new_dir = os.path.join(current_dir, path)

        return new_path, new_dir



parser = argparse.ArgumentParser(description='')

group1 = parser.add_argument_group('Basic options')
group1.add_argument('-p', '--port', metavar='', type=int, default=21, required=False, help='Port to listen')
group1.add_argument('-r', '--root-dir', metavar='', default="data", required=False, help='FTP root directory')
group1.add_argument('-l', '--login', metavar='', default="anonymous", required=False, help='Login')
group1.add_argument('-a', '--password', metavar='', default="anonymous", required=False, help='Password')
group1.add_argument('-d', '--debug', action='store_true', required=False, help='Output debug informations')
args = parser.parse_args()



ftp = SimpleFTP(port=args.port, root_dir=args.root_dir, login=args.login, password=args.password, debug=args.debug)
