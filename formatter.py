import os
from progress.bar import Bar
import re
import datetime
from slugify import slugify
import time
from natsort import natsorted
import zipfile
import rarfile
import io
from PIL import Image
rarfile.UNRAR_TOOL = "UnRAR.exe"

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')
image_ext = ('.jpg', '.png', '.webp', '.jpeg')

class Formatter:

    def cleanName(self, name):
        
        # Remove head and tail whitespaces
        name = name.strip()
        
        name_output = slugify(name, separator=" ")
        if name_output == "":
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
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
                        new_arthur = "_".join([new_arthur, suffix])
                        os.rename(os.path.join(srcPath, arthur),
                                  os.path.join(srcPath, new_arthur))
                self.cleanRecur(new_arthur, os.path.join(srcPath, new_arthur))
            bar.next()
        bar.finish()
        
    def sep_arthur_name(self, name):
        arthur = name[name.find("[")+1:name.find("]")]
        arthur = arthur[arthur.find("(")+1:arthur.find(")")]
        item_name = name[name.find("]")+1:]
        if arthur != "" and item_name != "":
            arthur_output = self.cleanName(arthur)
            item_name = self.cleanName(item_name)
            return arthur_output, item_name
        else:
            name_output = self.cleanName(name)
            return None, name_output
        
    def cleanFile(self, filePath):
        if zipfile.is_zipfile(filePath):
            zipObj = zipfile.ZipFile(filePath, 'r')
        elif rarfile.is_rarfile(filePath):
            zipObj = rarfile.RarFile(filePath, 'r')
        else:
            print("File {} is either zip or rar file".format(filePath))
            return
        # Clean if there is dir or '.jpg', '.png', '.jpeg' in archieve or '.webp' is not in root
        notClean = False
        for fileDirPath in zipObj.namelist():
            if os.path.isdir(fileDirPath):
                notClean = True
                break
            else:
                filename = os.path.basename(fileDirPath)
                if filename.lower().endswith(('.jpg', '.png', '.jpeg')) or filename != fileDirPath:
                    notClean = True
                    break
                        
        if notClean:
            jpeglist = []
            for x in zipObj.namelist():
                if x.lower().endswith('/'):
                    pass
                elif x.lower().endswith(image_ext):
                    jpeglist.append(x)
            jpeglist = natsorted(jpeglist)
            zip_filename = os.path.basename(filePath)
            dirPath = os.path.dirname(filePath)
            new_zipObj = zipfile.ZipFile(os.path.join(dirPath, "temp.zip"), 'w')
            
            try:
                for i, jpeg_file in enumerate(jpeglist):
                    filename = os.path.basename(jpeg_file)
                    name, ext = os.path.splitext(filename)
                    image_pil = Image.open(zipObj.open(jpeg_file))
                    image_pil = image_pil.convert('RGB')
                    image_byte = io.BytesIO()
                    image_pil.save(image_byte, "webp", quality=100)
                    new_zipObj.writestr(name + ".webp", image_byte.getvalue())
                    print(" Image process: {}/{}".format(i, len(jpeglist)), end="\r")
                    
                zipObj.close()
                new_zipObj.close()
                
                if os.path.exists(filePath):
                    os.remove(filePath)
                if not os.path.exists(os.path.join(dirPath, zip_filename)):
                    os.rename(os.path.join(dirPath, "temp.zip"), os.path.join(dirPath, zip_filename))
                else:
                    print("File {} already exist".format(os.path.join(dirPath, zip_filename)))
                
            except Exception as e:
                print("{}: {}".format(filePath, e))

    def cleanRecur(self, arthur, arthur_path, isChapter=False):
        for fileDir in os.listdir(arthur_path):
            if os.path.isdir(os.path.join(arthur_path, fileDir)):
                name = fileDir
                ext = None
            else:
                name, ext = os.path.splitext(fileDir)
                if ext.endswith(zip_ext):
                    ext = ".cbz"
            _, new_name = self.sep_arthur_name(name)
            
            if isChapter:
                if fileDir.lower().endswith(image_ext):
                    new_name = "[" + arthur + "] " + "thumbnails"
                else:
                    dirName = os.path.basename(arthur_path)
                    if "chapter" in new_name:
                        num_list = re.findall(r'\d+', new_name[new_name.find("chapter")+1:]) 
                        if num_list != []:
                            new_name = " ".join([dirName, num_list[0]])
                        else:
                            # Can not find number in filename
                            chapFileList = [ele for ele in natsorted(os.listdir(arthur_path)) if not ele.lower().endswith(image_ext)]
                            new_name = " ".join([dirName, str(chapFileList.index(fileDir)+1)])
                    else:
                        chapFileList = [ele for ele in natsorted(os.listdir(arthur_path)) if not ele.lower().endswith(image_ext)]
                        new_name = " ".join([dirName, str(chapFileList.index(fileDir)+1)])
            else:
                remove_list = ["chapter", "english", "digital", "fakku", "comic", "comics", "decensored", "x3200"]
                for word in remove_list:
                    new_name = new_name.split(word, 1)[0]
                new_name = re.sub(r'\d{6}\s\d{6}', "", new_name)
                new_name = " ".join(new_name.split())
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
            else:
                formatter.cleanFile(os.path.join(arthur_path, new_fileDir))

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
