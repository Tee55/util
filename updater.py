from formatter import formatterUtil
import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil
from progress.bar import Bar

formatterutil = formatterUtil()
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')

def main():
    tk = Tk()
    srcPath = filedialog.askdirectory()
    print("Select source dir path: {}".format(srcPath))
    
    destPath = filedialog.askdirectory()
    print("Select dir path you want to update: {}".format(destPath))
    tk.destroy()
    
    for root, dirs, files in os.walk(srcPath):
        for file in files:
            if file.endswith(zip_ext):
                new_file = formatterutil.cleanFileName(file)
                name, ext = os.path.splitext(new_file)
                os.rename(os.path.join(root, file), os.path.join(root, name + ".cbz"))
    
    '''
    src_filelist = []
    src_arthurList = []
    for root, dirs, files in os.walk(srcPath):
        for file in files:
            if file.endswith(zip_ext):
                arthur = formatterutil.get_arthur(file)
                if arthur:
                    src_filelist.append(os.path.join(root, file))
                    src_arthurList.append(arthur)
                    
    dest_filelist = []
    dest_arthurList = []
    for root, dirs, files in os.walk(destPath):
        for file in files:
            if file.endswith(zip_ext):
                arthur = formatterutil.get_arthur(file)
                if arthur:
                    dest_filelist.append(os.path.join(root, file))
                    dest_arthurList.append(arthur)
    
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
    '''
    
    

if __name__ == '__main__':
    main()
    