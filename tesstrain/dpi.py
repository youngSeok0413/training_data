# 1. 이미지 DPI 설정 (Python)
from PIL import Image
import os

folder = "data/korLicense-ground-truth"
for filename in os.listdir(folder):
    if filename.endswith(".tif"):
        path = os.path.join(folder, filename)
        img = Image.open(path)
        img.save(path, dpi=(300, 300))
