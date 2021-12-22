import os
from tkinter import filedialog
from tkinter import *
import shutil
from progress.bar import Bar
from formatter import Formatter
import time
import datetime

formatter = Formatter()

class Updater:

    def __init__(self):
        pass

    def get_all_files_arthurs(self, srcPath):
        src_filelist = []
        src_arthurList = []
        for root, dirs, files in os.walk(srcPath):
            for filename in files:
                name, ext = os.path.splitext(filename)
                arthur, new_name = formatter.sep_arthur_name(name)
                new_filename = "[" + arthur + "] " + new_name + ext
                if not arthur:
                    components = root.split(os.sep)
                    arthur = components[1]

                if filename != new_filename:
                    if not os.path.exists(os.path.join(root, new_filename)):
                        os.rename(os.path.join(root, filename),
                                  os.path.join(root, new_filename))
                    else:
                        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                        time.sleep(1)
                        new_name = "_".join([new_name, suffix])
                        new_filename = "[" + arthur + "] " + new_name + ext
                        os.rename(os.path.join(root, filename),
                                  os.path.join(root, new_filename))

                src_filelist.append(os.path.join(root, new_filename))
                src_arthurList.append(arthur)

        return src_filelist, src_arthurList

    def run(self):
        tk = Tk()
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))

        destPath = filedialog.askdirectory()
        print("Select dir path you want to update: {}".format(destPath))
        tk.destroy()

        src_filelist, src_arthurList = self.get_all_files_arthurs(srcPath)
        dest_filelist, dest_arthurList = self.get_all_files_arthurs(destPath)

        dest_namelist = [os.path.splitext(os.path.basename(fullPath))[
            0] for fullPath in dest_filelist]

        bar = Bar('Processing', max=len(src_filelist))
        for fullPath, arthur in zip(src_filelist, src_arthurList):
            if not os.path.exists(os.path.join(destPath, arthur)):
                os.makedirs(os.path.join(destPath, arthur))
            filename = os.path.basename(fullPath)
            name = os.path.splitext(filename)[0]
            if name not in dest_namelist:
                movePath = os.path.join(destPath, arthur, filename)
                if not os.path.exists(movePath):
                    shutil.move(fullPath, movePath)
            else:
                print("You already have: {}".format(filename))
            bar.next()
        bar.finish()


if __name__ == '__main__':
    updater = Updater()
    updater.run()
