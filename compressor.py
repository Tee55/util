import os
from tkinter import filedialog
from tkinter import *
import zipfile
import shutil
from progress.bar import Bar

image_ext = ('.jpg', 'png')
zip_ext = ('.zip', '.rar', '.cbz', '.cbr')


class Compressor:

    def __init__(self):
        pass

    def run(self):

        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        tk.destroy()

        filelist = []
        for root, dirs, files in os.walk(srcPath):
            for file in files:
                filelist.append(os.path.join(root, file))

        bar = Bar('Processing', max=len(filelist))
        for fullPath in filelist:
            components = fullPath.split(os.sep)
            arthur = components[1]
            if arthur not in os.listdir(srcPath):
                os.makedirs(os.path.join(srcPath, arthur))

            filename = os.path.basename(fullPath)
            name, ext = os.path.splitext(filename)

            if os.path.exists(fullPath):
                if ext.lower().endswith(image_ext):
                    dirPath = os.path.dirname(fullPath)

                    zipPath = os.path.join(srcPath, arthur, name + ".cbz")
                    zipobj = zipfile.ZipFile(zipPath, "w")

                    for image_file in os.listdir(dirPath):
                        if image_file.lower().endswith(image_ext):
                            zipobj.write(os.path.join(
                                dirPath, image_file), arcname=image_file)
                            os.remove(os.path.join(dirPath, image_file))
                    zipobj.close()

                    if len(os.listdir(dirPath)) == 0:
                        os.rmdir(dirPath)
                elif ext.lower().endswith(zip_ext):
                    movePath = os.path.join(srcPath, arthur, name + ".cbz")
                    if not os.path.exists(movePath):
                        print("Move zipfile to: {}".format(movePath))
                        shutil.move(fullPath, movePath)
            bar.next()


if __name__ == '__main__':
    compressor = Compressor()
    compressor.run()
