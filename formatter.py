import os
from progress.bar import Bar
import re
import datetime
from werkzeug.utils import secure_filename
import time
try:
    from tkinter import filedialog
    from tkinter import *
except:
    pass

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

class Formatter:
    
    def __init__(self):
        pass
    
    def cleanName(self, name):
        name = name.strip()
        name_output = secure_filename(name)
        if not re.search('[a-zA-Z]', name_output):
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            time.sleep(1)
            name_output = "_".join([basename, suffix])
        name_output = name_output.lower()
        return name_output
    
    def clean(self, srcPath):
        
        bar = Bar('Processing', max=len(os.listdir(srcPath)))
        for arthur in os.listdir(srcPath):
            if len(os.listdir(os.path.join(srcPath, arthur))) == 0:
                os.rmdir(os.path.join(srcPath, arthur))
            else:
                new_arthur = self.cleanName(arthur)
                if arthur != new_arthur:
                    if not os.path.exists(os.path.join(srcPath, new_arthur)):
                        os.rename(os.path.join(srcPath, arthur), os.path.join(srcPath, new_arthur))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                        time.sleep(1)
                        new_arthur = "_".join([new_arthur, suffix])
                        os.rename(os.path.join(srcPath, arthur), os.path.join(srcPath, new_arthur))     
                self.cleanRecur(new_arthur, os.path.join(srcPath, new_arthur))
            bar.next()
        bar.finish()
    
    def cleanRecur(self, arthur, fullPath):
        for fileDir in os.listdir(fullPath):
            if os.path.isdir(os.path.join(fullPath, fileDir)):
                if len(os.listdir(os.path.join(fullPath, fileDir))) == 0:
                    os.rmdir(os.path.join(fullPath, fileDir))
                else:
                    self.cleanRecur(arthur, os.path.join(fullPath, fileDir))
            else:
                name, ext = os.path.splitext(fileDir)
                new_name = self.cleanName(name)
                
                if ext.endswith(zip_ext):
                    ext = ".cbz"
                
                new_fileDir = "[" + arthur + "] " + new_name + ext
                if fileDir != new_fileDir:
                    if not os.path.exists(os.path.join(fullPath, new_fileDir)):
                        os.rename(os.path.join(fullPath, fileDir), os.path.join(fullPath, new_fileDir))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                        time.sleep(1)
                        new_fileDir = "_".join([new_fileDir, suffix])
                        os.rename(os.path.join(fullPath, fileDir), os.path.join(fullPath, new_fileDir))
                               
if __name__ == '__main__':
    
    tk = Tk()
    srcPath = filedialog.askdirectory()
    print("Select source dir path: {}".format(srcPath))
    tk.destroy()
    
    formatter = Formatter()
    formatter.clean(srcPath)
    
        