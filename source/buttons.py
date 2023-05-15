
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
import os 
import tkinter.messagebox
import socket
import time
from threading import Thread

LOCAL_UDP_IP = "192.168.1.2"
SHARED_UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((LOCAL_UDP_IP, SHARED_UDP_PORT))


def saveData(fn, ext, fileSize):
    text_field.insert(END, ("\nGetting: %s" % fn))

    myFile = None
    file_b =""
    if ext == "txt":
        myFile = open(fn, "w")

    else:
        myFile = open(fn, "wb")
        file_b = b""
    done = False
    barIncrement = int(fileSize/100)
    myProgress.tkraise()
    myProgress.start()
    while not done:
        data, addr = sock.recvfrom(2048)
        if data == b"<NEXT>" :
            done = True
        else:
            if ext == "txt":
                file_b+= data.decode(encoding="utf-8", errors="ignore").rstrip(".\\.x\\.?\\9\\.(.\\.).") 
            else:
                file_b += data.rstrip()
        myProgress['value'] +=barIncrement
        root.update_idletasks()

    myFile.write(file_b) 
    myFile.close()
    myProgress.stop()
    myProgress.lower()

#Thread for getting live data
def threadingLive():
    # Call work function
    t1=Thread(target=liveData)
    t1.start()   

#getting the Live data
def liveData():
    # Handshake
    statusBar['text'] ="Getting live data.."
    root.update_idletasks()
    time.sleep(1)
    
    text_field.delete('1.0', END)
    data, addr = sock.recvfrom(2048)
    while data != b"Hello":
        data, addr = sock.recvfrom(2048)
        root.update_idletasks()
    
    sock.sendto("Read".encode(), addr)
    done = False
    while not done:
        data, addr = sock.recvfrom(2048)
        if data == b"Done" :
            done = True
        else:
            if data !=b"Hello":
                text_field.insert(END, data.decode(encoding="utf-8", errors="ignore").rstrip(".\\.x\\.?\\9\\.(.\\.).") )
                text_field.insert(END,"\n")
        root.update_idletasks()
           
    statusBar['text'] = "Done."     

#Thread for saving data
def threadingLoop():
    # Call work function
    t1=Thread(target=loop)
    t1.start()
 
#Getting the data
def loop():
    # Handshake
    statusBar['text'] ="Getting Saved Data.."
    root.update_idletasks()
    time.sleep(1)

    data, addr = sock.recvfrom(2048)
    while data != b"Hello":
        data, addr = sock.recvfrom(2048)
        root.update_idletasks()
    
    sock.sendto("Send".encode(), addr)
    
    while(data!=b'Done Sending'):
        data, addr = sock.recvfrom(2048)
        details = data.split()
        intro = details[0]
        
        if intro ==b'FILE:':
            filename = details[1].decode()
            fileSize = int(details[3].decode())
            file_extension = details[5].decode()
            saveData(filename, file_extension, fileSize)
        root.update_idletasks()
    statusBar['text'] = "Done."

#subMenu bar: about us section
def about_us():
    tkinter.messagebox.showinfo("Branch PAL", "Application to get get data from ESP32-Cam")

def my_txt(line):
        text =Label(root, text=line)
        text.pack()

#browsing directory
def browser():
    global filename 
    global text_field
    global extension
    filename = filedialog.askopenfilename(initialdir="./",title = "Select your File",filetypes = [("Image Files",["*.jpg", "*png", "*jpeg"]),("Text Documents","*.txt")])
    if filename:
        fname =  os.path.basename(filename)
        statusBar['text'] ="File Opened: "+ fname
        extension= filename[filename.index(".")+1:]

        if extension == "txt":
            txt_file = open(filename,"r")
            readInfo = txt_file.read()
            txt_file.close()
            text_field.delete('1.0', END)
            text_field.insert(END, readInfo)
        if extension == "jpg":
            myPhoto = PhotoImage(file=str(filename))
            text_field.delete('1.0', END)
            # text_field.image_create(END, image=myPhoto)
            text_field.window_create(END, window = Label(text_field, image = myPhoto))

def save_file():
        filename = filedialog.askopenfilename(initialdir="./",title = "Save File as",filetypes = [("Image Files",["*.jpg", "*png", "*jpeg"]),("Text Documents","*.txt")])
        my_File = open(filename, "w") 
        my_File.write(text_field.get(1.0, END))
        my_File.close()
        statusBar['text'] = "File Saved as: "+filename

# root = Tk()
root = tk.ThemedTk()
root.get_themes()
root.set_theme("breeze")
# root.geometry('400x400')
root.title("Branch PAL")
root.iconbitmap(r'comms/source/eee.ico')

## sub menu
#Menu
menubar = Menu(root)
root.config(menu=menubar) #fixed at top, menubar must be ready to receive sub menus
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browser)
subMenu.add_command(label="Save File", command=save_file)
subMenu.add_command(label="Exit", command=root.destroy)

subMenu2 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu2)
subMenu2.add_command(label="About Us", command=about_us)


text = ttk.Label(root, text="Welcome to Branch PAL") #widget, but Label can act as container
text.pack(pady=10) #add widget

#Adding image
photo = PhotoImage(file=r"comms\source\interaction.png")
photoLabel = ttk.Label(root, image=photo)
photoLabel.pack()
myProgress = ttk.Progressbar(root, orient=HORIZONTAL, )
text_field = Text(root, width=20, height=25)
text_field.pack(pady=10, fill=X, padx=10)

midFrame = Frame(root)
midFrame.pack(padx=10, pady=5)

#Adding button
btn = ttk.Button(midFrame , text="Get Saved Data",command=threadingLoop)
btn.grid(row=0, column=0, padx=10 )
btn = ttk.Button(midFrame , text="Read Now", command=threadingLive)
btn.grid(row=0, column=1, padx=10)
btn = ttk.Button(midFrame , text="Get ESP Stats")
btn.grid(row=0, column=2, padx=10)

#Bar Frame
progress_Frame = Frame(root)
progress_Frame.pack(fill=X, expand=True)

myProgress = ttk.Progressbar(progress_Frame, orient=HORIZONTAL, length=200, mode="determinate")
myProgress.grid(row=0, column=0, sticky='nsew')
blankCover = Frame(progress_Frame)
blankCover.grid(row=0, column=0, sticky='nsew')

statusBar = ttk.Label(root, text="Hello World!", relief="sunken",anchor=W, font="times 15 italic")
statusBar.pack(side=BOTTOM, fill=X)

#pack manager arranges items in vertical order of appearance
def on_closing():
    # tk.messagebox.showinfo("Message Box", "Hi there" )
    root.destroy()

#overriding
root.protocol('WM_DELETE_WINDOW', on_closing)

root.mainloop()
 


