import random
from pathlib import Path
from aiogram.types import FSInputFile

IMAGE_MAP = {
    "selfie": "images/selfie",
    "beach": "images/beach",
    "night": "images/night",
    "outdoor": "images/outdoor"
}

def get_random_image(category: str):
    folder_path = IMAGE_MAP.get(category)

    if not folder_path:
        return None

    folder = Path(folder_path)
    images = list(folder.glob("*"))

    if not images:
        return None

    return FSInputFile(str(random.choice(images)))
