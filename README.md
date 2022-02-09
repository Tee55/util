# Utility for comic directory

### Initial Setup
```
pip install -r requirements.txt
```

### Keywords
```
FILE_FORMAT = '[author|artist] name.ext'
IMAGE_SIZE = 1024px (both width and height)
```

### Compressor
SOURCE_DIRECTORY Structure
```
My Source/                  # SOURCE_DIRECTORY
    ├── title01/            # ITEM_FOLDER
    │      ├── 01.jpg       # Image File
    │      ├── 02.jpg       # Image File
    │      ├── 03.jpg       # Image File
    │      └── ...
    └── title02.zip         # ITEM_FILE
```

DESIRED_DIRECTORY Structure
```
My Source/                   # SOURCE_DIRECTORY
    ├── author01/            # AUTHOR_FOLDER
    │      ├── title01.zip   # ITEM_FILE
    │      ├── title02.zip   # ITEM_FILE
    │      ├── title03.zip   # ITEM_FILE
    │      └── ...
    └── author02/            # AUTHOR_FOLDER
```
* Find all file in SOURCE_DIRECTORY as well as remove empty directory.
* Create an author folder in SOURCE_DIRECTORY and naming from this order.
    * Sub folder of SOURCE_DIRECTORY (Where this file inside) (Priority first)
    * If files are in root of SOURCE_DIRECTORY, then get author from filename itself (Seperate from FILE_FORMAT)
    * If none, then author is "unknown"
* Rename file to FILE_FORMAT. 
* If file is images in folder, then compress to single zip file.
* If file is archieve, then move to author folder.

### Formatter
* Slugnify -> Remove unneccessary words and special character from filename (Please see https://github.com/un33k/python-slugify for more information)
* Rename file to FILE_FORMAT, then do following
    * Reduce image size (keep aspect ratio) to IMAGE_SIZE
    * Convert .jpg, .png -> .webp image format
    * Convert .avi, .mkv -> .mp4 video format ***(This function need ffmpeg, you need to install ffmpeg correctly)***

### Updater
TARGET_DIRECTORY Structure (Directory you want to update)
```
My Source/                                 # TARGET_DIRECTORY
    ├── author01/                          # AUTHOR_FOLDER
    │      ├── title01.zip                 # ITEM_FILE
    │      ├── title02.zip                 # ITEM_FILE
    │      ├── title03/                    # CHAPTER_FOLDER
    │      │        ├── chapter01.zip      # CHAPTER_ITEM
    │      │        ├── chapter02.zip      # CHAPTER_ITEM
    │      │        └── chapter03.zip      # CHAPTER_ITEM
    │      └── ...      
    └── author02/                          # AUTHOR_FOLDER
```
For more information on TARGET_DIRECTORY Structure, please refer to reader project https://github.com/Tee55/reader.

* Format SOURCE_DIRECTORY using Formatter function.
* Get author and name from file, by following
    * Sub folder of SOURCE_DIRECTORY (Where this file inside) (Priority first)
    * If files are in root of SOURCE_DIRECTORY, then get author from filename itself (Seperate from FILE_FORMAT)
    * If none, then author is "unknown"
* Rename file to FILE_FORMAT.
* If file not exist, move to AUTHOR_FOLDER in TARGET_DIRECTORY.

### Create stanalone executable
```
pyinstaller --onefile main.py
```
