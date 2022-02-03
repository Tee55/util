import os
import re
import datetime
from slugify import slugify
import time
from natsort import natsorted
import zipfile
import rarfile
import tarfile
import io
from PIL import Image, ImageFile, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES=True
Image.MAX_IMAGE_PIXELS = None
from tqdm import tqdm
from moviepy.editor import *
import py7zr
import shutil
rarfile.UNRAR_TOOL = "UnRAR.exe"

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')
image_ext = ('.jpg', '.png', '.webp', '.jpeg')
video_ext = ('.mp4', '.avi', '.mkv')
image_size = (1024, 1024)

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

        for arthur in tqdm(os.listdir(srcPath), desc='Main Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
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
            try:
                zipObj = zipfile.ZipFile(filePath, 'r')
            except Exception as e:
                print("{}: {}".format(filePath, e))
                return
        elif rarfile.is_rarfile(filePath):
            try:
                zipObj = rarfile.RarFile(filePath, 'r')
            except Exception as e:
                print("{}: {}".format(filePath, e))
                return
        elif tarfile.is_tarfile(filePath):
            try:
                zipObj = tarfile.TarFile(filePath, 'r')
            except Exception as e:
                print("{}: {}".format(filePath, e))
                return
        elif py7zr.is_7zfile(filePath):
            try:
                zipObj = py7zr.SevenZipFile(filePath, 'r')
            except Exception as e:
                print("{}: {}".format(filePath, e))
                return
        elif filePath.lower().endswith(image_ext):
            image_pil = Image.open(filePath)
            image_pil = image_pil.convert('RGB')
            w, h = image_pil.size
            if filePath.lower().endswith(('.jpg', '.png', '.jpeg')):
                image_pil.thumbnail(image_size)
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                if not os.path.exists(os.path.join(dirPath, name + ".webp")):
                    image_pil.save(os.path.join(dirPath, name + ".webp"), "webp", quality=100)
                return
            elif w > 1024 and h > 1024 and h <= 3*w:
                image_pil.thumbnail(image_size)
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                if not os.path.exists(os.path.join(dirPath, name + ".webp")):
                    image_pil.save(os.path.join(dirPath, name + ".webp"), "webp", quality=100)
                return
            else:
                return
        elif filePath.lower().endswith(".gif"):
            image_pil = Image.open(filePath)   
            frames = ImageSequence.Iterator(image_pil)
            def thumbnails(frames):
                for frame in frames:
                    thumbnail = frame.copy()
                    thumbnail.thumbnail(image_size)
                    yield thumbnail
                    
            frames = thumbnails(frames)
            filename = os.path.basename(filePath)
            name, ext = os.path.splitext(filename)
            dirPath = os.path.dirname(filePath)
            if not os.path.exists(os.path.join(dirPath, name + ".gif")):
                image_pil.save(os.path.join(dirPath, name + ".gif"), save_all=True, append_images=list(frames))
            return
        elif filePath.lower().endswith(video_ext):
            if filePath.lower().endswith(('.avi', '.mkv')):
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                clip = VideoFileClip(filePath)
                if os.path.exists(filePath):
                    os.remove(filePath)
                if not os.path.exists(os.path.join(dirPath, name + ".mp4")):
                    clip.write_videofile(os.path.join(dirPath, name + ".mp4"))
                return
            else:
                return
        else:
            print("File format unknown: {}".format(filePath))
            return
        
        # Clean if there is dir or '.jpg', '.png', '.jpeg' in archieve
        # .webp' is not in root
        # '.webp' h and w > 1024
        zip_filename = os.path.basename(filePath)
        dirPath = os.path.dirname(filePath)
        new_zipObj = zipfile.ZipFile(os.path.join("temp/", "temp.zip"), 'w')
        isWrite = False
        image_index = 1
        write_index = 1
        for fileDirPath in tqdm(natsorted(zipObj.namelist()), leave=False, desc='Archieve Image Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            if os.path.isdir(fileDirPath):
                pass
            elif fileDirPath.lower().endswith(image_ext):
                filename = os.path.basename(fileDirPath)
                try:
                    image_pil = Image.open(zipObj.open(fileDirPath))
                    image_pil = image_pil.convert('RGB')
                    w, h = image_pil.size
                except Exception as e:
                    print("{}: {}".format(filePath, e))
                    zipObj.close()
                    new_zipObj.close()
                    if os.path.exists(os.path.join("temp/", "temp.zip")):
                        os.remove(os.path.join("temp/", "temp.zip"))
                    return

                # Check image size
                if w > 1024 and h > 1024:
                    if h <= 3*w:
                        image_pil.thumbnail(image_size)
                        isWrite = True
                        
                # Check image mime types
                if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    isWrite = True
                
                # Check if image file in root
                if filename != fileDirPath:
                    isWrite = True
                    
                # Check if image filename in ascending order
                name, ext = os.path.splitext(filename)
                if name != str(image_index):
                    isWrite = True
                    
                if isWrite:
                    if write_index==image_index:
                        image_byte = io.BytesIO()
                        image_pil.save(image_byte, "webp", quality=100)
                        new_zipObj.writestr(str(image_index) + ".webp", image_byte.getvalue())
                        write_index += 1
                    else:
                        zipObj.close()
                        new_zipObj.close()
                        if os.path.exists(os.path.join("temp/", "temp.zip")):
                            os.remove(os.path.join("temp/", "temp.zip"))
                        print("{}: Internal filename conflict, please check.".format(filePath))
                        return
                    
                image_index += 1
                    
        zipObj.close()
        new_zipObj.close()
        
        # Remove file -> Rename temp to file
        if isWrite:
            if os.path.exists(filePath):
                os.remove(filePath)
            if not os.path.exists(os.path.join(dirPath, zip_filename)):
                shutil.move(os.path.join("temp/", "temp.zip"), os.path.join(dirPath, zip_filename))
            else:
                print("File {} already exist".format(os.path.join(dirPath, zip_filename)))
                return
        else:
            if os.path.exists(os.path.join("temp/", "temp.zip")):
                os.remove(os.path.join("temp/", "temp.zip"))


    def cleanRecur(self, arthur, arthur_path, isChapter=False):
        
        if isChapter:
            desc = "Chapter Folder Progress"
        else:
            desc = "Author Folder Progress"
        
        
        # Only one image in Chapter Folder mean it is thumbnail
        count = 0
        isThumbnail = True
        for fileDir in os.listdir(arthur_path):
            if fileDir.lower().endswith(image_ext):
                count += 1
            if count >= 2:
                isThumbnail = False
                break
        
        for fileDir in tqdm(os.listdir(arthur_path), leave=False, desc=desc, bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            if os.path.isdir(os.path.join(arthur_path, fileDir)):
                name = fileDir
                ext = None
            else:
                name, ext = os.path.splitext(fileDir)
                if ext.endswith(zip_ext):
                    ext = ".cbz"
            _, new_name = self.sep_arthur_name(name)
            
            if isChapter:
                if fileDir.lower().endswith(image_ext) and isThumbnail:
                    new_name = "[" + arthur + "] " + "thumbnails"
                elif fileDir.lower().endswith(image_ext) and not isThumbnail:
                    chapFileList = [ele for ele in natsorted(os.listdir(arthur_path)) if ele.lower().endswith(image_ext)]
                    new_name = " ".join([dirName, str(chapFileList.index(fileDir)+1)])
                else:
                    dirName = os.path.basename(arthur_path)
                    noChapterNum = True
                    for word in ["chapter", "chapters"]:
                        num_list = re.findall(r'\d+', new_name[new_name.find(word)+1:])
                        if num_list != []:
                            new_name = " ".join([dirName, num_list[0]])
                            noChapterNum = False
                    if noChapterNum:
                        chapFileList = [ele for ele in natsorted(os.listdir(arthur_path)) if not ele.lower().endswith(image_ext)]
                        new_name = " ".join([dirName, str(chapFileList.index(fileDir)+1)])
            else:
                remove_list = ["chapter", "chapters", "english", "digital", "fakku", "comic", "comics", "decensored", "x3200", "uncensored"]
                for word in remove_list:
                    new_name = new_name.split(word, 1)[0]
                    
                if re.search(r'\d{6}\s\d{6}', new_name):
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
