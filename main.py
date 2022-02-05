from argparse import ArgumentParser
from module.compressor import Compressor
from module.formatter import Formatter
from module.updater import Updater

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-m', '-module', '--module', default="formatter", choices=['compressor', 'formatter', 'updater'],
        help='Choose Module you want to run (compressor, formatter, updater)'
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
        formatter.clean(srcPath)
    elif args.module == "compressor":
        compressor = Compressor()
        compressor.run()
    elif args.module == "updater":
        updater = Updater()
        updater.run()