import socket
import tqdm
import sys

# a python program to send an initial packet, then listen for packets from the ESP32
# but requires configuring your laptop to share its internet connection (which can be a negative because it is tricky to set up depending on your OS)
# for version that does not require sharing an internet connection, see https://gist.github.com/santolucito/70ecb94ce297eb1b8b8034f78683447b 
LOCAL_UDP_IP = "192.168.1.2"
SHARED_UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((LOCAL_UDP_IP, SHARED_UDP_PORT))

def saveData(fn, ext, fileSize):
    print("\n%s" % fn)
    myFile = None
    file_b =""
    if ext == "txt":
        myFile = open(fn, "w")
    else:
        myFile = open(fn, "wb")
        file_b = b""
        
    done = False
    progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=2048, total=fileSize)
    while not done:
        data, addr = sock.recvfrom(2048)
        if data == b"<NEXT>" :
            done = True
        else:
            if ext == "txt":
                file_b+= data.decode(encoding="utf-8", errors="ignore").rstrip(".\\.x\\.?\\9\\.(.\\.).") 
            else:
                file_b += data.rstrip()
        progress.update(2048)
    myFile.write(file_b) 
    myFile.close()
    print("\n")

 
def loop():
    # Handshake
    data, addr = sock.recvfrom(2048)
    while data != b"Hello":
        data, addr = sock.recvfrom(2048)
    print("Ready to Get Data")
    sock.sendto("Send Data".encode(), addr)
    while(data!=b'Done Sending'):
        data, addr = sock.recvfrom(2048)
        details = data.split()
        intro = details[0]
        if intro ==b'FILE:':
            filename = details[1].decode()
            fileSize = int(details[3].decode())
            file_extension = details[5].decode()
            saveData(filename, file_extension, fileSize)
    print("Done.")


if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        sys.exit()
