import socket
import tqdm
import time
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
import sys
import random




# a python program to send an initial packet, then listen for packets from the ESP32
# the laptop/rasp pi that this code runs on can still be connected to the internet, but should also "share" its connection by creating its own mobile hotspot
# this version of the code allows your laptop to remain connected to the internet (which is a postive)
# but requires configuring your laptop to share its internet connection (which can be a negative because it is tricky to set up depending on your OS)
# for version that does not require sharing an internet connection, see https://gist.github.com/santolucito/70ecb94ce297eb1b8b8034f78683447b 
# use ifconfig -a to find this IP. If your pi is the first and only device connected to the ESP32, 
# this should be the correct IP by default on the raspberry pi

LOCAL_UDP_IP = "192.168.1.2"
SHARED_UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((LOCAL_UDP_IP, SHARED_UDP_PORT))
      
 
def loop():
    # Handshake
    data, addr = sock.recvfrom(2048)
    while data != b"Hello":
        data, addr = sock.recvfrom(2048)
    # print(addr)
    sock.sendto("Send Data".encode(), addr)

    while(data!=b'Done Sending'):

        data, addr = sock.recvfrom(2048)
        details = data.split()
        intro = details[0]

        if intro ==b'FILE:':
            filename = details[1].decode()
            fileSize = int(details[3].decode())
            file_extension = details[5].decode()
            print(details)
            if (file_extension == "txt"):
                print(filename)
                myFile = open(filename, "w")
                file_bytes = ""
                done = False
                progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=fileSize)

                while not done:
                    data, addr = sock.recvfrom(2048)
                    if data == b"<NEXT>" :
                        done = True
                    else:
                        # get data and try to clean 
                        # print(data)
                        file_bytes += data.decode(encoding="utf-8", errors="ignore").rstrip(".\\.x\\.?\\9\\.(.\\.).")  
                    progress.update(2048)
                    print("\n")

                myFile.write(file_bytes) 
                myFile.close()

            else:
                print(filename)
                myFile = open(filename, "wb")
                file_b = b""
                done = False
                while not done:
                    data, addr = sock.recvfrom(2048)
                    if data == b"<NEXT>" :
                        done = True
                    else:
                        file_b += data.rstrip()
               
                # print(file_b)
                # image = cv2.imdecode(np.frombuffer([file_b], dtype=np.uint8), cv2.IMREAD_COLOR)
                # # Display the image
                # cv2.imshow(filename, image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                myFile.write(file_b) 
                myFile.close()
            print("\n")
        


if __name__ == "__main__":

    try:
        loop()

    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit()


# image = cv2.imdecode(np.frombuffer(file_b, dtype=np.uint8), cv2.IMREAD_COLOR)
# # Display the image
# cv2.imshow(filename, image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()