cd data/korLicense-ground-truth
for f in *.tif; do
    base="${f%.tif}"
    if [ ! -f "$base.gt.txt" ]; then
        echo "❌ $base.gt.txt 누락"
    elif ! tesseract "$base.tif" "$base" --psm 6 lstm.train 2>/dev/null; then
        echo "❌ $base.tif lstmf 생성 실패"
    fi
done
