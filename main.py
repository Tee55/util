from argparse import ArgumentParser
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
        '-m', '-module', '--module', default="formatter", choices=['formatter', 'updater'],
        help='Choose Module you want to run (formatter, updater)'
    )
    parser.add_argument(
        '-t', '-type', '--type', default="content", choices=['author', 'content', "category", "collection"],
        help='Choose what kind of folder you want to run'
    )
    parser.add_argument(
        '-source', '--source', default="",
        help='Choose source folder'
    )
    parser.add_argument(
        '-target', '--target', default="",
        help='Choose target folder'
    )
    args = parser.parse_args()
    
    if args.module == "formatter":
        
        if args.source != "":
            sourcePath = args.source
        else:
            tk = tk.Tk()
            sourcePath = filedialog.askdirectory()
            tk.destroy()

        print("Select source dir path: {}".format(sourcePath))

        formatter = Formatter()
        
        if args.type == "content":
            if os.path.basename(sourcePath) in ["r18", "norm"]:
                formatter.clean(sourcePath)
            else:
                print("{}: This is not content folder.".format(sourcePath))
        elif args.type == "author":
            if os.path.basename(sourcePath) not in ["r18", "norm"]:
                old_author = os.path.basename(sourcePath)
                contentPath = os.path.dirname(sourcePath)
                
                # Get cleaned author name
                new_author = formatter.cleanName(old_author, isAuthor=True)

                # Rename
                if new_author != old_author:
                    new_author = formatter.renameRecur(
                        contentPath, old_author, new_author)
                
                formatter.cleanRecur(new_author, os.path.join(
                        contentPath, new_author), isChapter=False)
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
            
    elif args.module == "updater":
        
        if args.source != "" and args.target != "":
            sourcePath = args.source
            targetPath = args.target
        else:
            tk = tk.Tk()
            sourcePath = filedialog.askdirectory()
            targetPath = filedialog.askdirectory()
            tk.destroy()

        print("Select source dir path: {}".format(sourcePath))
        print("Select dir path you want to update: {}".format(targetPath))

        updater = Updater()
        
        if os.path.basename(sourcePath) in ["r18", "norm"]:
            if os.path.basename(targetPath) in ["r18", "norm"]:
                updater.run(sourcePath, targetPath)
            else:
                print("{}: TARGET_FOLDER is not CONTENT_FOLDER".format(sourcePath))
        else:
            print("{}: SOURCE_FOLDER is not CONTENT_FOLDER".format(sourcePath))

    print("======Finish======")