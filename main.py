from argparse import ArgumentParser
from module.compressor import Compressor
from module.formatter import Formatter
from module.updater import Updater
import os
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
import ctypes

# Make tk window clear in high dpi screen
ctypes.windll.shcore.SetProcessDpiAwareness(1)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-m', '-module', '--module', default="formatter", choices=['compressor', 'formatter', 'updater'],
        help='Choose Module you want to run (compressor, formatter, updater)'
    )
    parser.add_argument(
        '-t', '-type', '--type', default="content", choices=['author', 'content', "category", "collection"],
        help='Choose what kind of folder you want to run'
    )
    args = parser.parse_args()
    
    if args.module == "formatter":
        
        root = tk.Tk()
        root.call('tk', 'scaling', 4.0)
        sourcePath = filedialog.askdirectory()
        print("Select source dir path: {}".format(sourcePath))
        root.destroy()

        formatter = Formatter()
        
        if args.type == "content":
            if os.path.basename(sourcePath) in ["r18", "norm"]:
                formatter.clean(sourcePath)
            else:
                print("{}: This is not content folder.".format(sourcePath))
        elif args.type == "author":
            if os.path.basename(sourcePath) not in ["r18", "norm"]:
                author = os.path.basename(sourcePath)
                formatter.cleanRecur(author, sourcePath, isChapter=False)
        elif args.type == "category":
            for content_folder in os.listdir(sourcePath):
                if content_folder in ["r18", "norm"]:
                    formatter.clean(os.path.join(sourcePath, content_folder))
        elif args.type == "collection":
            for category_folder in tqdm(os.listdir(sourcePath), desc='Collection Folder Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
                if os.path.isdir(os.path.join(sourcePath, category_folder)):
                    for content_folder in os.listdir(os.path.join(sourcePath, category_folder)):
                        if content_folder in ["r18", "norm"]:
                            formatter.clean(os.path.join(sourcePath, category_folder, content_folder))
    elif args.module == "compressor":
        
        root = tk.Tk()
        root.call('tk', 'scaling', 4.0)
        sourcePath = filedialog.askdirectory()
        print("Select source dir path: {}".format(sourcePath))
        root.destroy()
        
        if os.path.basename(sourcePath) in ["r18", "norm"]:
            compressor = Compressor()
            compressor.run(sourcePath)
        else:
            print("{}: SOURCE_FOLDER is not CONTENT_FOLDER".format(sourcePath))
            
    elif args.module == "updater":
        
        tk = tk.Tk()
        sourcePath = filedialog.askdirectory()
        print("Select source dir path: {}".format(sourcePath))
            
        targetPath = filedialog.askdirectory()
        print("Select dir path you want to update: {}".format(targetPath))
        tk.destroy()
        
        if os.path.basename(sourcePath) in ["r18", "norm"]:
            if os.path.basename(targetPath) in ["r18", "norm"]:
                updater = Updater()
                updater.run(sourcePath, targetPath)
            else:
                print("{}: TARGET_FOLDER is not CONTENT_FOLDER".format(sourcePath))
        else:
            print("{}: SOURCE_FOLDER is not CONTENT_FOLDER".format(sourcePath))