import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil
from progress.bar import Bar

image_ext = ('.jpg', 'png')
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')


class organizeUtil:

    def main(self):
        
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        
        destPath = filedialog.askdirectory()
        print("Select destination dir path: {}".format(destPath))
        tk.destroy()
      
        filelist = []
        arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                filelist.append(os.path.join(root,file))
                components = root.split(os.sep)
                arthurList.append(components[1])
        
        content_list = []
        bar = Bar('Processing', max=len(filelist))
        for fullPath, arthur in zip(filelist, arthurList):
            if not os.path.exists(os.path.join(destPath, arthur)):
                os.makedirs(os.path.join(destPath, arthur))
            if fullPath.endswith(image_ext):
                dirPath = os.path.dirname(fullPath)
                arthurDir, content = os.path.split(dirPath)
                
                if content not in content_list:
                    content_list.append(content)
                    
                    zipPath = os.path.join(arthurDir, content + ".cbz")
                    zipobj = zipfile.ZipFile(zipPath, "w")
                    print("Create zip file: {}".format(zipPath))
                    
                    for filename in os.listdir(dirPath):
                        if filename.endswith(image_ext):
                            zipobj.write(os.path.join(dirPath, filename), arcname=filename)
                    
                    zipobj.close()
                            
                    movePath = os.path.join(destPath, arthur, content + ".cbz")
                    if not os.path.exists(movePath):
                        print("Move zipfile to: {}".format(movePath))
                        shutil.move(zipPath, movePath)
            elif zipfile.is_zipfile(fullPath):
                print("Found zip file: {}".format(fullPath))
                
                dirPath = os.path.dirname(fullPath)
                arthurDir, content = os.path.split(dirPath)
                
                name = os.path.splitext(os.path.basename(fullPath))[0]
                
                if content not in content_list:
                    content_list.append(content)

                    srcPath = os.path.join(dirPath, name + ".cbz")
                    os.rename(fullPath, srcPath)
                    
                    movePath = os.path.join(destPath, arthur, name + ".cbz")
                    if not os.path.exists(movePath):
                        print("Move zipfile to: {}".format(movePath))
                        shutil.move(srcPath, movePath)
            bar.next()
                    
        
        
if __name__ == '__main__':
    formatutil = organizeUtil()
    formatutil.main()
    