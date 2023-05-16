import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

def add_image():
    global myPhoto
    filename = filedialog.askopenfilename(initialdir="./",title = "Select your File",filetypes = [("Image Files",["*.jpg", "*png", "*jpeg"])])
    myPhoto = ImageTk.PhotoImage(Image.open(filename)) 
    text.image_create(tk.END, image = myPhoto) # Example 1
    # text.window_create(tk.END, window = tk.Label(text, image = img)) # Example 2

root = tk.Tk()
text = tk.Text(root)
text.pack(padx = 20, pady = 20)
bt = tk.Button(root, text = "Insert", command = add_image)
bt.pack()

root.mainloop()


