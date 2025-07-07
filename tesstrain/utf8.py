from pathlib import Path
import chardet
import unicodedata

def try_decodings(raw_bytes, encodings):
    """
    주어진 인코딩 리스트 순서대로 시도하여 디코딩에 성공하면 텍스트 반환.
    실패 시 None 반환.
    """
    for enc in encodings:
        try:
            return raw_bytes.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return None, None

def convert_gt_txt_to_utf8(folder: str, normalize_nfc=True) -> None:
    """
    .gt.txt 파일들의 실제 인코딩을 감지하고 UTF-8로 재저장.
    감지된 인코딩이 windows-1252이면 cp949, euc-kr, utf-8 등을 순차 시도.
    """
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"❌ 디렉터리가 아닙니다: {root}")

    converted, already_utf8, failed = 0, 0, 0

    for fp in sorted(root.glob("*.gt.txt")):
        try:
            raw = fp.read_bytes()
            detected = chardet.detect(raw)
            encoding = (detected["encoding"] or "").lower()

            if encoding in ["windows-1252", "iso-8859-1"]:
                # windows-1252 감지되면 cp949 등 여러 인코딩 시도
                encodings_to_try = ["cp949", "euc-kr", "utf-8"]
                text, used_enc = try_decodings(raw, encodings_to_try)
                if text is None:
                    print(f"❌ {fp.name}: cp949/euc-kr/utf-8 모두 디코딩 실패 (windows-1252 감지됨)")
                    failed += 1
                    continue
                encoding = used_enc
            elif encoding == "utf-8":
                print(f"✔️ 이미 UTF-8: {fp.name}")
                already_utf8 += 1
                continue
            else:
                text, used_enc = try_decodings(raw, [encoding, "utf-8", "cp949", "euc-kr"])
                if text is None:
                    print(f"❌ {fp.name}: {encoding} 및 fallback 인코딩 모두 디코딩 실패")
                    failed += 1
                    continue
                encoding = used_enc

            if normalize_nfc:
                text = unicodedata.normalize("NFC", text)

            fp.write_text(text, encoding="utf-8")
            print(f"✅ 변환 완료: {fp.name} ({encoding} → utf-8)")
            converted += 1

        except Exception as e:
            print(f"❌ 처리 실패: {fp.name} - {e}")
            failed += 1

    print("\n📊 처리 요약")
    print(f"  🔄 변환됨    : {converted}개")
    print(f"  ✅ 이미 UTF-8 : {already_utf8}개")
    print(f"  ❌ 실패        : {failed}개")

# 사용 예시
if __name__ == "__main__":
    folder_path = "data/korLicense-ground-truth"
    convert_gt_txt_to_utf8(folder_path)
