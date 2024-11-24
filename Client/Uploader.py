import base64, json, hashlib, math, os, socket, threading, time

config_file = "Config//client_config.txt"

class Uploader:

    def __init__(self):
        self.uploader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    
    def start_uploader(self):
        if not self.server_ip:
            print("Cannot connect to tracker")
            return
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
        try:
            if not os.path.exists(f"Uploads//{file}"):
                print(f"File {file} not found.")
                return
            base, ext = file.split('.')
            os.makedirs(f"Torrents//{file}", exist_ok = True)

            totalparts = math.ceil(os.path.getsize(f"Uploads//{file}")/(512*1024))
            magnetinfo = {}
            with open(f"Uploads//{file}", "rb") as reading_file:
                magnetinfo["file"] = file
                magnetinfo["totalparts"] = totalparts
                magnetinfo["checksum"] = self.calculate_checksum(f"Uploads//{file}")
                magnetinfo["uploader"] = (self.ip, self.port)
                magnetinfo["fragments"] = []

                for i in range(totalparts):
                    with open(f"Torrents//{file}//{base}_{ext}_{i+1}.fragment", "w") as writing_part:
                        part = {}
                        part["text"] = base64.b64encode(reading_file.read(512*1024)).decode('utf-8')
                        json.dump(part, writing_part, indent=4)
                        magnetinfo["fragments"].append(f"{base}_{ext}_{i+1}.fragment")
                        print(f"[{file}] is uploading: {round((i+1)/totalparts*100,2)} %")
                
                with open(f"Torrents//{file}//{base}_{ext}.torrent", "w") as writing_magnetinfo:
                    json.dump(magnetinfo, writing_magnetinfo, indent=4)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip,self.server_port))
                s.sendall("UPLOAD".encode('utf-8'))
                time.sleep(0.5)
                s.sendall(json.dumps(magnetinfo).encode('utf-8'))

        except Exception as e:
            print(f"[Error occured at upload()]\n{e}")


if __name__ == "__main__":
    uploader = Uploader()
    uploader.start_uploader()

