#!/usr/bin/env python3
"""
audit_tif_pairs.py  ―  tesstrain ground‑truth 폴더 점검·수선 (Unicode‑safe)

특징
  • 이미지 확장자 : .tif / .tiff  (대소문자 불문, 한글·공백 파일명 허용)
  • GT 텍스트    : 동일 base + .gt.txt
  • 모든 파일명을 NFC + 소문자 확장자 로 정규화
  • 쌍 불완전 항목 보고 + (--fix) 시 자동 수선
사용 예시
  $ python audit_tif_pairs.py korLicense-ground-truth          # 검사만
  $ python audit_tif_pairs.py korLicense-ground-truth --fix --create-empty
"""

from pathlib import Path
from unicodedata import normalize
import argparse
import sys
import itertools

IMG_EXTS = {".tif", ".tiff"}
TXT_SUFFIX = ".gt.txt"

def _unique_name(dir_p: Path, name: str) -> Path:
    """충돌을 피하며 dir_p/name 이 없는 이름을 반환한다."""
    cand = dir_p / name
    if not cand.exists():
        return cand
    for i in itertools.count(1):
        dup = dir_p / f"{cand.stem}._dup{i}{cand.suffix}"
        if not dup.exists():
            return dup

def normalize_unicode_case(fp: Path) -> Path:
    """NFC + 확장자 소문자로 통일하고 필요하면 파일명 변경."""
    # .gt.txt 같은 다중 확장자 처리
    if fp.name.lower().endswith(TXT_SUFFIX):
        stem_raw = fp.name[:-len(TXT_SUFFIX)]
        stem_norm = normalize("NFC", stem_raw)
        new_name = f"{stem_norm}{TXT_SUFFIX}"
    else:
        stem_norm = normalize("NFC", fp.stem)
        new_name = f"{stem_norm}{fp.suffix.lower()}"
    new_p = fp.with_name(new_name)
    if fp != new_p:
        new_p = _unique_name(fp.parent, new_name)
        fp.rename(new_p)
        print(f"[rename] {fp.name} → {new_p.name}")
    return new_p

def scan(dir_p: Path):
    imgs, txts = set(), set()
    for fp in dir_p.iterdir():
        if not fp.is_file():
            continue
        fp = normalize_unicode_case(fp)
        if fp.suffix in IMG_EXTS:
            imgs.add(fp.stem)
        elif fp.name.endswith(TXT_SUFFIX):
            txts.add(fp.stem.replace(".gt", ""))
    return imgs, txts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ground_truth_dir", type=Path)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--create-empty", action="store_true",
                    help="이미지만 있고 .gt.txt 없는 경우 빈 파일 생성")
    ap.add_argument("--delete-orphan", action="store_true",
                    help=".gt.txt만 있고 이미지 없는 경우 삭제")
    args = ap.parse_args()

    if not args.ground_truth_dir.is_dir():
        sys.exit("ground_truth_dir가 디렉터리가 아닙니다.")

    imgs, txts = scan(args.ground_truth_dir)
    only_imgs = sorted(imgs - txts)
    only_txts = sorted(txts - imgs)
    matched   = len(imgs & txts)

    print(f"\n=== {args.ground_truth_dir} ===")
    print(f"✓ 매칭 쌍            : {matched}")
    print(f"✗ 이미지만 있는 항목  : {len(only_imgs)}")
    print(f"✗ .gt.txt만 있는 항목 : {len(only_txts)}")

    if not args.fix:
        print("\n(참고) --fix 옵션을 주면 자동 수선을 시도합니다.")
        return

    # ---------- 수선 ----------
    for base in only_imgs:
        tgt = args.ground_truth_dir / f"{base}{TXT_SUFFIX}"
        if args.create_empty:
            tgt.touch()
            print(f"[create] {tgt.name}")
        else:
            print(f"[warn]   {tgt.name} 없음 (빈 파일 만들려면 --create-empty)")

    for base in only_txts:
        txt_f = args.ground_truth_dir / f"{base}{TXT_SUFFIX}"
        if args.delete_orphan:
            txt_f.unlink()
            print(f"[delete] {txt_f.name}")
        else:
            print(f"[warn]   {txt_f.name} 고아 파일 (삭제하려면 --delete-orphan)")

    print("수선 완료. 다시 실행해 잔여 오류가 없는지 확인하세요.")

if __name__ == "__main__":
    main()
