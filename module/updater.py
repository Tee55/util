import os
import shutil
import filetype
from tqdm import tqdm
import logging
from tqdm.contrib.logging import logging_redirect_tqdm

import zipfile
import rarfile
import tarfile

from util.module.general import temp_dirPath, image_ext, zip_ext
from util.module.formatter import Formatter

formatter = Formatter()

class Updater:

    def __init__(self):

        # Truncate the log file
        if not os.path.exists(temp_dirPath):
            os.mkdir(temp_dirPath)
            
        f = open(os.path.join(temp_dirPath, "error.log"), 'w+')
        f.close()

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

            if old_filename.lower().endswith(image_ext):

                # Compress images to zip
                zipobj = zipfile.ZipFile(os.path.join(
                    sourcePath, author, name + ".cbz"), "w")

                for image_file in os.listdir(dirPath):
                    if image_file.lower().endswith(image_ext):

                        # Write image in zip
                        zipobj.write(os.path.join(
                            dirPath, image_file), arcname=image_file)

                        # Remove image file in folder
                        if os.path.exists(os.path.join(dirPath, image_file)):
                            os.remove(os.path.join(dirPath, image_file))
                zipobj.close()

                # Remove image parent folder
                if len(os.listdir(dirPath)) == 0:
                    os.rmdir(dirPath)

                # Clean file
                formatter.cleanFile(os.path.join(
                    sourcePath, author, name + ".cbz"))

                # Create author folder if not exist
                if author not in os.listdir(targetPath):
                    os.makedirs(os.path.join(targetPath, author))

                # Move file
                shutil.move(os.path.join(dirPath, new_filename),
                            os.path.join(targetPath, author, new_filename))

            elif old_filename.lower().endswith(zip_ext):

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
                shutil.move(os.path.join(dirPath, new_filename),
                            os.path.join(targetPath, author, new_filename))
            else:
                kind = filetype.guess(filePath)
                if kind is None:
                    with logging_redirect_tqdm():
                        self.logger.error(
                            "{}: File format unknown.".format(filePath))
                    return
                else:
                    with logging_redirect_tqdm():
                        self.logger.error(
                            "{}: We do not support {}.".format(filePath, kind.mime))
                    return
