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
import math
import ffmpeg
import filetype

from PIL import Image, ImageFile, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES=True
Image.MAX_IMAGE_PIXELS = None

from tqdm import tqdm
import shutil
rarfile.UNRAR_TOOL = "UnRAR.exe"

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')
image_ext = ('.jpg', '.png', '.webp', '.jpeg')
video_ext = ('.mp4', '.avi', '.mkv')
image_size = (1024, 1024)
temp_dirPath = "./temp/"

class Formatter:

    def cleanName(self, name, isAuthor=False):
        
        # Remove head and tail whitespaces
        name = name.strip()
        
        # Slugify
        name_output = slugify(name, separator=" ")
        
        # Append datetime if string after slugnify is empty
        if name_output == "":
            basename = "unknown"
            suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
            time.sleep(1)
            name_output = " ".join([basename, suffix])
            
        # Change to all lowercase 
        name_output = name_output.lower()
        
        if isAuthor:
            # Hitomi.la website's author sometime end with etc
            if name_output.endswith("etc"):
                name_output = name_output.replace("etc", "")
        
        # Remove common end words in doujin
        remove_list = ["chapter", "chapters", "english", "digital", "fakku", "comic", "comics", "decensored", "x3200"]
        for word in remove_list:
            name_output = name_output.replace(word, "")
            
        # Remove datetime if there is datetime in string (Also update datetime)
        if re.search(r'\d{6}\s\d{6}$', name_output):
            name_output = re.sub(r'\d{6}\s\d{6}$', "", name_output)
        
        # Combine multiple whitespaces to one
        name_output = " ".join(name_output.split())
        
        return name_output

    def clean(self, srcPath):

        for arthur in tqdm(os.listdir(srcPath), desc='Content Folder Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            if len(os.listdir(os.path.join(srcPath, arthur))) == 0:
                
                # Remove empty folder
                if os.path.exists(os.path.join(srcPath, arthur)):
                    os.rmdir(os.path.join(srcPath, arthur))
            else:
                # Get cleaned author name
                new_arthur = self.cleanName(arthur, isAuthor=True)

                # Renaming arthur name
                if arthur != new_arthur:
                    
                    if not os.path.exists(os.path.join(srcPath, new_arthur)):
                        os.rename(os.path.join(srcPath, arthur),
                                  os.path.join(srcPath, new_arthur))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                        time.sleep(1)
                        new_arthur = " ".join([new_arthur, suffix])
                        if not os.path.exists(os.path.join(srcPath, new_arthur)):
                            os.rename(os.path.join(srcPath, arthur),
                                    os.path.join(srcPath, new_arthur))
                        else:
                            print("{}: Problem with renaming file, please check.".format(os.path.join(srcPath, arthur)))
                            pass
                        
                # Renaming arthur items
                self.cleanRecur(new_arthur, os.path.join(srcPath, new_arthur))
        
    def sep_arthur_name(self, name):
        
        # Get text inside []
        arthur = name[name.find("[")+1:name.find("]")]
        
        # Get text inside ()
        arthur = arthur[arthur.find("(")+1:arthur.find(")")]
        
        # Text after ] is item name
        item_name = name[name.find("]")+1:]
        if arthur != "" and item_name != "":
            # Get cleaned author name
            arthur_output = self.cleanName(arthur, isAuthor=True)
            
            # Get cleaned item name
            item_name = self.cleanName(item_name)
            return arthur_output, item_name
        else:
            # Get cleaned item name
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
        elif filePath.lower().endswith(image_ext):
            image_pil = Image.open(filePath)
            image_pil = image_pil.convert('RGB')
            w, h = image_pil.size
            if filePath.lower().endswith(('.jpg', '.png', '.jpeg')):
                image_pil.thumbnail(image_size)
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                
                # Check if .webp exist or not
                if not os.path.exists(os.path.join(dirPath, name + ".webp")):
                    image_pil.save(os.path.join(dirPath, name + ".webp"), "webp", quality=100)
                else:
                    print("{}: There is already .webp file, please check.".format(filePath))
                    return
                    
                # Remove old file
                if os.path.exists(filePath):
                    os.remove(filePath)
                return
            elif filePath.lower().endswith('.webp') and w > 1024 and h > 1024:
                image_pil.thumbnail(image_size)
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                
                # Override old .webp
                image_pil.save(os.path.join(dirPath, name + ".webp"), "webp", quality=100)
                return
            else:
                # Perfect
                return
        elif filePath.lower().endswith(".gif"):
            image_pil = Image.open(filePath)
            frames = ImageSequence.Iterator(image_pil)
            
            # Check size only first frame (Save time)
            w, h = frames[0].size
    
            if w > 1024 and h > 1024:
                def thumbnails(frames):
                    for frame in frames:
                        thumbnail = frame.copy()
                        thumbnail.thumbnail(image_size)
                        yield thumbnail
                        
                frames = thumbnails(frames)
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                
                # Override old .gif
                image_pil.save(os.path.join(dirPath, name + ".gif"), save_all=True, append_images=list(frames))
                return
            else:
                # Perfect
                return
        elif filePath.lower().endswith(video_ext):
            if filePath.lower().endswith(('.avi', '.mkv')):
                filename = os.path.basename(filePath)
                name, ext = os.path.splitext(filename)
                dirPath = os.path.dirname(filePath)
                stream = ffmpeg.input(filePath)
                stream = ffmpeg.output(stream, os.path.join(dirPath, name + ".mp4"))
                ffmpeg.run(stream)
                
                # Remove old file
                if os.path.exists(filePath):
                    os.remove(filePath)
                return
            elif filePath.lower().endswith('.mp4'):
                # Perfect
                return
        else:
            kind = filetype.guess(filePath)
            if kind is None:
                print("{}: File format unknown.".format(filePath))
                return
            else:
                print("{}: We do not support {}.".format(filePath, kind.mime))
        
        zip_filename = os.path.basename(filePath)
        dirPath = os.path.dirname(filePath)
        new_zipObj = zipfile.ZipFile(os.path.join(temp_dirPath, "temp.zip"), 'w')
        isWrite = False
        isManhwa = False
        
        combined_image_height = 0
        imageList = []
        
        for fileDirPath in natsorted(zipObj.namelist()):
            if os.path.isdir(fileDirPath):
                pass
            elif fileDirPath.lower().endswith(image_ext):
                
                # Check first image if it need to write (Save time)
                try:
                    image_pil = Image.open(zipObj.open(fileDirPath))
                    image_pil = image_pil.convert('RGB')
                    imageList.append(image_pil)
                    w, h = image_pil.size
                except Exception as e:
                    print("{}: {}".format(filePath, e))
                    zipObj.close()
                    new_zipObj.close()
                    if os.path.exists(os.path.join(temp_dirPath, "temp.zip")):
                        os.remove(os.path.join(temp_dirPath, "temp.zip"))
                    return
            
                filename = os.path.basename(fileDirPath)
                name, ext = os.path.splitext(filename)
                
                # Check all conditions
                if w > 1024 and h > 1024 and h < 3*w:
                    isWrite = True
                elif h > 1024 and h >= 3*w:
                    combined_image_width = w
                    combined_image_height += h
                    isWrite = True
                    isManhwa = True   
                elif filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    isWrite = True
                elif filename != fileDirPath:
                    isWrite = True
                elif name != "1":
                    isWrite = True
                    
                if not isWrite:
                    break
                
        if isWrite and len(imageList) != 0:
            if not isManhwa:
                for index, image_pil in enumerate(tqdm(imageList, leave=False, desc='Archieve Images Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}')):
                    image_pil.thumbnail(image_size)
                    image_byte = io.BytesIO()
                    image_pil.save(image_byte, "webp", quality=100)
                    new_zipObj.writestr(str(index+1) + ".webp", image_byte.getvalue())
            else:
                combined_image = Image.new('RGB', (combined_image_width, combined_image_height))
                y_offset = 0
                for image_pil in imageList:
                    w, h = image_pil.size
                    
                    # Ensure that it is all images have same width
                    if w == combined_image_width:
                        combined_image.paste(image_pil, (0, y_offset))
                        y_offset += h
                    else:
                        image_pil = image_pil.resize((combined_image_width, int(h * (combined_image_width/w))))
                        w, h = image_pil.size
                        combined_image.paste(image_pil, (0, y_offset))
                        y_offset += h
                        
                # Crop each section to specific height
                slices = int(math.ceil(combined_image_height/image_size[1]))
                count = 1
                y = 0
                crop_images = []
                for _ in range(slices):
                    #if we are at the end, set the lower bound to be the bottom of the image
                    if count == slices:
                        lower = combined_image_height
                    else:
                        lower = int(count * image_size[1])

                    bbox = (0, y, combined_image_width, lower)
                    crop_image = combined_image.crop(bbox)
                    crop_images.append(crop_image)
                    y += image_size[1]
                    count +=1
                
                for index, crop_image in enumerate(tqdm(crop_images, leave=False, desc='Archieve Images Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}')):
                    image_byte = io.BytesIO()
                    crop_image.save(image_byte, "webp", quality=100)
                    new_zipObj.writestr(str(index+1) + ".webp", image_byte.getvalue())
        elif isWrite and len(imageList) == 0:
            print("{}: Can not find image file in archieve.".format(filePath))
            return
            
        zipObj.close()
        new_zipObj.close()
        
        # Remove file -> Rename temp to file
        if isWrite:
            if os.path.exists(filePath):
                
                # Remove old file
                os.remove(filePath)
                
                # Check if file exist
                if not os.path.exists(os.path.join(dirPath, zip_filename)):
                    # Move file from temp folder
                    shutil.move(os.path.join(temp_dirPath, "temp.zip"), os.path.join(dirPath, zip_filename))
                else:
                    print("{}: File already exist".format(os.path.join(dirPath, zip_filename)))
                    return
        else:
            # Remove temp file
            if os.path.exists(os.path.join(temp_dirPath, "temp.zip")):
                os.remove(os.path.join(temp_dirPath, "temp.zip"))


    def cleanRecur(self, arthur, arthur_path, isChapter=False):
        
        if isChapter:
            # Progress description
            desc = "Chapter Folder Progress"
            
            # Only one image in Chapter Folder mean it is thumbnail
            imageList = [chapFile for chapFile in os.listdir(arthur_path) if chapFile.lower().endswith(image_ext)]
            if len(os.listdir(arthur_path)) >= 1 and len(imageList) == 1:
                isThumbnail = True
            else:
                isThumbnail = False
        else:
            # Progress description
            desc = "Author Folder Progress"
        
        for fileDir in tqdm(os.listdir(arthur_path), leave=False, desc=desc, bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            if os.path.isdir(os.path.join(arthur_path, fileDir)):
                name = fileDir 
            else:
                name = os.path.splitext(fileDir)[0]
                
            # Sep filename and arthur from format '[author|artist] filename.ext'
            _, new_name = self.sep_arthur_name(name)
            if isChapter:
                if fileDir.lower().endswith(image_ext) and isThumbnail:
                    
                    # Thumbnail in chapter folder
                    new_name = "[" + arthur + "] " + "thumbnail"
                elif not re.search(r'\d+[a-z]?$', new_name):
                    print("{}: Can not find chapter indicate pattern, please check.".format(os.path.join(arthur_path, fileDir)))
                    pass
                
            # add arthur name to the front
            new_name = "[" + arthur + "] " + new_name
                
            if name != new_name:
                if os.path.isfile(os.path.join(arthur_path, fileDir)):
                    name, ext = os.path.splitext(fileDir)
                    new_fileDir = new_name + ext
                else:
                    new_fileDir = new_name
                
                # Rename fileDir
                if not os.path.exists(os.path.join(arthur_path, new_fileDir)):
                    os.rename(os.path.join(arthur_path, fileDir),
                                    os.path.join(arthur_path, new_fileDir))
                else:
                    suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                    time.sleep(1)
                    new_name = " ".join([new_name, suffix])
                    if os.path.isfile(os.path.join(arthur_path, fileDir)):
                        name, ext = os.path.splitext(fileDir)
                        new_fileDir = new_name + ext
                    else:
                        new_fileDir = new_name
                    if not os.path.exists(os.path.join(arthur_path, new_fileDir)):
                        os.rename(os.path.join(arthur_path, fileDir),
                                os.path.join(arthur_path, new_fileDir))
                    else:
                        print("{}: Problem with renaming file, please check.".format(os.path.join(arthur_path, fileDir)))
                        pass
            else:
                new_fileDir = fileDir
                        
            if os.path.isdir(os.path.join(arthur_path, new_fileDir)):
                if len(os.listdir(os.path.join(arthur_path, new_fileDir))) == 0:
                    # Remove empty folder
                    os.rmdir(os.path.join(arthur_path, new_fileDir))
                else:
                    self.cleanRecur(arthur, os.path.join(arthur_path, new_fileDir), isChapter=True)
            else:
                self.cleanFile(os.path.join(arthur_path, new_fileDir))