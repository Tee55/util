from argparse import ArgumentParser
from module.compressor import Compressor
from module.formatter import Formatter
from module.updater import Updater
import os

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-m', '-module', '--module', default="formatter", choices=['compressor', 'formatter', 'updater'],
        help='Choose Module you want to run (compressor, formatter, updater)'
    )
    parser.add_argument(
        '-t', '-type', '--type', default="content", choices=['content', 'author'],
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
            formatter.clean(srcPath)
        elif args.type == "author":
            author = os.path.basename(srcPath)
            formatter.cleanRecur(author, srcPath, isChapter=False)
        
    elif args.module == "compressor":
        compressor = Compressor()
        compressor.run()
    elif args.module == "updater":
        updater = Updater()
        updater.run()