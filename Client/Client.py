import base64, json, os, random, socket, subprocess, threading

config_file = "Config//client_config.txt"

class Client:

    def get_random_port(self):
        return random.randint(1024, 65535)  # Use ports in the dynamic range

    def generate_and_save_ip_port(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = self.get_random_port()

        # Save the IP and port to a file
        with open(config_file, "w") as file:
            file.write(f"{ip}\n{port}")
        print(f"Generated and saved IP: {ip}, Port: {port}")
        return ip, port

    def load_ip_port(self):
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                ip, port = file.read().splitlines()
                print(f"Loaded IP: {ip}, Port: {port}")
                return ip, int(port)
        else:
            return self.generate_and_save_ip_port()


    def __init__(self):
        os.makedirs("Torrents", exist_ok = True)
        os.makedirs("Uploads", exist_ok = True)
        os.makedirs("Downloads", exist_ok = True)
        os.makedirs("Config", exist_ok = True)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = self.load_ip_port()
        while True:
            try:
                self.client_socket.bind((self.ip,self.port))
                break
            except OSError:
                self.ip, self.port = self.generate_and_save_ip_port()
                continue
        print(f"Client {self.ip}:{self.port} is online!")

    def client_listening(self):
        try:
            self.client_socket.listen(500)
            while True:
               conn, addr = self.client_socket.accept()
               thr = threading.Thread(target = self.thread_handling, args = [conn,])
               thr.start()
                    
        except Exception as e:
            return
            # print(f"[Error occured at client_listening()]\n{e}")

    def thread_handling(self, conn):
        cmd = conn.recv(1024).decode('utf-8')
        if cmd == "CHECK":
            file, part = conn.recv(1024).decode('utf-8').split(' ')
            if os.path.exists(f"Torrents//{file}//{part}"):
                conn.sendall("EXIST".encode('utf-8'))
            else:
                conn.sendall("NOTEXIST".encode('utf-8'))
        elif cmd == "DOWNLOAD":
            file, part = conn.recv(1024).decode('utf-8').split(' ')
            with open(f"Torrents//{file}//{part}", "r") as reading_part:
                data = json.load(reading_part)
            conn.sendall(json.dumps(data).encode('utf-8'))
        else:
           pass
    def start_client(self):
        thr = threading.Thread(target = self.client_listening)
        thr.start()
        while True:
            print("\nEnter COMMAND:")
            print("UPLOAD if you want to upload file(s)")
            print("DOWNLOAD if you want to download file(s)")
            print("EXIT if you want to exit the program.")
            cmd = input(">> ").strip()
            if cmd == "UPLOAD":
                subprocess.Popen(["start", "cmd", "/k", "python", "Uploader.py"], shell = True)
            elif cmd == "DOWNLOAD":
                subprocess.Popen(["start", "cmd", "/k", "python", "Downloader.py"], shell = True)
            elif cmd == "EXIT":
                break

            else:
                print("INVALID COMMAND!")

        

    def stop_client(self):
        print(f"Client {self.ip}:{self.port} is going to offline!")
        self.client_socket.close()


if __name__ == "__main__":
    client = Client()
    client.start_client()
    client.stop_client()
