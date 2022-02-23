from module.general import image_ext, subtitle_ext, video_ext, image_size, temp_dirPath, TqdmLoggingHandler
import shutil
from tqdm import tqdm
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
import filetype
import logging
import enzyme
import ffpb

from PIL import Image, ImageFile, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

rarfile.UNRAR_TOOL = "UnRAR.exe"


class Formatter:

    def __init__(self):
        logging.basicConfig(filename=os.path.join(
            temp_dirPath, "error.log"), filemode="w")
        self.logger = logging.getLogger()
        self.logger.addHandler(TqdmLoggingHandler())

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
        remove_list = ["chapter", "chapters", "english", "digital",
                       "fakku", "comic", "comics", "decensored", "x3200"]
        for word in remove_list:
            name_output = name_output.replace(word, "")

        # Remove datetime if there is datetime in string (Also update datetime)
        if re.search(r'\d{6}\s\d{6}$', name_output):
            name_output = re.sub(r'\d{6}\s\d{6}$', "", name_output)

        # Combine multiple whitespaces to one
        name_output = " ".join(name_output.split())

        return name_output
    
    def renameRecur(self, dir_path, old_name, new_name):
        # Rename if not exist
        if new_name not in os.listdir(dir_path):
            os.rename(os.path.join(dir_path, old_name),
                        os.path.join(dir_path, new_name))
            return new_name
        else:
            suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
            time.sleep(1)
            self.renameRecur(dir_path, new_name, " ".join([new_name, suffix]))
                
    def clean(self, contentPath):

        for old_author in tqdm(os.listdir(contentPath), desc='Content Folder Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            
            # Check if it is dir (author folder)
            if os.path.isdir(os.path.join(contentPath, old_author)):
                if len(os.listdir(os.path.join(contentPath, old_author))) == 0:

                    # Remove empty folder
                    if os.path.exists(os.path.join(contentPath, old_author)):
                        os.rmdir(os.path.join(contentPath, old_author))
                else:
                    # Get cleaned author name
                    new_author = self.cleanName(old_author, isAuthor=True)
                    
                    # Rename
                    if new_author != old_author:
                        new_author = self.renameRecur(contentPath, old_author, new_author)

                    # Clean item inside author folder
                    self.cleanRecur(new_author, os.path.join(
                        contentPath, new_author))
            else:
                logging.error("{}: This is not AUTHOR_FOLDER.".format(
                    os.path.join(contentPath, old_author)))
                continue

    def sep_author_name(self, name):

        # Get text inside []
        author = name[name.find("[")+1:name.find("]")]

        # Get text inside ()
        author = author[author.find("(")+1:author.find(")")]

        # Text after ] is item name
        item_name = name[name.find("]")+1:]
        if author != "" and item_name != "":
            # Get cleaned author name
            author_output = self.cleanName(author, isAuthor=True)

            # Get cleaned item name
            item_name = self.cleanName(item_name)
            return author_output, item_name
        else:
            # Get cleaned item name
            name_output = self.cleanName(name)
            return None, name_output
        
    def cleanArchiveFile(self, zipObj, filePath):
        
        # General info
        filename = os.path.basename(filePath)
        dirPath = os.path.dirname(filePath)
        
        # Create temp.zip
        new_zipObj = zipfile.ZipFile(
            os.path.join(temp_dirPath, "temp.zip"), 'w')
        isWrite = False
        isManhwa = False

        combined_image_height = 0
        imageList = []

        for fileDirPath in natsorted(zipObj.namelist()):
            if os.path.isdir(fileDirPath):
                continue
            elif fileDirPath.lower().endswith(image_ext):

                # Check first image if it need to write (Save time)
                try:
                    image_pil = Image.open(zipObj.open(fileDirPath))
                    image_pil = image_pil.convert('RGB')
                    imageList.append(image_pil)
                    w, h = image_pil.size
                except Exception as e:
                    logging.error("{}: {}".format(filePath, e))
                    zipObj.close()
                    new_zipObj.close()
                    if os.path.exists(os.path.join(temp_dirPath, "temp.zip")):
                        os.remove(os.path.join(temp_dirPath, "temp.zip"))
                    return

                zipItem_filename = os.path.basename(fileDirPath)
                zipItem_name, ext = os.path.splitext(filename)

                # Check all conditions
                if w > 1024 and h > 1024 and h < 3*w:
                    isWrite = True
                elif h > 1024 and h >= 3*w:
                    combined_image_width = w
                    combined_image_height += h
                    isWrite = True
                    isManhwa = True
                elif zipItem_filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    isWrite = True
                elif zipItem_filename != fileDirPath:
                    isWrite = True
                elif zipItem_name != "1":
                    isWrite = True

                if not isWrite:
                    break

        if isWrite and len(imageList) != 0:
            if not isManhwa:
                for index, image_pil in enumerate(tqdm(imageList, leave=False, desc='Archieve Images Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}')):
                    image_pil.thumbnail(image_size)
                    image_byte = io.BytesIO()
                    image_pil.save(image_byte, "webp", quality=100)
                    new_zipObj.writestr(
                        str(index+1) + ".webp", image_byte.getvalue())
            else:
                combined_image = Image.new(
                    'RGB', (combined_image_width, combined_image_height))
                y_offset = 0
                for image_pil in imageList:
                    w, h = image_pil.size

                    # Ensure that it is all images have same width
                    if w == combined_image_width:
                        combined_image.paste(image_pil, (0, y_offset))
                        y_offset += h
                    else:
                        image_pil = image_pil.resize(
                            (combined_image_width, int(h * (combined_image_width/w))))
                        w, h = image_pil.size
                        combined_image.paste(image_pil, (0, y_offset))
                        y_offset += h

                # Crop each section to specific height
                slices = int(math.ceil(combined_image_height/image_size[1]))
                count = 1
                y = 0
                crop_images = []
                for _ in range(slices):
                    # if we are at the end, set the lower bound to be the bottom of the image
                    if count == slices:
                        lower = combined_image_height
                    else:
                        lower = int(count * image_size[1])

                    bbox = (0, y, combined_image_width, lower)
                    crop_image = combined_image.crop(bbox)
                    crop_images.append(crop_image)
                    y += image_size[1]
                    count += 1

                for index, crop_image in enumerate(tqdm(crop_images, leave=False, desc='Archieve Images Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}')):
                    image_byte = io.BytesIO()
                    crop_image.save(image_byte, "webp", quality=100)
                    new_zipObj.writestr(
                        str(index+1) + ".webp", image_byte.getvalue())
        elif isWrite and len(imageList) == 0:
            logging.error(
                "{}: Can not find image file in archieve.".format(filePath))
            return

        zipObj.close()
        new_zipObj.close()

        # Remove file -> Rename temp to file
        if isWrite:
            if os.path.exists(filePath):
                # Remove old file
                os.remove(filePath)
            else:
                logging.error("{}: File not exist".format(filePath))
                return

            # Check if file exist
            if filename not in os.listdir(dirPath):
                # Move file from temp folder
                shutil.move(os.path.join(temp_dirPath, "temp.zip"),
                            os.path.join(dirPath, filename))
                return
            else:
                logging.error("{}: File already exist".format(
                    os.path.join(dirPath, filename)))
                return
        else:
            # Remove temp file
            if os.path.exists(os.path.join(temp_dirPath, "temp.zip")):
                os.remove(os.path.join(temp_dirPath, "temp.zip"))
            return

    def cleanFile(self, filePath):

        filename = os.path.basename(filePath)
        name, ext = os.path.splitext(filename)
        dirPath = os.path.dirname(filePath)

        if zipfile.is_zipfile(filePath):
            try:
                zipObj = zipfile.ZipFile(filePath, 'r')
                self.cleanArchiveFile(zipObj, filePath)
            except Exception as e:
                logging.error("{}: {}".format(filePath, e))
                return
        elif rarfile.is_rarfile(filePath):
            try:
                zipObj = rarfile.RarFile(filePath, 'r')
                self.cleanArchiveFile(zipObj, filePath)
            except Exception as e:
                logging.error("{}: {}".format(filePath, e))
                return
        elif tarfile.is_tarfile(filePath):
            try:
                zipObj = tarfile.TarFile(filePath, 'r')
                self.cleanArchiveFile(zipObj, filePath)
            except Exception as e:
                logging.error("{}: {}".format(filePath, e))
                return
        elif filePath.lower().endswith(image_ext):
            image_pil = Image.open(filePath)
            image_pil = image_pil.convert('RGB')
            w, h = image_pil.size
            if filePath.lower().endswith(('.jpg', '.png', '.jpeg')):

                # Resize ratio image
                image_pil.thumbnail(image_size)

                # Check if .webp exist or not
                if name + ".webp" not in os.listdir(dirPath):
                    image_pil.save(os.path.join(
                        dirPath, name + ".webp"), "webp", quality=100)
                    # Remove old file
                    if os.path.exists(filePath):
                        os.remove(filePath)
                else:
                    logging.error(
                        "{}: There is already .webp file, please check.".format(filePath))
                    return
            elif filePath.lower().endswith('.webp') and w > 1024 and h > 1024:

                # Resize ratio image
                image_pil.thumbnail(image_size)

                # Override old .webp
                image_pil.save(os.path.join(dirPath, name +
                               ".webp"), "webp", quality=100)
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

                # Override old .gif
                image_pil.save(os.path.join(dirPath, name + ".gif"),
                               save_all=True, append_images=list(frames))
            return
        elif filePath.lower().endswith(subtitle_ext):
            # Subtitle File
            return
        elif filePath.lower().endswith(video_ext):
            
            # Remove temp.mp4 if exist
            if os.path.exists(os.path.join(temp_dirPath, "temp.mp4")):
                os.remove(os.path.join(temp_dirPath, "temp.mp4"))

            # ffmpeg initial command
            command = ['-i', filePath]
            
            # Subtitle file
            subFilePath = None
            for ext in subtitle_ext:
                if os.path.exists(os.path.join(dirPath, name + ext)):
                    subFilePath = os.path.join(dirPath, name + ext)
                    command.extend(['-i', subFilePath])
                    break
            
            if filePath.lower().endswith('.mkv'):
                file = open(filePath, 'rb')
                mkv = enzyme.MKV(file)

                # Video track
                if len(mkv.video_tracks) == 1:
                    command.extend(['-map', '0:v:0'])

                    # Check if video is h264 or h265
                    if mkv.video_tracks[0].codec_id not in ["V_MPEG4/ISO/AVC", "V_MPEGH/ISO/HEVC"]:
                        command.extend(['-c:v', 'libx264'])
                    else:
                        command.extend(['-c:v', 'copy'])
                else:
                    logging.error("{}: There are more than one video track.")
                    return

                # Audio track
                for index, track in enumerate(mkv.audio_tracks):
                    if track.language == "jpn":
                        command.extend(['-map', '0:a:' + str(index)])

                        # Check if audio is aac
                        if track.codec_id != "A_AAC":
                            command.extend(['-c:a', 'aac'])
                        else:
                            command.extend(['-c:a', 'copy'])
                        break
                else:
                    if len(mkv.audio_tracks) != 0:
                        command.extend(['-map', '0:a:0', '-c:a', 'copy'])
                    else:
                        logging.error("{}: There is no audio track.".format(filePath))
                        return

                # Subtitle track
                if subFilePath:
                    command.extend(['-map', '1:s:0', '-c:s', 'mov_text'])
                else:
                    for index, track in enumerate(mkv.subtitle_tracks):
                        if track.language == "jpn":
                            command.extend(['-map', '0:s:' + str(index)])
                            
                            if track.codec_id == "S_TEXT/ASS":
                                command.extend(['-c:s', 'mov_text'])
                            else:
                                logging.error("{}: Subtitle only support ass (text-based subtitle) codec".format(filePath))
                                return
                            break
                    else:
                        if len(mkv.subtitle_tracks) != 0:
                            command.extend(['-map', '0:s:0'])
                            if mkv.subtitle_tracks[0].codec_id == "S_TEXT/ASS":
                                command.extend(['-c:s', 'mov_text'])
                            else:
                                logging.error("{}: Subtitle only support ass codec".format(filePath))
                                return
                
                # Add metadata and output
                command.extend(['-metadata:s:a:0', 'language=jpn',
                            '-metadata:s:s:0', 'language=eng', os.path.join(temp_dirPath, "temp.mp4")])
                
                # Run command
                ffpb.main(command, tqdm=tqdm)
                
                # Close mkv file
                file.close()
            elif filePath.lower().endswith('.mp4') and subFilePath:
                command.extend(['-map', '0:v', '-c:v', 'copy', '-map', '0:a', '-c:a', 'copy', '-map', '1:s:0', '-c:s', 'mov_text', '-metadata:s:a:0', 'language=jpn',
                            '-metadata:s:s:0', 'language=eng', os.path.join(temp_dirPath, "temp.mp4")])
                
                # Run command
                ffpb.main(command, tqdm=tqdm)
            
            # Remove old file if convert success
            if os.path.exists(os.path.join(temp_dirPath, "temp.mp4")):
                
                # Remove old file
                if os.path.exists(filePath):
                    os.remove(filePath)
                
                # Remove subtitle file
                if subFilePath and os.path.exists(subFilePath):
                    os.remove(subFilePath)

                shutil.move(os.path.join(temp_dirPath, "temp.mp4"),
                            os.path.join(dirPath, name + ".mp4"))
                
            return
        else:
            kind = filetype.guess(filePath)
            if kind is None:
                logging.error("{}: File format unknown.".format(filePath))
                return
            else:
                logging.error("{}: We do not support {}.".format(
                    filePath, kind.mime))
                return

    def cleanRecur(self, author, author_path, isChapter=False):

        if isChapter:
            # Check if there is only one image in folder
            # Only one image in Chapter Folder mean it is thumbnail
            imageList = [chapFile for chapFile in os.listdir(
                author_path) if chapFile.lower().endswith(image_ext)]
            if len(os.listdir(author_path)) >= 1 and len(imageList) == 1:
                # This folder contain thumbnail image
                isThumbnail = True
            else:
                # This folder does not contain thumbnail image
                isThumbnail = False
            
        tqdm_progress = tqdm(os.listdir(author_path), leave=False, bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}')
        chapters_index_list = []
        for old_fileDir in tqdm_progress:
            
            # tqdm Progress description
            if isChapter:
                tqdm_progress.set_description("Chapter Folder Progress ({})".format(old_fileDir))
            else:
                tqdm_progress.set_description("Author Folder Progress ({})".format(old_fileDir))
            
            # Split ext if it is file to get only filename
            name, ext = os.path.splitext(old_fileDir)

            # Get filename from format '[author|artist] filename'
            _, new_name = self.sep_author_name(name)
            
            # Filename condition
            if isChapter and old_fileDir.lower().endswith(image_ext) and isThumbnail:
                # Thumbnail in chapter folder
                new_name = "[" + author + "] " + "thumbnail"
            elif isChapter:
                # General File in chapter folder
                
                # Find chapter indiate pattern
                if re.search(r'\d{1,3}[a-z]$', new_name):
                    # special chapter like 2a, 3b, 4c
                    match = re.findall(r'\d{1,3}[a-z]$', new_name)
                    
                    # Chapter's Folder name + chapter indicator
                    new_name = " ".join([os.path.basename(author_path), match[-1]])
                elif re.search(r'\d{1,3}$', new_name):
                    # normal chapter like 2, 3, 4
                    match = re.findall(r'\d{1,3}$', new_name)
                    
                    # Chapter's Folder name + chapter indicator
                    new_name = " ".join([os.path.basename(author_path), match[-1]])
                    chapters_index_list.append(int(match[-1]))
                else:
                    logging.error("{}: Can not find chapter indicate pattern, please check.".format(
                        os.path.join(author_path, old_fileDir)))
                    continue
            else:
                # General File in author folder
                # add author name to the front
                new_name = "[" + author + "] " + new_name
            
            if ext != "":
                new_fileDir = new_name + ext
            else:
                new_fileDir = new_name

            # Rename
            if new_fileDir != old_fileDir:
                new_fileDir = self.renameRecur(author_path, old_fileDir, new_fileDir)

            if os.path.isdir(os.path.join(author_path, new_fileDir)):
                if len(os.listdir(os.path.join(author_path, new_fileDir))) == 0:
                    # Remove empty chapter's folder
                    os.rmdir(os.path.join(author_path, new_fileDir))
                else:
                    self.cleanRecur(author, os.path.join(
                        author_path, new_fileDir), isChapter=True)
            else:
                self.cleanFile(os.path.join(author_path, new_fileDir))

        # Check if all chapter complete (Not include special chapter)
        if isChapter:
            if len(chapters_index_list) != 0:
                missing_chapter = []
                for index in range(1, natsorted(chapters_index_list)[-1]+1):
                    if index not in chapters_index_list:
                        missing_chapter.append(index)

                if len(missing_chapter) != 0:
                    logging.error("{}: Chapter {} is missing.".format(author_path, missing_chapter))
                    return
            else:
                logging.error(
                    "{}: Can not find chapter item".format(author_path))
                return
