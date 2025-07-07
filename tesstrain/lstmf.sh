#!/bin/bash

cd data/korLicense-ground-truth || exit 1

# 실패 파일 저장할 텍스트 파일
FAILED_LOG="failed_lstmf.txt"
FAIL_DIR="fail_images"

# 실패 폴더 생성
mkdir -p "$FAIL_DIR"
> "$FAILED_LOG"  # 기존 실패 기록 초기화

for f in *.tif; do
    base="${f%.tif}"

    # 1. .gt.txt 존재 확인
    if [ ! -f "$base.gt.txt" ]; then
        echo "❌ $base.gt.txt 없음, 건너뜀"
        continue
    fi

    # 2. DPI 확인
    dpi=$(identify -format "%x %y" "$f" 2>/dev/null || echo "0 0")
    if [[ "$dpi" == "0 0" ]]; then
        echo "⚠️  $f: DPI 0, 재저장 필요"
        continue
    fi

    # 3. lstmf 생성 시도
    tesseract "$f" "$base" --psm 6 lstm.train 2>/dev/null

    # 4. 결과 확인 및 정리
    if [ ! -f "$base.lstmf" ]; then
        echo "❌ $f → .lstmf 생성 실패 → 이동 및 로그 기록"
        echo "$base" >> "$FAILED_LOG"

        # 실패한 파일들을 fail_images 폴더로 이동
        mv -f "$base.tif" "$FAIL_DIR/" 2>/dev/null
        [ -f "$base.gt.txt" ] && mv -f "$base.gt.txt" "$FAIL_DIR/"
        [ -f "$base.box" ] && mv -f "$base.box" "$FAIL_DIR/"
    else
        echo "✅ $f → $base.lstmf 생성 완료"
    fi
done

echo ""
echo "📄 실패 목록은 $FAILED_LOG 에 저장되었습니다."
echo "📁 실패 이미지 및 관련 파일은 $FAIL_DIR/ 폴더로 이동되었습니다."
