from argparse import ArgumentParser
from module.compressor import Compressor
from module.formatter import Formatter
from module.updater import Updater
import os
from tqdm import tqdm

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-m', '-module', '--module', default="formatter", choices=['compressor', 'formatter', 'updater'],
        help='Choose Module you want to run (compressor, formatter, updater)'
    )
    parser.add_argument(
        '-t', '-type', '--type', default="content", choices=['content', 'author', "collection"],
        help='Choose what kind of folder you want to run'
    )
    args = parser.parse_args()
    
    if args.module == "formatter":
        import tkinter as tk
        from tkinter import filedialog
        import ctypes
        
        # Make tk window clear in high dpi screen
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        root = tk.Tk()
        root.call('tk', 'scaling', 4.0)
        srcPath = filedialog.askdirectory()
        print("Select source dir path: {}".format(srcPath))
        root.destroy()

        formatter = Formatter()
        
        if args.type == "content":
            if os.path.basename(srcPath) in ["r18", "norm"]:
                formatter.clean(srcPath)
            else:
                print("{}: This is not content folder.".format(srcPath))
        elif args.type == "author":
            if os.path.basename(srcPath) not in ["r18", "norm"]:
                author = os.path.basename(srcPath)
                formatter.cleanRecur(author, srcPath, isChapter=False)
        elif args.type == "collection":
            for item_folder in tqdm(os.listdir(srcPath), desc='Collection Folder Progress', bar_format='{l_bar}{bar:10}| {n_fmt}/{total_fmt}'):
                if os.path.isdir(os.path.join(srcPath, item_folder)):
                    formatter.clean(os.path.join(srcPath, item_folder))
        
    elif args.module == "compressor":
        compressor = Compressor()
        compressor.run()
    elif args.module == "updater":
        updater = Updater()
        updater.run()