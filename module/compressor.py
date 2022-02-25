import os
import zipfile
import shutil
import filetype
from module.formatter import Formatter
import logging
from tqdm import tqdm
from module.general import zip_ext, image_ext, temp_dirPath
from tqdm.contrib.logging import logging_redirect_tqdm

class Compressor:

    def __init__(self):
        
        # Truncate the log file
        with open(os.path.join(temp_dirPath, "error.log"), 'w'):
            pass
        
        logging.basicConfig(filename=os.path.join(temp_dirPath, "error.log"), filemode = "a")
        self.logger = logging.getLogger()
        self.formatter = Formatter()
    
    def run(self, srcPath):
        
        for root, dirs, files in os.walk(srcPath):
            
            # Loop all files in SOURCE_FOLDER
            for file in tqdm(files, desc='Main Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
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
                
                # If none, author is "unknown"
                if not author:
                    author = "unknown"
                
                # Create author folder
                if author not in os.listdir(srcPath):
                    os.mkdir(os.path.join(srcPath, author))

                if filename.lower().endswith(image_ext):
                    
                    # Get images parent folder
                    dirPath = os.path.dirname(filePath)
                    
                    # Compress images to zip
                    zipPath = os.path.join(srcPath, author, name + ".zip")
                    zipobj = zipfile.ZipFile(zipPath, "w")
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
                        
                elif filename.lower().endswith(zip_ext):
                    dirPath = os.path.dirname(filePath)
                    movePath = os.path.join(srcPath, author, new_name + ext)
                    if new_name + ext not in os.listdir(os.path.join(srcPath, author)):
                        shutil.move(filePath, movePath)
                        
                        # Remove item parent folder if empty
                        if len(os.listdir(dirPath)) == 0:
                            os.rmdir(dirPath)
                    else:
                        with logging_redirect_tqdm():
                            self.logger.error("{}: File already exist, please check.".format(filePath))
                        continue
                else:
                    kind = filetype.guess(filePath)
                    if kind is None:
                        with logging_redirect_tqdm():
                            self.logger.error("{}: File format unknown.".format(filePath))
                        return
                    else:
                        with logging_redirect_tqdm():
                            self.logger.error("{}: We do not support {}.".format(filePath, kind.mime))
                        return
