import os
import shutil
from module.formatter import Formatter
import time
import datetime
from tqdm import tqdm
import logging
from tqdm.contrib.logging import logging_redirect_tqdm
from module.general import temp_dirPath

formatter = Formatter()

class Updater:

    def __init__(self):
        logging.basicConfig(filename=os.path.join(temp_dirPath, "error.log"), filemode = "a")
        self.logger = logging.getLogger()
        self.formatter = Formatter()

    def get_all_files_authors(self, fullPath):
        source_filelist = []
        source_authorList = []
        for root, dirs, files in os.walk(fullPath):
            for file in files:
                filePath = os.path.join(root, file)
                filename = os.path.basename(filePath)
                dirPath = os.path.dirname(filePath)
                name, ext = os.path.splitext(filename)
                
                # Try to get author name

                # 1st method
                author, new_name = self.formatter.sep_author_name(name)
                if author:
                    author = self.formatter.cleanName(author, isAuthor=True)
                else:
                    # 2st method
                    # Seperate each components from path
                    components = filePath.split(os.sep)
                    
                    # Use second component as author name
                    author = components[1]
                    if author:
                        author = self.formatter.cleanName(author, isAuthor=True)
                
                # New filename
                new_filename = "[" + author + "] " + new_name + ext

                # Rename filename
                if new_filename not in os.listdir(dirPath):
                    os.rename(os.path.join(root, filename),
                                os.path.join(root, new_filename))
                elif os.path.exists(os.path.join(root, new_filename)) and new_name != name:
                    suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                    time.sleep(1)
                    new_name = " ".join([new_name, suffix])
                    new_filename = "[" + author + "] " + new_name + ext
                    if new_filename not in os.listdir(dirPath):
                        os.rename(os.path.join(root, filename),
                                os.path.join(root, new_filename))
                    else:
                        with logging_redirect_tqdm():
                            self.logger.error("{}: Problem with renaming file, please check.".format(os.path.join(root, filename)))
                        continue

                source_filelist.append(os.path.join(root, new_filename))
                source_authorList.append(author)

        return source_filelist, source_authorList

    def run(self, sourcePath, targetPath):
        # Get all file fullpath and author name from both SOURCE_FOLDER and TARGET_FOLDER
        source_filelist, source_authorList = self.get_all_files_authors(sourcePath)
        target_filelist, target_authorList = self.get_all_files_authors(targetPath)

        # Get only name (not include ext)
        target_namelist = [os.path.splitext(os.path.basename(fullPath))[0] for fullPath in target_filelist]

        for fullPath, author in tqdm(zip(source_filelist, source_authorList), desc='Main Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
            filename = os.path.basename(fullPath)
            name = os.path.splitext(filename)[0]
            movePath = os.path.join(targetPath, author, filename)
            if name not in target_namelist:
                # Create author folder if not exist
                if author not in os.listdir(targetPath):
                    os.makedirs(os.path.join(targetPath, author))
                
                # Move file
                shutil.move(fullPath, movePath)
            else:
                with logging_redirect_tqdm():
                    self.logger.error("{}: File already exist, please check.".format(fullPath))
                continue