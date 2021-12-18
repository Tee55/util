import os
from tkinter import filedialog
from tkinter import *
import shutil
from progress.bar import Bar
import re
import datetime
from werkzeug.utils import secure_filename

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

class formatterUtil:
    
    def cleanFileName(self, filename):
        arthur_input, name_input = self.get_arthur(filename)
        arthur_output = secure_filename(arthur_input)
        name_output = secure_filename(name_input)
        
        if not re.search('[a-zA-Z]', arthur_output):
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            arthur_output = "_".join([basename, suffix])
        if not re.search('[a-zA-Z]', name_output):
            basename = "reader"
            suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            name_output = "_".join([basename, suffix])
        name_output = "[" + arthur_output + "] " + name_output
        return name_output
    
    def get_arthur(self, filename):
        start = None
        end = None
        for i, char in enumerate(filename):
            if char == "[":
                start = i+1
            elif char == "]":
                end = i
            
            if start and end:
                break
        
        arthur = filename[start:end]
        arthur = arthur.strip()
        
        name = filename[end+1:]
        name = name.strip()
        return arthur, name
        
    def main(self):
        
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        tk.destroy()
        
        filelist = []
        arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                if file.endswith(zip_ext):
                    arthur,_ = self.get_arthur(file)
                    if arthur:
                        filelist.append(os.path.join(root, file))
                        arthurList.append(arthur)
                    
            for dir in dirs:
                if len(os.listdir(os.path.join(root, dir))) == 0:
                    os.rmdir(os.path.join(root, dir))
                
        bar = Bar('Processing', max=len(filelist))
        for fullPath, arthur in zip(filelist, arthurList):
            if not os.path.exists(os.path.join(srcPath, arthur)):
                os.makedirs(os.path.join(srcPath, arthur))
            basename = os.path.basename(fullPath)
            movePath = os.path.join(srcPath, arthur, basename)
            if not os.path.exists(movePath):
                print("Move zipfile to: {}".format(movePath))
                shutil.move(fullPath, movePath)
            bar.next()
            
                
if __name__ == '__main__':
    formatterutil = formatterUtil()
    formatterutil.main()
    
        