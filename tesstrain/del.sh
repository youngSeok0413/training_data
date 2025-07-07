# 모든 .tif 파일 중에서 이름이 숫자이고 1~999 이외는 삭제
for file in *.tif; do
  base="${file%.tif}"
  if ! [[ "$base" =~ ^[0-9]+$ ]]; then
    continue  # 숫자가 아닌 이름은 무시
  fi
  if [ "$base" -lt 1 ] || [ "$base" -gt 999 ]; then
    rm "$file"
  fi
done

# .gt.txt 파일도 동일하게 처리
for file in *.gt.txt; do
  base="${file%.gt.txt}"
  if ! [[ "$base" =~ ^[0-9]+$ ]]; then
    continue
  fi
  if [ "$base" -lt 1 ] || [ "$base" -gt 999 ]; then
    rm "$file"
  fi
done
