import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil

tk = Tk()

image_ext = ('.jpg', 'png')
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')


class formatUtil:
    def get_arthur(self, components):
        for component in components:
            if component in self.arthurList:
                return component

    def main(self):
        fullPath = filedialog.askdirectory()
        print("Select dir path: {}".format(fullPath))
        
        destPath = filedialog.askdirectory()
        print("Select destination path: {}".format(destPath))
        
        self.arthurList = []
        for arthur in os.listdir(fullPath):
            if not os.path.exists(os.path.join(destPath, arthur)):
                os.makedirs(os.path.join(destPath, arthur))
            self.arthurList.append(arthur)
        
        content_list = []
        
        for root, dirs, files in os.walk(fullPath):
            for file in files:
                if file.endswith(image_ext):
                    fullPath = os.path.join(root, file)
                    dirPath = os.path.split(fullPath)[0]
                    contentDir, content = os.path.split(dirPath)
                    
                    if content not in content_list:
                        components = contentDir.split(os.sep)
                        arthur = self.get_arthur(components)
                        
                        content_list.append(content)
                        zipPath = os.path.join(contentDir, content + ".cbz")
                        zipobj = zipfile.ZipFile(zipPath, "w")
                        print("Create zip file: {}".format(zipPath))
                        
                        for filename in os.listdir(dirPath):
                            if filename.endswith(image_ext):
                                zipobj.write(os.path.join(dirPath, filename), arcname=filename)
                                
                        movePath = os.path.join(destPath, arthur)
                        print("Move zipfile to: {}".format(movePath))
                        shutil.move(zipPath, movePath)
                elif file.endswith(zip_ext):
        
        tk.destroy()
    

if __name__ == '__main__':
    formatutil = formatUtil()
    formatUtil.main()
    