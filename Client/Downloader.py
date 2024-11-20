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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #STILL CODING AAAAAAAA
            pass


if __name__ == "__main__":
    downloader = Downloader()
    downloader.start_downloader()

