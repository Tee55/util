import os
from progress.bar import Bar
import re
import datetime
from slugify import slugify
import time

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

class Formatter:

    def cleanName(self, name):
        
        # Remove head and tail whitespaces
        name = name.strip()
        
        name_output = slugify(name, separator=" ")
        if name_output == "":
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
            time.sleep(1)
            name_output = " ".join([basename, suffix])
        name_output = name_output.lower()
        
        # Combine multiple whitespaces to one
        name_output = " ".join(name_output.split())
        return name_output

    def clean(self, srcPath):

        bar = Bar('Processing', max=len(os.listdir(srcPath)))
        for arthur in os.listdir(srcPath):
            if len(os.listdir(os.path.join(srcPath, arthur))) == 0:
                os.rmdir(os.path.join(srcPath, arthur))
            else:
                new_arthur = self.cleanName(arthur)
       
                if arthur != new_arthur:
                    if new_arthur not in os.listdir(srcPath):
                        os.rename(os.path.join(srcPath, arthur),
                                  os.path.join(srcPath, new_arthur))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                        time.sleep(1)
                        new_arthur = "_".join([new_arthur, suffix])
                        os.rename(os.path.join(srcPath, arthur),
                                  os.path.join(srcPath, new_arthur))
                self.cleanRecur(new_arthur, os.path.join(srcPath, new_arthur))
            bar.next()
        bar.finish()
        
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

                arthur_output = self.cleanName(arthur)
                name_output = self.cleanName(name)

                return arthur_output, name_output

        name_output = self.cleanName(name)
        return None, name_output

    def cleanRecur(self, arthur, arthur_path, isChapter=False):
        for fileDir in os.listdir(arthur_path):
            if os.path.isdir(os.path.join(arthur_path, fileDir)):
                name = fileDir
                ext = None
            else:
                name, ext = os.path.splitext(fileDir)
                if ext.endswith(zip_ext):
                    ext = ".cbz"
            fileDir_arthur, new_name = self.sep_arthur_name(name)
            
            if isChapter:
                num_list = re.findall(r'\d+', new_name)
                if num_list != []:
                    chap_num = num_list[0]
            
            remove_list = ["chapter", "english", "digital"]
            for word in remove_list:
                new_name = new_name.split(word, 1)[0]
            new_name = re.sub(r'\d{6}\s\d{6}', "", new_name)
            new_name = " ".join(new_name.split())
            
            if isChapter:
                new_name = " ".join([new_name, chap_num])
                
            new_name = "[" + arthur + "] " + new_name
            if name != new_name:
                if ext:
                    new_fileDir = new_name + ext
                else:
                    new_fileDir = new_name
                if os.path.exists(os.path.join(arthur_path, new_fileDir)):
                    suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                    time.sleep(1)
                    new_name = " ".join([new_name, suffix])
                    if ext:
                        new_fileDir = new_name + ext
                    else:
                        new_fileDir = new_name
                
                os.rename(os.path.join(arthur_path, fileDir),
                                os.path.join(arthur_path, new_fileDir))
            else:
                new_fileDir = fileDir
                        
            if os.path.isdir(os.path.join(arthur_path, new_fileDir)):
                if len(os.listdir(os.path.join(arthur_path, new_fileDir))) == 0:
                    os.rmdir(os.path.join(arthur_path, new_fileDir))
                else:
                    self.cleanRecur(arthur, os.path.join(arthur_path, new_fileDir), isChapter=True)

if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    root.call('tk', 'scaling', 4.0)
    srcPath = filedialog.askdirectory()
    print("Select source dir path: {}".format(srcPath))
    root.destroy()

    formatter = Formatter()
    formatter.clean(srcPath)
