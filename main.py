import os

from dotenv import load_dotenv
from photo_downloader import ImagesDownloader

load_dotenv()

CUSTOM_PATH = os.getenv("CUSTOM_PATH")
result = ImagesDownloader.download_images(CUSTOM_PATH, 'dog', 1)
