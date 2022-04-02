import os
import shutil
from module.formatter import Formatter
import time
import datetime
from tqdm import tqdm
import logging
from tqdm.contrib.logging import logging_redirect_tqdm
from module.general import temp_dirPath
import zipfile
import rarfile
import tarfile

formatter = Formatter()


class Updater:

    def __init__(self):

        # Truncate the log file
        with open(os.path.join(temp_dirPath, "error.log"), 'w'):
            pass

        logging.basicConfig(filename=os.path.join(
            temp_dirPath, "error.log"), filemode="a")
        self.logger = logging.getLogger()
        self.formatter = Formatter()

    def run(self, sourcePath, targetPath):

        files = []
        for r, d, f in os.walk(sourcePath):
            for file in f:
                files.append(os.path.join(r, file))

        tqdm_progress = tqdm(files, leave=False,
                             bar_format='{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt}')

        # Loop all file
        for filePath in tqdm_progress:
            old_filename = os.path.basename(filePath)

            tqdm_progress.set_description(
                "Files Progress ({:10})".format(old_filename))

            dirPath = os.path.dirname(filePath)
            name, ext = os.path.splitext(old_filename)

            # Get author name from filename
            author, new_name = self.formatter.sep_author_name(name)
            if author:
                author = self.formatter.cleanName(author, isAuthor=True)
            else:
                with logging_redirect_tqdm():
                    self.logger.error("{}: Cannot get author name.".format(
                        os.path.join(dirPath, old_filename)))
                return

            # Use correct ext
            if zipfile.is_zipfile(os.path.join(dirPath, old_filename)):
                ext = ".cbz"
            elif rarfile.is_rarfile(os.path.join(dirPath, old_filename)):
                ext = ".cbr"
            elif tarfile.is_tarfile(os.path.join(dirPath, old_filename)):
                ext = ".cbt"

            # New filename
            new_filename = "[" + author + "] " + new_name + ext

            # Rename filename
            if new_filename != old_filename:
                new_filename = formatter.renameRecur(
                    dirPath, old_filename, new_filename)
            else:
                new_filename = old_filename

            # Clean file
            formatter.cleanFile(os.path.join(dirPath, new_filename))

            # Create author folder if not exist
            if author not in os.listdir(targetPath):
                os.makedirs(os.path.join(targetPath, author))

            # Move file
            shutil.move(os.path.join(dirPath, new_filename), os.path.join(targetPath, author, new_filename))
