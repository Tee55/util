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
    
    def cleanName(self, name):
        name = name.strip()
        name_output = secure_filename(name)
        if not re.search('[a-zA-Z]', name_output):
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            name_output = "_".join([basename, suffix])
        name_output = name_output.lower()
        return name_output
    
    def get_arthur_name_ext(self, fullPath):
        filename, ext = os.path.splitext(os.path.basename(fullPath))
        for i, char in enumerate(filename):
            if char == "[":
                start = i+1
            elif char == "]":
                end = i
            
            if start and end:
                arthur = filename[start:end]
                name = filename[end+1:]
                
                arthur_output = self.cleanName(arthur)
                name_output = self.cleanName(name)
                
                ext_output = ext.lower()
                
                return arthur_output, name_output, ext_output
        else:
            components = fullPath.split(os.sep)
            arthur = components[1]
            arthur_output = self.cleanName(arthur)
            
            name = filename
            name_output = self.cleanName(name)
            
            ext_output = ext.lower()
            return arthur_output, name_output, ext_output
        
    
    def clean(self, srcPath):
        
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                arthur, name, ext = self.get_arthur_name_ext(os.path.join(root, file))
                new_name = "[" + arthur + "] " + name
                    
                if file.endswith(zip_ext):
                    if not os.path.exists(os.path.join(root, new_name + ".cbz")):
                        os.rename(os.path.join(root, file), os.path.join(root, new_name + ".cbz"))
                else:
                    if not os.path.exists(os.path.join(root, new_name + ext)):
                        os.rename(os.path.join(root, file), os.path.join(root, new_name + ext))
                        
            for dir in dirs:
                new_dir = self.cleanName(dir)
                if len(os.listdir(os.path.join(root, dir))) == 0:
                    os.rmdir(os.path.join(root, dir))
                else:
                    if not os.path.exists(os.path.join(root, new_dir)):
                        os.rename(os.path.join(root, dir), os.path.join(root, new_dir))
                    
                    
    def main(self):
        
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        tk.destroy()
        
        self.clean(srcPath)
        
        filelist = []
        arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                if file.endswith(zip_ext):
                    arthur, name, ext = self.get_arthur_name_ext(os.path.join(root, file))
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
    
        