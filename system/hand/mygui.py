import tkinter as tk
from tkinter import filedialog, colorchooser

def mygui_deco(func) :
    def wrap(*args, **kwargs):
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw() 
        result = func(*args,**kwargs)
        root.destroy()
        return result 
    return wrap

# filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("PPTX files","*.pptx"),("all files","*.*")))

@mygui_deco
def ask_openfilename() :
    filename = filedialog.askopenfilename(initialdir="D:/", title="Select file", filetypes=(("PPTX files","*.pptx"),("all files","*.*")))
    return filename 

@mygui_deco
def ask_savefilename() :
    filename = filedialog.asksaveasfilename() 
    return filename 

@mygui_deco
def ask_directory() :
    directory = filedialog.askdirectory() 
    return directory 

@mygui_deco
def ask_color() :
    color = colorchooser.askcolor() 
    return color[1]
