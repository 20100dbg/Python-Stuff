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
        self.print_debug(f"Starting FTP server on port {port}")

        if port < 1024 and os.getuid() != 0:
            self.print_debug(f"WARNING : trying to listen on port {port} with euid {os.getuid()}")


        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(1)

        self.root_dir = os.path.abspath(root_dir)
        self.print_debug(f"Root dir is {self.root_dir}")
        
        self.valid_creds = [login, password]
        self.current_dir = ""
        self.current_creds = ["", ""]
        self.data_type = "ascii"

        self.listener()
        

    def start_data_listener(self, port):

        self.print_debug(f"Starting FTP-DATA server on port {port}")

        server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_data.bind(('0.0.0.0', port))
        server_data.listen(1)

        self.client_data, client_address = server_data.accept()

        while True:
            if not self.client_data:
                break


    def print_debug(self, txt):
        if self.debug:
            print(txt)


    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
        

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
            self.print_debug("331 Please specify password.\n".encode())
        
        elif cmd == "PASS":
            self.current_creds[1] = arg

            if self.valid_creds == ["anonymous", "anonymous"] or \
                (self.valid_creds[0] == self.current_creds[0] and \
                self.valid_creds[1] == self.current_creds[1]):
                client.send("230 Login successful.\n".encode())
                self.print_debug(f"Login successful for {self.current_creds[0]}")

            else:
                client.send("530 Login incorrect.\n".encode())
                self.print_debug(f"Login incorrect for {self.current_creds[0]}")


        elif cmd == "SYST":
            client.send(f"215 {platform.system()}\n".encode())
            self.print_debug(f"215 {platform.system()}\n".encode())


        elif cmd == "FEAT":
            client.send("211-Features:\n".encode())
            client.send(" EPSV\n".encode())
            client.send(" PASV\n".encode())
            client.send(" MDTM\n".encode())
            client.send(" SIZE\n".encode())
            client.send("211 End\n".encode())


        elif cmd == "EPSV":
            passive_port = random.randint(10000,65000)

            t = threading.Thread(target=self.start_data_listener,args=[passive_port])
            t.start()
            time.sleep(0.1)
            client.send(f"229 Entering Extended Passive Mode (|||{passive_port}|)\n".encode())
            self.print_debug(f"229 Entering Extended Passive Mode (|||{passive_port}|)\n".encode())


        elif cmd == "PASV":
            passive_port = random.randint(10000,65000)

            t = threading.Thread(target=self.start_data_listener,args=[passive_port])
            t.start()
            time.sleep(0.1)

            local_ip = client.getsockname()[0]
            p2 = passive_port % 256
            p1 = passive_port // 256

            client.send(f"227 Entering Passive Mode ({local_ip.replace('.', ',')},{p1},{p2})\n".encode())
            self.print_debug(f"227 Entering Passive Mode ({local_ip.replace('.', ',')},{p1},{p2})\n".encode())


        elif cmd == "LIST":

            client.send(f"150 Here comes the directory listing.\n".encode())
            self.print_debug(f"150 Here comes the directory listing.\n".encode())

            output = ""
            current_path = os.path.join(self.root_dir, self.current_dir)

            for entry in os.scandir(current_path):
                current_file = os.path.join(current_path, entry.name)

                file_info = os.stat(current_file)
                permissions = stat.filemode(file_info.st_mode)

                last_modification = datetime.datetime.fromtimestamp(file_info.st_mtime)
                last_modification = last_modification.strftime("%b %d %Y")

                output += f"{permissions}\t{file_info.st_nlink}\t{file_info.st_uid}\t{file_info.st_gid}\t{file_info.st_size}\t{last_modification}\t{entry.name}\r\n"


            if arg and "a" in arg and "l" in arg:
                output = output.replace('\t', ' ' * 4)


            self.client_data.send(output.encode())
            self.client_data.close()
            self.client_data = None
            self.print_debug(f"{output.encode()}\n")

            client.send(f"226 Directory send OK.\n".encode())
            self.print_debug(f"226 Directory send OK.\n".encode())

        elif cmd == "NLST":

            client.send(f"150 Here comes the directory listing.\n".encode())
            self.print_debug(f"150 Here comes the directory listing.\n".encode())

            output = ""
            current_path = os.path.join(self.root_dir, self.current_dir)

            for entry in os.scandir(current_path):
                output += f"{entry.name}\r\n"

            self.client_data.send(output.encode())
            self.client_data.close()
            self.client_data = None
            client.send(f"226 Directory send OK.\n".encode())
            self.print_debug(f"226 Directory send OK.\n".encode())


        elif cmd == "AUTH":
            client.send("530 Please login with USER and PASS.\n".encode())
            self.print_debug("530 Please login with USER and PASS.\n".encode())


        elif cmd == "PWD":
            client.send(f'257 "/{self.current_dir}" is the current directory\n'.encode())
            self.print_debug(f'257 "/{self.current_dir}" is the current directory\n'.encode())


        elif cmd == "CWD":

            new_path, new_dir = self.get_new_path(arg)
            new_path = os.path.normpath(new_path)
            self.print_debug(f"new path : {new_path}")

            #Force to stay in FTP root dir
            if self.path_starts_with(self.root_dir, new_path):
                self.current_dir = new_dir

                client.send("250 Directory successfully changed.\n".encode())
                self.print_debug("250 Directory successfully changed.\n".encode())
            else:
                client.send("550 Failed to change directory.\n".encode())
                self.print_debug("550 Failed to change directory.\n".encode())


        elif cmd == "TYPE":

            if arg == "I":
                self.data_type = "bin"
                client.send("200 Switching to Binary mode.\n".encode())
                self.print_debug("200 Switching to Binary mode.\n".encode())
            
            elif arg == "A":
                self.data_type = "ascii"
                client.send("200 Switching to ASCII mode.\n".encode())
                self.print_debug("200 Switching to ASCII mode.\n".encode())
        

        elif cmd == "SIZE":
            filepath, new_dir = self.get_new_path(arg)

            client.send(f"212 {os.path.getsize(filepath)}\n".encode())
            self.print_debug(f"212 {os.path.getsize(filepath)}\n".encode())


        elif cmd == "MDTM":
            filepath, new_dir = self.get_new_path(arg)

            file_info = os.stat(filepath)
            date_formated = datetime.datetime.fromtimestamp(file_info.st_mtime)
            date_formated = date_formated.strftime("%Y%m%d%H%M%S")

            client.send(f"213 {date_formated}\n".encode())
            self.print_debug(f"213 {date_formated}\n".encode())


        elif cmd == "RETR":

            filepath, new_dir = self.get_new_path(arg)
            filename = os.path.basename(filepath)

            if self.path_starts_with(self.root_dir, filepath) and os.path.isfile(filepath):

                filemode = 'r'
                if self.data_type == "bin":
                    filemode = 'rb'

                client.send(f"150 Opening {self.data_type} mode data connection for {filename} ({os.path.getsize(filepath)} bytes).\n".encode())                
                self.print_debug(f"150 Opening {self.data_type} mode data connection for {filename} ({os.path.getsize(filepath)} bytes).\n".encode())                

                with open(filepath, filemode) as f:
                    self.client_data.send(f.read())
                    self.client_data.close()
                    self.client_data = None
                    client.send("226 Transfer complete.\n".encode())
                    self.print_debug("226 Transfer complete.\n".encode())
                    
            else:
                client.send("535 Failed security check. \n".encode())
                self.print_debug("535 Failed security check. \n".encode())


        elif cmd == "STOR":

            filepath, new_dir = self.get_new_path(arg)
            #filename = os.path.basename(filepath)
            #dirpath = os.path.dirname(fullpath)

            if self.path_starts_with(self.root_dir, filepath):

                client.send("150 Ok to send data.\n".encode())
                self.print_debug("150 Ok to send data.\n".encode())

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
                self.print_debug("226 Transfer complete.\n".encode())
            else:
                client.send("535 Failed security check. \n".encode())
                self.print_debug("535 Failed security check. \n".encode())


        elif cmd == "QUIT":
            client.send(f"221 Goodbye.\n".encode())
            self.print_debug(f"221 Goodbye.\n".encode())
            client.close()

        elif cmd == "SITE":
            args = arg.split()
            self.print_debug(args)


            if args[0] == "CHMOD":
                mode = args[1]
                filepath, new_dir = self.get_new_path(args[2])
                #self.print_debug(f"filepath {filepath}")
                #os.chmod(filepath, 0o644)

                client.send(f"200 SITE CHMOD command ok.\n".encode())
                self.print_debug(f"200 SITE CHMOD command ok.\n".encode())

        else:
            client.send(f"502 Command not implemented.\n".encode())
            self.print_debug(f"502 Command not implemented.\n".encode())



    def listener(self):

        listening = True

        while listening:
            client, client_address = self.server.accept()

            self.current_dir = ""
            self.current_creds = ["", ""]
            self.data_type = "ascii"

            try:
                print(f"Connected to client: {client_address}")
                
                client.send("220 SimpleFTP 0.1\n".encode())
                self.print_debug("220 SimpleFTP 0.1\n".encode())

                while listening:

                    try:
                        data = client.recv(1024)
                    except KeyboardInterrupt as e:
                        self.print_debug("KeyboardInterrupt")
                        data = None
                        listening = False
                    
                    if data:
                        data = data.decode('utf-8').strip()
                        self.handle(client, data)

                        if data == "QUIT":
                            break

            except Exception as e:
                print(f"Exception : {e}")
            finally:
                client.close()
                self.print_debug("Close client")

        self.print_debug("Close server")
        self.server.close()


    def path_starts_with(self, parent_path, child_path):
        return child_path[:len(parent_path)] == parent_path


    def print_path(self, path):
        if len(path) > 1 and path[-1] == "/":
            return path[:-1]
        else:
            return path


    def get_new_path(self, arg):
        if arg[0] == "/":
            arg = arg[1:]
            new_path = os.path.join(self.root_dir, arg)
            new_dir = arg
        else:
            new_path = os.path.join(self.root_dir, self.current_dir, arg)
            new_dir = os.path.join(self.current_dir, arg)

        return new_path, new_dir




parser = argparse.ArgumentParser(description='')

group1 = parser.add_argument_group('Basic options')
group1.add_argument('-p', '--port', metavar='', type=int, default=21, required=False, help='Port to listen')
group1.add_argument('-r', '--root-dir', metavar='', default="data", required=False, help='FTP root directory, relative or absolute')
group1.add_argument('-l', '--login', metavar='', default="anonymous", required=False, help='Login')
group1.add_argument('-a', '--password', metavar='', default="anonymous", required=False, help='Password')
group1.add_argument('-d', '--debug', action='store_true', required=False, help='Output debug informations')
args = parser.parse_args()

ftp = SimpleFTP(port=args.port, root_dir=args.root_dir, login=args.login, password=args.password, debug=args.debug)
