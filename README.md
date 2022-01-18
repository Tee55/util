# Utility for formatting directory

### Setup
```
pip install -r requirements.txt
```

### Compressor
Find all file in source directory as well as remove empty directory. Create an author folder in source folder by using file's parent directory name -> (if fail) -> From filename itself -> (if fail) -> Author is "unknown". Rename file (zip, rar, cbz, cbx and cbr only) to format '[author|artist] filename.ext'. If it is images, then compress to single zip file (with rename as .cbz). If it is zip, rar, cbz, cbr or cbx, then move to author folder.

Source Directory Structure
```
My Source/                  # Source Folder
    ├── title01/              # Item File
    │      ├── 01.jpg       # Image File
    │      ├── 02.jpg       # Image File
    │      ├── 03.jpg       # Image File
    │      └── ...          # Content Folder
    └── title02/            # Content Folder
```

### Formatter
Slugnify -> Remove unneccessary words -> rename filename as format '[author|artist] filename.ext'

### Updater
Update new file to destined directory. For destined directory format, please refer to reader project https://github.com/Tee55/reader.
