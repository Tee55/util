import os
import shutil
from module.formatter import Formatter
import time
import datetime
from tqdm import tqdm
import logging
from general import temp_dirPath, TqdmLoggingHandler

formatter = Formatter()

class Updater:

    def __init__(self):
        logging.basicConfig(filename=os.path.join(temp_dirPath, "error.log"), filemode = "w")
        self.logger = logging.getLogger()
        self.logger.addHandler(TqdmLoggingHandler())
        self.formatter = Formatter()

    def get_all_files_authors(self, fullPath):
        source_filelist = []
        source_authorList = []
        for root, dirs, files in os.walk(fullPath):
            for file in files:
                filePath = os.path.join(root, file)
                filename = os.path.basename(filePath)
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

                # Rename if filename is not as same as before
                if filename != new_filename:
                    if not os.path.exists(os.path.join(root, new_filename)):
                        os.rename(os.path.join(root, filename),
                                  os.path.join(root, new_filename))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d %H%M%S")
                        time.sleep(1)
                        new_name = " ".join([new_name, suffix])
                        new_filename = "[" + author + "] " + new_name + ext
                        if not os.path.exists(os.path.join(root, new_filename)):
                            os.rename(os.path.join(root, filename),
                                  os.path.join(root, new_filename))
                        else:
                            logging.error("{}: Problem with renaming file, please check.".format(os.path.join(root, filename)))
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
            if name not in target_namelist and not os.path.exists(movePath):
                # Create author folder if not exist
                if not os.path.exists(os.path.join(targetPath, author)):
                    os.makedirs(os.path.join(targetPath, author))
                
                # Move file
                shutil.move(fullPath, movePath)
            else:
                logging.error("{}: File already exist, please check.".format(fullPath))
                continue