import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil
from progress.bar import Bar

image_ext = ('.jpg', 'png')
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')


class formatUtil:

    def main(self):
        
        fullPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(fullPath))
        
        destPath = filedialog.askdirectory()
        print("Select destination dir path: {}".format(destPath))
    
        content_list = []
        
        bar = Bar('Processing', max=len(os.listdir(fullPath)))
        
        for arthur in os.listdir(fullPath):
            if not os.path.exists(os.path.join(destPath, arthur)):
                os.makedirs(os.path.join(destPath, arthur))
            for root, dirs, files in os.walk(os.path.join(fullPath, arthur)):
                for file in files:
                    if file.endswith(image_ext):
                        fullPath = os.path.join(root, file)
                        dirPath = os.path.split(fullPath)[0]
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
                            print("Move zipfile to: {}".format(movePath))
                            
                            if not os.path.exists(movePath):
                                shutil.move(zipPath, movePath)
                    elif file.endswith(zip_ext):
                        fullPath = os.path.join(root, file)
                        
                        print("Found zip file: {}".format(fullPath))
                        
                        dirPath = os.path.split(fullPath)[0]
                        arthurDir, content = os.path.split(dirPath)
                        
                        if content not in content_list:
                            content_list.append(content)
                            
                            name = os.path.split(file)[0]
                            srcPath = os.path.join(dirPath, name + ".cbz")
                            os.rename(fullPath, srcPath)
                            
                            movePath = os.path.join(destPath, arthur, name + ".cbz")
                            print("Move zipfile to: {}".format(movePath))
                            if not os.path.exists(movePath):
                                shutil.move(srcPath, movePath)
            bar.next()
                    
        
        
if __name__ == '__main__':
    tk = Tk()
    formatutil = formatUtil()
    formatutil.main()
    tk.destroy()
    