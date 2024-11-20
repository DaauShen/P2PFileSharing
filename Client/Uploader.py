import hashlib, math, os, socket, threading

config_file = "Config//client_config.txt"

class Uploader:
    def __init__(self):
        self.uploader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    
    def start_uploader(self):
        try:
            self.uploader_socket.connect((self.ip, self.port)) #This step to make sure that uploader is called by Client
            print("Remember to put the file(s) you want to upload to the 'Uploads' folder.")
            print("Enter the file(s) that you want to upload, each separate with a single space character")
            files = input(">> ").strip().split(' ')
            for file in files:
                thr = threading.Thread(target = self.upload, args = [file,])
                thr.start()

        except Exception as e:
            print(f"[Error occured at start_uploader()]\n{e}")

    def upload(self, file):
        if os.path.exists(f"Uploads//{file}"):
            try:
                os.makedirs(f"Torrents//{file}", exist_ok = False)
                num = math.ceil(os.path.getsize(f"Uploads//{file}") / (512*1024))
                base, ext = file.split('.')
                with open(f"Uploads//{file}", "rb") as reading_file, open(f"Torrents//{file}//{base}_{ext}.torrent", "wb") as writing_torrent:
                    writing_torrent.write(f"{file} {num}\n".encode())
                    part = 1
                    while True:
                        chunk = reading_file.read(512*1024)
                        if not chunk:
                            break
                        with open(f"Torrents//{file}//{base}_{ext}_part{part}.fragment", "wb") as writing_part:
                            writing_part.write(chunk)
                        writing_torrent.write(f"{base}_{ext}_part{part}.fragment {self.calculate_checksum(f"Torrents//{file}//{base}_{ext}_part{part}.fragment")}\n".encode())
                        part += 1
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('localhost',6969))
                    s.sendall("UPLOAD".encode())
                    temp = s.recv(1024).decode() #waiting
                    s.sendall((f"{file} {self.ip} {self.port}").encode())
                    temp = s.recv(1024).decode() #waiting
                    with open(f"Torrents//{file}//{base}_{ext}.torrent", "rb") as reading_torrent:
                        while chunk := reading_torrent.read(1024):
                            if not chunk:
                                break
                            s.sendall(chunk)
                    print(f"Uploaded {file} sucessfully!")
            except FileExistsError:
                print(f"File {file} is already uploaded!")

        else:
            print(f"File {file} doesn't exist.")


if __name__ == "__main__":
    uploader = Uploader()
    uploader.start_uploader()

