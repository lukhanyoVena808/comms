
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image
import os 
import tkinter.messagebox
import socket
import time
import random
from threading import Thread

LOCAL_UDP_IP = "192.168.1.2"
SHARED_UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((LOCAL_UDP_IP, SHARED_UDP_PORT))


# // -------------------------------------------- // ------------------------------------------------------- // -------------------------------------------
#saving data to local directory
def saveData(fn, ext, fileSize):
    start_time = time.time()
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
    print("--- %s seconds --- file size:%d bytes" % ((time.time() - start_time), fileSize))
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
                live =  (data.decode(encoding="utf-8", errors="ignore").rstrip(".\\.x\\.?\\9\\.(.\\.)."))
                # num = float(live[live.rindex(":")+1:])
                # in_line = num + random.uniform(80, 82.5)
                # showing = "Weight:%f" % (in_line)
                text_field.insert(END, live)
                text_field.insert(END,"\n")
        root.update_idletasks()
    statusBar['text'] = "Done."  


#Thread for getting live data
def threadingStats():
    # Call work function
    t1=Thread(target=StatsData)
    t1.start()   

#getting the Live data
def StatsData():
    # Handshake
    statusBar['text'] ="Getting ESP32 Stats.."
    root.update_idletasks()
    time.sleep(1)
    text_field.delete('1.0', END)
    data, addr = sock.recvfrom(2048)
    while data != b"Hello":
        data, addr = sock.recvfrom(2048)
        root.update_idletasks()
    sock.sendto("Stats".encode(), addr)
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
    text_field.delete('1.0', END)
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
    filename = filedialog.askopenfilename(initialdir="./",  defaultextension=".txt",title = "Select your File",filetypes = [("Image Files",["*.jpg", "*png", "*jpeg"]),("Text Documents","*.txt")])
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
        if extension in ["jpg", "png", "jpeg"]:
            global myPhoto
            myPhoto = ImageTk.PhotoImage(Image.open(filename)) 
            text_field.delete('1.0', END)
            text_field.image_create(END, image=myPhoto)
            # text_field.window_create(END, window = Label(text_field, image = myPhoto))

def save_file():
        filename = filedialog.asksaveasfile(mode='w',initialdir="./", defaultextension=".txt",title = "Save File as",filetypes = [("Text Documents","*.txt")])
        fn = filename.name[filename.name.rindex("/")+1:]
        filename.write(text_field.get(1.0, END))
        filename.close()
        statusBar['text'] = "File Saved as: "+fn

def on_closing():
    mbox = tkinter.messagebox.askyesnocancel("Warning!","Do you want to exit now?")
    if mbox:
        root.destroy()
    else:
        pass

# // -------------------------------------------- // ------------------------------------------------------- // -------------------------------------------

# Setting up main window
root = tk.ThemedTk()
style = ttk.Style(root)
root.tk.call('source', 'comms/source/Azure-ttk-theme/azure3/azure.tcl')
style.theme_use('azure')
style.configure("Accentbutton", foreground='white')
style.configure("Togglebutton", foreground='white')
root.title("Branch PAL")
root.iconbitmap(r'comms/icons/eee.ico')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Setting up menu and subMenus
open_icon = PhotoImage(file="comms/icons/open.png")
save_as_icon = PhotoImage(file="comms/icons/save_as.png")
exit_icon = PhotoImage(file="comms/icons/exit.png")
ab = PhotoImage(file="comms/icons/find.png")
menubar = Menu(root, font="times 18 italic")
root.config(menu=menubar,) #fixed at top, menubar must be ready to receive sub menus
subMenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browser, image=open_icon, compound=LEFT)
subMenu.add_command(label="Save txt File as", command=save_file, image=save_as_icon, compound=LEFT)
subMenu.add_command(label="Exit", command=on_closing, image=exit_icon, compound=LEFT)
subMenu2 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu2)
subMenu2.add_command(label="About Us", command=about_us, compound=LEFT, image=ab)

# Setting up App Heading
text = ttk.Label(root, text="Welcome to Branch PAL", font="times 12") #widget, but Label can act as container
text.pack(pady=10) #add widget

#Adding image
photo = PhotoImage(file=r"comms\images\interaction.png")
photoLabel = ttk.Label(root, image=photo)
photoLabel.pack()

# Setting up Text Field for viewing and editting
TextFrame = ttk.Frame(root)
TextFrame.pack(padx=10, expand=True, fill=X, anchor=CENTER )
text_field = Text(TextFrame)
myScrollbar = Scrollbar(TextFrame, orient="vertical", command=text_field.yview)
myScrollbar.pack(side=RIGHT, fill=Y)
text_field.configure(yscrollcommand=myScrollbar.set)
text_field.pack(expand=True, fill=X)
TextFrame2 = ttk.Frame(root)
TextFrame2.pack(padx=50, fill=X)
myScrollbar2 = Scrollbar(TextFrame2, orient="horizontal", command=text_field.xview,)
text_field.configure(xscrollcommand=myScrollbar2.set)
myScrollbar2.pack(side=BOTTOM, fill=X)

# Setting up Buttons
midFrame = Frame(root)
midFrame.pack(padx=10, pady=10, expand=True)

#Adding button
btn = ttk.Button(midFrame , text="Get Saved Data",command=threadingLoop, style="Accentbutton")
btn.grid(row=0, column=0, padx=10 )
btn = ttk.Button(midFrame , text="Read Now", command=threadingLive, style="Accentbutton")
btn.grid(row=0, column=1, padx=10)
btn = ttk.Button(midFrame , text="Get ESP Stats", command=threadingStats, style="Accentbutton")
btn.grid(row=0, column=2, padx=10)

# Setting up Progress Bar
progress_Frame = Frame(root)
progress_Frame.pack( expand=True, padx=10, anchor=CENTER)
myProgress = ttk.Progressbar(progress_Frame, orient=HORIZONTAL, length=450, mode="determinate", )
myProgress.grid(row=0, column=1, sticky='nsew')
blankCover = Frame(progress_Frame)
blankCover.grid(row=0, column=1, sticky='nsew')

# Setting up StatusBar
statusBar = ttk.Label(root, text="Hello World!", relief="sunken",anchor=W, font="times 18 italic", )
statusBar.pack(side=BOTTOM, fill=X)

#overriding Exit protocol
root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
    


