from module.general import image_ext, subtitle_ext, video_ext, image_size, temp_dirPath
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
from tqdm.contrib.logging import logging_redirect_tqdm

from PIL import Image, ImageFile, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

rarfile.UNRAR_TOOL = "UnRAR.exe"


class Formatter:

    def __init__(self):
        
        # Truncate the log file
        with open(os.path.join(temp_dirPath, "error.log"), 'w'):
            pass
        
        logging.basicConfig(filename=os.path.join(
            temp_dirPath, "error.log"), filemode="a")
        self.logger = logging.getLogger()
        self.session_datetime = datetime.datetime.now().strftime("%y%m%d %H%M%S")
        
        if not os.path.exists(temp_dirPath):
            os.mkdir(temp_dirPath)
        else:
            for filename in os.listdir(temp_dirPath):
                if os.path.isfile(os.path.join(temp_dirPath, filename)) and filename.startswith('temp'):
                    os.remove(os.path.join(temp_dirPath, filename))

    def cleanName(self, name, isAuthor=False):

        # Remove head and tail whitespaces
        name = name.strip()

        # Slugify
        name_output = slugify(name, separator=" ", allow_unicode=True)

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

    def renameRecur(self, dir_path, old_fileDir, new_fileDir):
        new_name, ext = os.path.splitext(new_fileDir)

        while True:
            # Rename if not exist
            if new_fileDir not in os.listdir(dir_path):
                os.rename(os.path.join(dir_path, old_fileDir),
                        os.path.join(dir_path, new_fileDir))
                break
            else:
                suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                time.sleep(1)
                new_name = " ".join([new_name, suffix])
                
                if ext != "":
                    new_fileDir = new_name + ext
                else:
                    new_fileDir = new_name
            
        return new_fileDir

    def clean(self, contentPath):

        for old_author in tqdm(natsorted(os.listdir(contentPath)), desc='Content Folder Progress', bar_format='{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt}'):

            # Check if it is dir (author folder)
            if os.path.isdir(os.path.join(contentPath, old_author)):

                # Remove empty folder
                if len(os.listdir(os.path.join(contentPath, old_author))) == 0:
                    os.rmdir(os.path.join(contentPath, old_author))
                else:
                    # Get cleaned author name
                    new_author = self.cleanName(old_author, isAuthor=True)

                    # Rename
                    if new_author != old_author:
                        new_author = self.renameRecur(
                            contentPath, old_author, new_author)

                    # Clean item inside author folder
                    self.cleanRecur(new_author, os.path.join(
                        contentPath, new_author))
            else:
                with logging_redirect_tqdm():
                    self.logger.error("{}: This is not AUTHOR_FOLDER.".format(
                        os.path.join(contentPath, old_author)))
                    continue

    def sep_author_name(self, name):

        # Get text inside []
        if name.find("[") >= 0 and name.find("]") >= 0:
            author = name[name.find("[")+1:name.find("]")]

            # Get text inside ()
            if author.find("(") >= 0 and author.find(")") >= 0:
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

    def cleanArchiveFile(self, zipObj, filePath, image_check=3):

        # General info
        filename = os.path.basename(filePath)
        name, ext = os.path.splitext(filename)
        dirPath = os.path.dirname(filePath)
        
        # Remove temp.zip if exist
        if os.path.exists(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime))):
            os.remove(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime)))

        isWrite = False
        isManhwa = False
        combined_image_height = 0
        image_count = 0
        for fileDirPath in natsorted(zipObj.namelist()):
            if fileDirPath.lower().endswith(image_ext):
                # Check images if it need to write (Save time)
                try:
                    image_pil = Image.open(zipObj.open(fileDirPath))
                    image_pil = image_pil.convert('RGB')
                    w, h = image_pil.size
                    image_count += 1
                except Exception as e:
                    # Close archieve file
                    zipObj.close()

                    with logging_redirect_tqdm():
                        self.logger.error("{}: {}".format(filePath, e))
                    return

                zipItem_filename = os.path.basename(fileDirPath)           
                zipItem_name, ext = os.path.splitext(zipItem_filename)

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
                elif zipItem_name != str(image_count):
                    isWrite = True

                if isWrite or image_count >= image_check:
                    break
                
        if isWrite:

            # Create temp.zip
            new_zipObj = zipfile.ZipFile(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime)), 'w')

            # Get all image file in archieve
            imageList = []
            for fileDirPath in natsorted(zipObj.namelist()):
                if fileDirPath.lower().endswith(image_ext):
                    try:
                        image_pil = Image.open(zipObj.open(fileDirPath))
                        image_pil = image_pil.convert('RGB')
                        imageList.append(image_pil)
                    except Exception as e:
                        # Close archieve file
                        zipObj.close()
                        new_zipObj.close()

                        if os.path.exists(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime))):
                            os.remove(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime)))

                        with logging_redirect_tqdm():
                            self.logger.error("{}: {}".format(filePath, e))
                        return

            if len(imageList) > 0:

                # If it is manhwa, combine all image vertically and slice in specific height
                if isManhwa:
                    combined_image = Image.new(
                        'RGB', (combined_image_width, combined_image_height))
                    y_offset = 0
                    for image_pil in imageList:
                        w, h = image_pil.size

                        # Ensure that all images have same width
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

                    for index, crop_image in enumerate(tqdm(crop_images, leave=False, desc='Archieve Images Progress', bar_format='{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt}')):
                        image_byte = io.BytesIO()
                        crop_image.save(image_byte, "webp", quality=100)
                        new_zipObj.writestr(
                            str(index+1) + ".webp", image_byte.getvalue())
                else:
                    for index, image_pil in enumerate(tqdm(imageList, leave=False, desc='Archieve Images Progress', bar_format='{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt}')):
                        image_pil.thumbnail(image_size)
                        image_byte = io.BytesIO()
                        image_pil.save(image_byte, "webp", quality=100)
                        new_zipObj.writestr(
                            str(index+1) + ".webp", image_byte.getvalue())
            else:
                with logging_redirect_tqdm():
                    self.logger.error(
                        "{}: Can not find image file in archieve.".format(filePath))
                return

            # Close archieve, so it can delete/move file
            zipObj.close()
            new_zipObj.close()

            # Remove original file
            if os.path.exists(filePath):
                # Remove old file
                os.remove(filePath)
            else:
                with logging_redirect_tqdm():
                    self.logger.error("{}: Cannot remove the file, file not exist".format(filePath))
                return

            # Move file from temp folder
            shutil.move(os.path.join(temp_dirPath, "temp {}.zip".format(self.session_datetime)),
                        os.path.join(dirPath, name + ".cbz"))
            return
        else:
            # Close archieve
            zipObj.close()
            
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
                with logging_redirect_tqdm():
                    self.logger.error("{}: {}".format(filePath, e))
                return
        elif rarfile.is_rarfile(filePath):
            try:
                zipObj = rarfile.RarFile(filePath, 'r')
                self.cleanArchiveFile(zipObj, filePath)
            except Exception as e:
                with logging_redirect_tqdm():
                    self.logger.error("{}: {}".format(filePath, e))
                return
        elif tarfile.is_tarfile(filePath):
            try:
                zipObj = tarfile.TarFile(filePath, 'r')
                self.cleanArchiveFile(zipObj, filePath)
            except Exception as e:
                with logging_redirect_tqdm():
                    self.logger.error("{}: {}".format(filePath, e))
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
                    with logging_redirect_tqdm():
                        self.logger.error(
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
            if os.path.exists(os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime))):
                os.remove(os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime)))

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
                    with logging_redirect_tqdm():
                        self.logger.error(
                            "{}: There are more than one video track.")
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
                        with logging_redirect_tqdm():
                            self.logger.error(
                                "{}: There is no audio track.".format(filePath))
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
                                with logging_redirect_tqdm():
                                    self.logger.error(
                                        "{}: Subtitle only support ass (text-based subtitle) codec".format(filePath))
                                return
                            break
                    else:
                        if len(mkv.subtitle_tracks) != 0:
                            command.extend(['-map', '0:s:0'])
                            if mkv.subtitle_tracks[0].codec_id == "S_TEXT/ASS":
                                command.extend(['-c:s', 'mov_text'])
                            else:
                                with logging_redirect_tqdm():
                                    self.logger.error(
                                        "{}: Subtitle only support ass codec".format(filePath))
                                return

                # Add metadata and output
                command.extend(['-metadata:s:a:0', 'language=jpn',
                                '-metadata:s:s:0', 'language=eng', os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime))])

                # Run command
                ffpb.main(command, tqdm=tqdm)

                # Close mkv file
                file.close()
            elif filePath.lower().endswith('.mp4') and subFilePath:
                command.extend(['-map', '0:v', '-c:v', 'copy', '-map', '0:a', '-c:a', 'copy', '-map', '1:s:0', '-c:s', 'mov_text', '-metadata:s:a:0', 'language=jpn',
                                '-metadata:s:s:0', 'language=eng', os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime))])

                # Run command
                ffpb.main(command, tqdm=tqdm)

            # Remove old file if convert success
            if os.path.exists(os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime))):

                # Remove old file
                if os.path.exists(filePath):
                    os.remove(filePath)

                # Remove subtitle file
                if subFilePath and os.path.exists(subFilePath):
                    os.remove(subFilePath)

                shutil.move(os.path.join(temp_dirPath, "temp {}.mp4".format(self.session_datetime)),
                            os.path.join(dirPath, name + ".mp4"))

            return
        else:
            kind = filetype.guess(filePath)
            if kind is None:
                with logging_redirect_tqdm():
                    self.logger.error(
                        "{}: File format unknown.".format(filePath))
                return
            else:
                with logging_redirect_tqdm():
                    self.logger.error("{}: We do not support {}.".format(
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
                isImageFolder = False
            elif len(imageList) == len(os.listdir(author_path)):
                isThumbnail = False
                isImageFolder = True
            else:
                # This folder does not contain thumbnail image
                isThumbnail = False
                isImageFolder = False

        tqdm_progress = tqdm(natsorted(os.listdir(author_path)), leave=False,
                             bar_format='{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt}')
        chapters_index_list = []
        for index, old_fileDir in enumerate(tqdm_progress):

            # tqdm Progress description
            if isChapter:
                tqdm_progress.set_description(
                    "Chapter Folder Progress ({:10})".format(old_fileDir))
            else:
                tqdm_progress.set_description(
                    "Author Folder Progress ({:10})".format(old_fileDir))

            # Split ext if it is file to get only filename
            name, ext = os.path.splitext(old_fileDir)

            # Get filename from format '[author|artist] filename'
            _, new_name = self.sep_author_name(name)

            # Filename condition
            if isChapter and old_fileDir.lower().endswith(image_ext) and isThumbnail:
                # Thumbnail in chapter folder
                new_name = "[" + author + "] " + "thumbnail"
            elif isChapter and isImageFolder:
                # Image Folder item rename
                 new_name = " ".join([os.path.basename(author_path), str(index+1)])
            elif isChapter:
                # General File in chapter folder

                # Find chapter indiate pattern
                if re.search(r'\d{1,3}[a-z]$', new_name):
                    # special chapter like 2a, 3b, 4c
                    match = re.findall(r'\d{1,3}[a-z]$', new_name)

                    # Chapter's Folder name + chapter indicator
                    new_name = " ".join(
                        [os.path.basename(author_path), match[-1]])
                elif re.search(r'\d{1,3}$', new_name):
                    # normal chapter like 2, 3, 4
                    match = re.findall(r'\d{1,3}$', new_name)

                    # Chapter's Folder name + chapter indicator
                    new_name = " ".join(
                        [os.path.basename(author_path), match[-1]])
                    chapters_index_list.append(int(match[-1]))
                else:
                    with logging_redirect_tqdm():
                        self.logger.error("{}: Can not find chapter indicate pattern, please check.".format(
                            os.path.join(author_path, old_fileDir)))
                    continue
            else:
                # General File in author folder
                # add author name to the front
                new_name = "[" + author + "] " + new_name

            if ext != "":

                # Use correct ext
                if zipfile.is_zipfile(os.path.join(author_path, old_fileDir)):
                    ext = ".cbz"
                elif rarfile.is_rarfile(os.path.join(author_path, old_fileDir)):
                    ext = ".cbr"
                elif tarfile.is_tarfile(os.path.join(author_path, old_fileDir)):
                    ext = ".cbt"

                new_fileDir = new_name + ext
            else:
                new_fileDir = new_name

            # Rename
            if new_fileDir != old_fileDir:
                new_fileDir = self.renameRecur(
                    author_path, old_fileDir, new_fileDir)

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
        if isChapter and not isImageFolder:
            if len(chapters_index_list) != 0:
                missing_chapter = []
                for index in range(1, natsorted(chapters_index_list)[-1]+1):
                    if index not in chapters_index_list:
                        missing_chapter.append(index)

                if len(missing_chapter) != 0:
                    with logging_redirect_tqdm():
                        self.logger.error("{}: Chapter {} is missing.".format(
                            author_path, missing_chapter))
                    return
            else:
                with logging_redirect_tqdm():
                    self.logger.error(
                        "{}: Can not find chapter item".format(author_path))
                return
