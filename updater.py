import os
from tkinter import filedialog
from tkinter import *
import shutil
from progress.bar import Bar
from formatter import Formatter

formatter = Formatter()
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

class Updater:
    
    def __init__(self):
        pass
    
    def sep_arthur_name(self, name):
        start = None
        end = None
        for i, char in enumerate(name):
            if char == "[":
                start = i+1
            elif char == "]":
                end = i
            
            if start and end:
                arthur = name[start:end]
                name = name[end+1:]
                
                arthur_output = formatter.cleanName(arthur)
                name_output = formatter.cleanName(name)
                
                return arthur_output, name_output
            
        name_output = formatter.cleanName(name)
        return None, name_output

    def run(self):
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        
        destPath = filedialog.askdirectory()
        print("Select dir path you want to update: {}".format(destPath))
        tk.destroy()
        
        formatter.clean(srcPath)
                    
        src_filelist = []
        src_arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                
                name, ext = os.path.splitext(file)
                arthur, new_name = self.sep_arthur_name(os.path.join(root, file))
                if arthur:
                    src_filelist.append(os.path.join(root, file))
                    src_arthurList.append(arthur)
                        
        dest_filelist = []
        for root, dirs, files in os.walk(destPath):
            for file in files:
                if file.endswith(zip_ext):
                    arthur, name, ext = formatterutil.get_arthur_name_ext(os.path.join(root, file))
                    if arthur:
                        dest_filelist.append(os.path.join(root, file))
        
        bar = Bar('Processing', max=len(src_filelist)) 
        for fullPath, arthur in zip(src_filelist, src_arthurList):
            if not os.path.exists(os.path.join(destPath, arthur)):
                os.makedirs(os.path.join(destPath, arthur))
            basename = os.path.basename(fullPath)
            if basename not in dest_filelist:
                movePath = os.path.join(destPath, arthur, basename)
                if not os.path.exists(movePath):
                    print("Move zipfile to: {}".format(movePath))
                    shutil.move(fullPath, movePath)
                bar.next()

if __name__ == '__main__':
    updater = Updater()
    updater.run()
    