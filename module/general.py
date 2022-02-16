import logging
from tqdm import tqdm

zip_ext = ('.zip', '.rar', '.cbz', '.cbr')
image_ext = ('.jpg', '.png', '.webp', '.jpeg')
video_ext = ('.mp4', '.avi', '.mkv')
subtitle_ext = ('.srt', '.ass')
image_size = (1024, 1024)
temp_dirPath = "./temp/"
leftkeys = (81, 110, 65361, 2424832)
rightkeys = (83, 109, 65363, 2555904)

class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record) 