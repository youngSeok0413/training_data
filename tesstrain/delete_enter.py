from pathlib import Path

def strip_newlines_in_gt_txt(folder: str) -> None:
    """
    지정 폴더의 .gt.txt 파일들을 모두 읽어 개행 문자를 제거하고
    UTF-8 형식으로 원본 파일을 덮어쓴다.

    Parameters
    ----------
    folder : str
        .gt.txt 파일들이 있는 디렉터리 경로
    """
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"❌ 디렉터리가 아닙니다: {root}")

    for fp in root.glob("*.gt.txt"):
        try:
            text = fp.read_text(encoding="utf-8")  # UTF-8로 읽기
        except UnicodeDecodeError:
            print(f"[오류] {fp.name} : UTF-8로 읽을 수 없습니다. 건너뜀")
            continue

        original_length = len(text)
        cleaned = text.replace("\r", "").replace("\n", "")
        if cleaned == text:
            print(f"[무변경] {fp.name} : 개행 없음")
            continue

        fp.write_text(cleaned, encoding="utf-8")  # UTF-8로 덮어쓰기
        print(f"[완료]   {fp.name} : {original_length - len(cleaned)}문자 제거")

# 사용 예시
# 경로는 원하는 디렉토리 경로로 바꾸어 사용하십시오.
folder_path = "/home/elicer/workspace/tesseract-ocr-train/tesstrain/data/korLicense-ground-truth"
strip_newlines_in_gt_txt(folder_path)
