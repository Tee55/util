import os
from tkinter import filedialog
from tkinter import *
import shutil
from progress.bar import Bar

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

class formatterUtil:
    
    def get_arthur(self, filename):
        title = os.path.splitext(filename)[0]
        
        start = 0
        end = 0
        for i, char in enumerate(title):
            if char == "[":
                start = i+1
            elif char == "]":
                end = i
        
        arthur = title[start:end]
        return arthur
        
    def main(self):
        
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        tk.destroy()
        
        filelist = []
        arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                arthur = self.get_arthur(file)
                if arthur:
                    filelist.append(os.path.join(root, file))
                    arthurList.append(arthur)
                
        bar = Bar('Processing', max=len(filelist))
        for fullPath, arthur in zip(filelist, arthurList):
            if not os.path.exists(os.path.join(srcPath, arthur)):
                os.makedirs(os.path.join(srcPath, arthur))
            if fullPath.endswith(zip_ext):
                basename = os.path.basename(fullPath)
                movePath = os.path.join(srcPath, arthur, basename)
                if not os.path.exists(movePath):
                    print("Move zipfile to: {}".format(movePath))
                    shutil.move(fullPath, movePath)
            bar.next()
            
                
if __name__ == '__main__':
    formatterutil = formatterUtil()
    formatterutil.main()
    
        