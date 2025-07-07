#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rename_pairs_numeric.py
-----------------------
tesstrain ground‑truth 디렉터리에서 .tif/.tiff‑.gt.txt 쌍을
1.tif + 1.gt.txt, 2.tif + 2.gt.txt … 형태의 숫자 파일명으로 일괄 변경한다.

사용 예
  $ python rename_pairs_numeric.py /data/kor_plate-ground-truth        # 시뮬레이션
  $ python rename_pairs_numeric.py /data/kor_plate-ground-truth --apply
  $ python rename_pairs_numeric.py /data/kor_plate-ground-truth --apply --start 101
"""

from pathlib import Path
from unicodedata import normalize
import argparse
import sys
import os

# ✅ stdout 인코딩 보장: Linux/macOS/Windows 공통 대응
def ensure_utf8_encoding():
    encoding = getattr(sys.stdout, "encoding", None)
    if encoding is None or encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            os.environ["PYTHONIOENCODING"] = "utf-8"
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

ensure_utf8_encoding()

IMG_EXTS = {".tif", ".tiff"}
TXT_SUFFIX = ".gt.txt"

def nfc(p: Path) -> Path:
    """파일명을 NFC로 변환하고 확장자만 소문자로 유지한다."""
    if p.name.lower().endswith(TXT_SUFFIX):
        stem = normalize("NFC", p.name[:-len(TXT_SUFFIX)])
        new = f"{stem}{TXT_SUFFIX}"
    else:
        stem = normalize("NFC", p.stem)
        new = f"{stem}{p.suffix.lower()}"
    return p.with_name(new)

def collect_pairs(gt_dir: Path):
    """(image_path, txt_path) 쌍 리스트 반환. 쌍이 불완전하면 경고."""
    img_map, txt_map = {}, {}
    for fp in gt_dir.iterdir():
        if not fp.is_file():
            continue
        fp = nfc(fp)           # Unicode 정규화
        if fp != fp.with_name(fp.name):
            fp = fp.rename(fp) # 바뀐 이름으로 갱신

        if fp.suffix.lower() in IMG_EXTS:
            img_map[fp.stem] = fp
        elif fp.name.endswith(TXT_SUFFIX):
            txt_map[fp.stem[:-3]] = fp  # stem은 ".gt" 전까지

    pairs = []
    for base, img in sorted(img_map.items()):
        txt = txt_map.get(base)
        if txt is None:
            print(f"[경고] 이미지만 있고 .gt.txt 없음: {img.name}")
            continue
        pairs.append((img, txt))

    for base, txt in sorted(txt_map.items()):
        if base not in img_map:
            print(f"[경고] .gt.txt만 있고 이미지 없음: {txt.name}")

    return pairs

def rename_pairs(pairs, start=1, apply=False):
    """지정된 쌍을 start부터 숫자 이름으로 변경한다."""
    for idx, (img, txt) in enumerate(pairs, start):
        num_name = str(idx)
        new_img = img.with_name(num_name + img.suffix.lower())
        new_txt = txt.with_name(num_name + TXT_SUFFIX)

        if new_img.exists() or new_txt.exists():
            print(f"[오류] {new_img.name} 또는 {new_txt.name} 이미 존재 ‑ 건너뜀")
            continue

        print(f"{img.name}  →  {new_img.name}")
        print(f"{txt.name}  →  {new_txt.name}")
        if apply:
            img.rename(new_img)
            txt.rename(new_txt)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ground_truth_dir", type=Path,
                    help="*‑ground-truth 디렉터리")
    ap.add_argument("--apply", action="store_true",
                    help="실제 파일명을 변경 (기본은 dry‑run)")
    ap.add_argument("--start", type=int, default=1,
                    help="시작 숫자 (기본 1)")
    args = ap.parse_args()

    gt_dir = args.ground_truth_dir
    if not gt_dir.is_dir():
        sys.exit("❌ ground_truth_dir가 존재하지 않는 디렉터리입니다.")

    pairs = collect_pairs(gt_dir)
    print(f"\n총 {len(pairs)} 쌍이 처리 대상입니다.")
    rename_pairs(pairs, start=args.start, apply=args.apply)

    if not args.apply:
        print("\n※ 위 목록은 미리보기입니다. 실제 변경하려면 --apply 옵션을 추가하십시오.")

if __name__ == "__main__":
    main()
