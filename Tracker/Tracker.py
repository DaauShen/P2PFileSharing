import json, os, socket, threading

def torrent_path(filename):
    base, ext = filename.split('.')
    return os.path.join("Tracker_torrents",filename,f"{base}_{ext}.torrent")


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
        self.ip = '0.0.0.0'
        self.port = 6969
        self.dict = self.take_data()
        self.tracker_socket.bind((self.ip,self.port))
        print("Tracker started at 0.0.0.0: 6969 and listening for request...")
    
    def handle_thread(self, conn):
        cmd = conn.recv(1024).decode()
        if cmd == "UPLOAD":
            conn.send("OK".encode())
            file, ip, port = conn.recv(1024).decode().split(' ')
            conn.send("OK".encode())
            base, ext = file.split('.')
            with open(f"Tracker_torrents//{base}_{ext}.torrent", "wb") as writing_torrent:
                while chunk := conn.recv(1024):
                    if not chunk:
                        break
                    writing_torrent.write(chunk)
            if file in self.dict:
                self.dict[file].append((ip,port))
            else:
                self.dict[file] = [(ip,port),]
            self.autosave()
            print(f"{ip}:{port} uploaded {file}!")
        else:
            #STILL CODING AAAAAAA
            pass
        

    def start_tracker(self):
        try:
            self.tracker_socket.listen(5)
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


if __name__ == "__main__":
    tracker = Tracker()
    tracker.start_tracker()

