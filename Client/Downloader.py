import base64, json, hashlib, os, socket, threading, time

config_file = "Config//client_config.txt"

class Downloader:

    def __init__(self):
        self.downloader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = self.load_ip_port()
        ip = socket.gethostbyname(socket.gethostname())
        ip = ip.split('.')
        ip[-1] = "100"
        ip[-2] = "1"
        self.server_ip = '.'.join(ip)
        self.server_port = 6969

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
        if not self.server_ip:
            print("Cannot connect to tracker")
            return
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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, self.server_port))
                s.sendall("DOWNLOAD".encode('utf-8'))
                requirements = {"file": file, "downloader": (self.ip, self.port)}
                time.sleep(0.5)
                s.sendall(json.dumps(requirements).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                if response == "NOTFOUND":
                    print(f"File {file} not found.")
                    return
                data = s.recv(512*1024).decode('utf-8')
                data = json.loads(data) 
            os.makedirs(f"Torrents//{file}", exist_ok = True)
            seeder_list = data["list"]
            magnetinfo = data["magnetinfo"]
            fragments = magnetinfo["fragments"]
            assign_task = {}
            for fragment in fragments:
                if os.path.exists(f"Torrents//{file}//{fragment}"):
                    continue
                for i in range(len(seeder_list)):
                    ip, port = seeder_list[i]
                    port = int(port)
                    print(f"Checking {fragment} from {ip}:{port}")
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((ip, port))
                            s.sendall("CHECK".encode('utf-8'))
                            time.sleep(0.5)
                            s.sendall(f"{file} {fragment}".encode('utf-8'))
                            response = s.recv(1024).decode('utf-8')
                            if response == "EXIST":
                                assign_task[fragment] = (ip, port)
                                seeder_list = seeder_list[i+1:] + seeder_list[:i+1]
                                break
                            else:
                                continue
                    except Exception as e:
                        continue
            
            thrs = []

            for task in assign_task:
                thr = threading.Thread(target = self.download_fragment, args = [file, task, assign_task[task]])
                thrs.append(thr)
            
            for i in range(len(thrs)):
                if (i+1)%5 == 0:
                    time.sleep(1)
                thrs[i].start()
            
            for thr in thrs:
                thr.join()
            
            with open(f"Downloads//{file}", "wb") as writing_file:
                for fragment in fragments:
                    with open(f"Torrents//{file}//{fragment}", "r") as reading_part:
                        data = json.load(reading_part)
                        writing_file.write(base64.b64decode(data["text"]))
                
            if self.calculate_checksum(f"Downloads//{file}") == magnetinfo["checksum"]:
                print(f"[{file}] is downloaded successfully.")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.server_ip, self.server_port))
                    s.sendall("FINISH".encode('utf-8'))
                    time.sleep(0.5)
                    s.sendall(json.dumps({"file": file, "downloader": (self.ip, self.port)}).encode('utf-8'))
            else:
                print(f"[{file}] is corrupted.")

        except Exception as e:
            print(f"[Error occured at download()]\n{e}")
            
    def download_fragment(self, file, fragment, seeder):
        while True:
            try:
                ip, port = seeder
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((ip, port))
                    s.sendall("DOWNLOAD".encode('utf-8'))
                    time.sleep(0.5)
                    s.sendall(f"{file} {fragment}".encode('utf-8'))
                    data = s.recv(685*1024).decode('utf-8')
                data = json.loads(data)
                with open(f"Torrents//{file}//{fragment}", "w") as writing_part:
                    json.dump(data, writing_part, indent=4)
                print(f"[{file}] is downloading: {fragment}")
                break

            except socket.error as e:
                print(f"Cannot connect to {seeder}, stop downloading {fragment}.")
                break        
            except Exception as e:
                print(f"Error occured at download_fragment({fragment}), retrying...")   
                continue     

if __name__ == "__main__":
    downloader = Downloader()
    downloader.start_downloader()

