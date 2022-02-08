import tkinter as tk
from tkinter import OptionMenu, StringVar
from tkinter import ttk
from tkinter import filedialog
    
class CompressorPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Compressor")
        label.pack()
        button = ttk.Button(self, text="Select source directory", command=self.opendir)
        button.pack()
    
    def opendir(self):
        sourcePath = filedialog.askdirectory()
        sourcePath_label = tk.Label(self, text=sourcePath)
        sourcePath_label.pack()
        
class FormatterPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Formatter")
        label.pack()
        button = ttk.Button(self, text="Select source directory", command=self.opendir)
        button.pack()
        
    def opendir(self):
        sourcePath = filedialog.askdirectory()
        sourcePath_label = tk.Label(self, text=sourcePath)
        sourcePath_label.pack()
        
class UpdaterPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Formatter")
        label.pack()
        
class MainPage(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        options = ["compressor", "formatter", "updater"]
        self.variable = StringVar(self)
        self.variable.set(options[0])
        self.variable.trace("w", self.callback)

        w = OptionMenu(self, self.variable, *options)
        w.pack()
        
    def callback(self, *args):
        select_module = self.variable.get()
        if select_module == "compressor":
            compressorPage = CompressorPage()
            compressorPage.pack()
        elif select_module == "formatter":
            formatterPage = FormatterPage()
            formatterPage.pack()
        else:
            updaterPage = UpdaterPage()
            updaterPage.pack()
            
root = MainPage()
root.title("Utility Selection Page")
root.mainloop()