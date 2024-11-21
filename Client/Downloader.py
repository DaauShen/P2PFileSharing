import hashlib, math, os, socket, threading

config_file = "Config//client_config.txt"

class Downloader:
    def __init__(self):
        self.downloader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = self.load_ip_port()

    def load_ip_port(self):
        with open(config_file, "r") as file:
            ip, port = file.read().splitlines()
            return ip, int(port)
        
    def calculate_checksum(self,file_path):
        hash_func = hashlib.sha256()
        with open(file_path, "rb") as f:
            chunk = f.read(512*1024)
            hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def start_downloader(self):
        try:
            self.downloader_socket.connect((self.ip, self.port)) #This step to make sure that downloader is called by Client
            print("Enter the file(s) that you want to download, each separate with a single space character")
            files = input(">> ").strip().split(' ')
            for file in files:
                thr = threading.Thread(target = self.download, args = [file,])
                thr.start()

        except Exception as e:
            print(f"[Error occured at start_downloader()]\n{e}")

    def download(self, file):
        base, ext = file.split('.')
        torrent_path = f"Torrents//{file}//{base}_{ext}.torrent"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost',6969)) #Connect to tracker
            s.sendall("DOWNLOAD".encode())
            response = s.recv(1024).decode()
            if response == "NOTFOUND":
                print(f"File {file} is not uploaded!")
                return
            elif response == "FOUND":
                s.sendall("OK".encode())
                with open(torrent_path, "wb") as writing_torrent:
                    while chunk := s.recv(1024):
                        writing_torrent.write(chunk)
                s.sendall("OK".encode())
            else: #Invalid data
                return
            online_list = []
            while True:
                data = s.recv(1024)
                if data == "END":
                    break
                ip, port = data.split(' ')
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_connection:
                        test_connection.connect((ip,int(port)))
                        test_connection.sendall("TEST")
                        online_list.append((ip,port))
                except Exception:
                    pass
                s.sendall("OK".encode())
            
        #Download each fragment
        checksum_dict = {}
        tasks = {}
        parts = []
        with open(torrent_path, "rb") as reading_torrent:
            file_name, total_parts = reading_torrent.readline().decode().strip().split()
            # Loop through the remaining lines
            for line in reading_torrent:
                # Split each line into part name and checksum
                part_name, checksum = line.decode().strip().split()
                parts.append(part_name)
                checksum_dict[part_name] = checksum
        for part in parts:
            for i in range(len(online_list)):
                ip, port = online_list[i]
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ip,int(port)))
                        s.sendall("CHECK".encode())
                        r = s.recv(1024).decode()
                        s.sendall(f"{file} {part}".encode())
                        r = s.recv(1024).decode()
                        if r == "FOUND":
                            tasks[part] = (ip, port)
                            online_list = online_list[i+1:] + online_list[:i+1]
                        else:
                            continue
                except Exception:
                    continue
        if len(parts) != total_parts:
            print(f"File {file} is missing part(s)!")
            return 
        #After assign all tasks, start downloading by using multithread
        check = {}
        for part in tasks:
            ip, port = tasks[part]
            thr = threading.Thread(target = self.download_part, args = [file,part,ip,port,check])
            thr.start()

        while len(check) != total_parts: #Waiting for all parts
            pass

        for part in check:
            if check[part] != checksum_dict[part]:
                print(f"File {file} is damaged!")
                return
        
        with open(f"Downloads//{file}", "wb") as writing_file:
            for part in parts:
                with open(f"Torrents//{file}//{part}", "rb") as reading_part:
                    while chunk := reading_part.read(1024):
                        if not chunk:
                            break
                        writing_file.write(chunk)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost',6969))
            s.sendall("ASSIGN".encode())
            ok = s.recv(1024).decode()
            s.sendall(f"{file} {self.ip} {self.port}".encode())
            

    def download_part(self,file,part,ip,port,check):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip,int(port)))
            s.sendall("REQUEST".encode())
            ok = s.recv(1024).decode()
            s.sendall(f"{file} {part}".encode())
            with open(f"Torrents//{file}//{part}", "wb") as writing_part:
                while chunk := s.recv(1024):
                    if not chunk:
                        break
                    writing_part.write(chunk)
        
        check[file] = self.calculate_checksum(f"Torrents//{file}//{part}")
            
            
                        


                



if __name__ == "__main__":
    downloader = Downloader()
    downloader.start_downloader()

