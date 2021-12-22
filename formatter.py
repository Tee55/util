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

                arthur_output = formatter.cleanName(arthur)
                name_output = formatter.cleanName(name)

                return arthur_output, name_output

        name_output = formatter.cleanName(name)
        return None, name_output

    def cleanRecur(self, arthur, fullPath):
        for fileDir in os.listdir(fullPath):
            if os.path.isdir(os.path.join(fullPath, fileDir)):
                if len(os.listdir(os.path.join(fullPath, fileDir))) == 0:
                    os.rmdir(os.path.join(fullPath, fileDir))
                else:
                    self.cleanRecur(arthur, os.path.join(fullPath, fileDir))
            else:
                name, ext = os.path.splitext(fileDir)
                file_arthur, new_name = self.sep_arthur_name(name)

                if ext.endswith(zip_ext):
                    ext = ".cbz"
                
                new_name = "[" + arthur + "] " + new_name
                    
                if name != new_name:
                    new_fileDir = new_name + ext
                    if not os.path.exists(os.path.join(fullPath, new_fileDir)):
                        os.rename(os.path.join(fullPath, fileDir),
                                  os.path.join(fullPath, new_fileDir))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                        time.sleep(1)
                        new_name = "_".join([new_name, suffix])
                        new_fileDir = new_name + ext
                        os.rename(os.path.join(fullPath, fileDir),
                                  os.path.join(fullPath, new_fileDir))


if __name__ == '__main__':

    tk = Tk()
    srcPath = filedialog.askdirectory()
    print("Select source dir path: {}".format(srcPath))
    tk.destroy()

    formatter = Formatter()
    formatter.clean(srcPath)
