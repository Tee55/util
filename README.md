# Utility for formatting directory

### Initial Setup
```
pip install -r requirements.txt
```

### Before Usage (Please read and understand)
Source Directory Structure
```
My Source/                  # Source Folder
    ├── title01/            # Item File
    │      ├── 01.jpg       # Image File
    │      ├── 02.jpg       # Image File
    │      ├── 03.jpg       # Image File
    │      └── ...          # Content Folder
    └── title02/            # Content Folder
```

### Compressor
* Find all file in source directory as well as remove empty directory
* Create an author folder in source folder by using file's parent directory name -> (if fail) -> From filename itself -> (if fail) -> Author is "unknown". 
* Rename file (zip, rar, cbz, cbx and cbr only) to format '[author|artist] filename.ext'. 
* If it is images, then compress to single zip file (with rename as .cbz). 
* If it is zip, rar, cbz, cbr or cbx, then move to author folder.

### Formatter
* Slugnify -> Remove unneccessary words and special character from filename (Please see https://github.com/un33k/python-slugify for more information)
* Rename filename as format '[author|artist] name.ext' -> Then do following condition for file types
    * Reduce image size (keep aspect ratio) if width and height > 1024px
    * Convert .jpg, .png -> .webp image format
    * Convert .avi, .mkv -> .mp4 video format

### Updater
Update new file to destined directory. For destined directory format, please refer to reader project https://github.com/Tee55/reader.

### Create stanalone executable
```
pyinstaller --onefile main.py
```
