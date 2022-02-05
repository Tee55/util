import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil
from progress.bar import Bar
from module.formatter import Formatter

image_ext = ('.jpg', '.png', '.webp')
zip_ext = ('.zip', '.rar', '.cbz', '.cbr', '.cbx')
formatter = Formatter()

class Compressor:

    def __init__(self):
        pass
    
    def run(self):

        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        tk.destroy()

        filelist = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                filelist.append(os.path.join(root, file))

        bar = Bar('Processing', max=len(filelist))
        for fullPath in filelist:
            components = fullPath.split(os.sep)
            arthur = components[1]
            filename = os.path.basename(fullPath)
            dirPath = os.path.dirname(fullPath)
            name, ext = os.path.splitext(filename)
            
            if arthur == os.path.basename(srcPath):
                arthur, new_name = formatter.sep_arthur_name(name)
                if not arthur:
                    arthur = "unknown"
            
            # Create author folder
            if arthur not in os.listdir(srcPath):
                os.mkdir(os.path.join(srcPath, arthur))

            if ext.lower().endswith(image_ext):
                # Images
                dirPath = os.path.dirname(fullPath)
                zipPath = os.path.join(srcPath, arthur, name + ".cbz")
                zipobj = zipfile.ZipFile(zipPath, "w")

                for image_file in os.listdir(dirPath):
                    if image_file.lower().endswith(image_ext):
                        zipobj.write(os.path.join(
                            dirPath, image_file), arcname=image_file)
                        os.remove(os.path.join(dirPath, image_file))
                zipobj.close()

                if len(os.listdir(dirPath)) == 0:
                    os.rmdir(dirPath)
            elif ext.lower().endswith(zip_ext):
                # zip, rar, cbz, cbx, cbr
                movePath = os.path.join(srcPath, arthur, new_name + ".cbz")
                if not os.path.exists(movePath):
                    print("Move zipfile from {} to {}".format(fullPath, movePath))
                    shutil.move(fullPath, movePath)
                else:
                    print("File already exist (move from {} to {})".format(fullPath, movePath))
            else:
                print("{} filetype not support".format(fullPath))
            bar.next()
        
        # Remove empty dir
        for root, dirs, files in os.walk(srcPath):
            for dir in dirs:
                if len(os.listdir(os.path.join(root, dir))) == 0:
                    os.rmdir(os.path.join(root, dir))
