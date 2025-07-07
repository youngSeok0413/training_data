from PIL import Image
import os

bad_files = []
folder = "data/korLicense-ground-truth"
for file in os.listdir(folder):
    if file.endswith(".tif"):
        path = os.path.join(folder, file)
        try:
            img = Image.open(path)
            dpi = img.info.get("dpi", (0, 0))
            if dpi[0] == 0 or dpi[1] == 0:
                bad_files.append(file)
        except:
            bad_files.append(file)

print(f"🚫 DPI=0 or corrupt: {len(bad_files)}")
for f in bad_files:
    print(f)
