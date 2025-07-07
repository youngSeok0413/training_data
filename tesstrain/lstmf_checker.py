# fix_lstmf_images.py
from PIL import Image
import os

folder = "data/korLicense-ground-truth"
for file in os.listdir(folder):
    if file.endswith(".tif"):
        path = os.path.join(folder, file)
        img = Image.open(path)
        img.save(path, dpi=(300, 300))  # 재설정
