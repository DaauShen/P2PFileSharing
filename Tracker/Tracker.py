import json, os, socket, threading, time

class Tracker:
    def take_data(self):
        if os.path.exists("Dictionary//dict.json"):
            with open("Dictionary//dict.json", "r") as json_file:
                data = json.load(json_file)
            return data
        else:
            return {}
        
    def autosave(self):
        with open("Dictionary//dict.json", "w") as json_file:
            json.dump(self.dict, json_file, indent=4)

    def __init__(self):
        os.makedirs("Dictionary", exist_ok = True)
        os.makedirs("Tracker_torrents", exist_ok = True)
        
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = "192.168.1.100", 6969
        self.dict = self.take_data()
        self.tracker_socket.bind((self.ip,self.port))
        print(f"Tracker hosted at {self.ip}:{self.port}")
        print("Listening for request...")

    def start_tracker(self):
        try:
            self.tracker_socket.listen(500)
            while True:
                conn, addr = self.tracker_socket.accept()
                thr = threading.Thread(target = self.handle_thread, args = [conn,])
                thr.start()

        except Exception as e:
            print(f"[Error occured in start_tracker()]\n{e}")
            self.stop_tracker()

    def stop_tracker(self):
        print("Tracker is shutting down...")
        self.tracker_socket.close()
    
    def handle_thread(self, conn):
        cmd = conn.recv(1024).decode('utf-8')
        if cmd == "UPLOAD":
            magnetinfo = conn.recv(1024).decode('utf-8')
            magnetinfo = json.loads(magnetinfo)
            base, ext = magnetinfo["file"].split('.')
            with open(f"Tracker_torrents//{base}_{ext}.torrent", "w") as writing_torrent:
                json.dump(magnetinfo, writing_torrent, indent=4)
            self.dict[magnetinfo["file"]] = {}
            self.dict[magnetinfo["file"]]["seeders"] = []
            self.dict[magnetinfo["file"]]["seeders"].append(magnetinfo["uploader"])
            self.dict[magnetinfo["file"]]["path"] = f"Tracker_torrents//{base}_{ext}.torrent"
            self.autosave()
            print(f"{magnetinfo['uploader']} uploaded {magnetinfo['file']}")

        elif cmd == "DOWNLOAD":
            requirements = conn.recv(1024).decode('utf-8')
            requirements = json.loads(requirements)
            file = requirements["file"]
            ip, port = requirements["downloader"]
            if file in self.dict:
                conn.sendall("FOUND".encode('utf-8'))
                full_info = {}
                full_info["list"] = self.dict[file]["seeders"]
                with open(self.dict[file]["path"], "r") as reading_torrent:
                    full_info["magnetinfo"] = json.load(reading_torrent)
                time.sleep(0.5)
                conn.sendall(json.dumps(full_info).encode('utf-8'))
                if (ip,port) not in self.dict[file]["seeders"]:
                    self.dict[file]["seeders"].append((ip, port))
                    self.autosave()
                print(f"({ip}:{port}) downloaded {file} and became a seeder.")
            else:
                conn.sendall("NOTFOUND".encode('utf-8'))
                return
        else:
            return
        


if __name__ == "__main__":
    tracker = Tracker()
    tracker.start_tracker()

