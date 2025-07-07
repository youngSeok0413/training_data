#!/bin/bash

# === 설정 ===
LANG=korLicense
GROUND_TRUTH_DIR=data/${LANG}-ground-truth
CHECKPOINT_DIR=data/${LANG}/checkpoints
TRAINEDDATA_PATH=data/${LANG}/${LANG}.traineddata
LSTM_MODEL=data/kor/${LANG}.lstm  # kor.traineddata에서 추출된 초기 모델
TESSDATA=../tessdata/kor.traineddata  # 경로는 필요에 따라 수정
OUTPUT_MODEL=${LANG}.traineddata
TRAIN_LIST=data/${LANG}/list.train
EVAL_LIST=data/${LANG}/list.eval
LANGDATA_DIR=data/langdata/${LANG}

# === 0. 폴더 준비 ===
echo "[1] 디렉토리 생성"
mkdir -p ${CHECKPOINT_DIR}
mkdir -p ${LANGDATA_DIR}
mkdir -p data/${LANG}

# === 1. 이미지 DPI 설정 ===
echo "[2] 이미지 DPI를 300으로 설정"
python3 <<EOF
from PIL import Image
import os

folder = "${GROUND_TRUTH_DIR}"
for filename in os.listdir(folder):
    if filename.endswith(".tif"):
        path = os.path.join(folder, filename)
        img = Image.open(path)
        img.save(path, dpi=(300, 300))
EOF

# === 2. .lstmf 재생성 ===
echo "[3] 기존 .lstmf 삭제 및 재생성"
rm -f ${GROUND_TRUTH_DIR}/*.lstmf
for tif in ${GROUND_TRUTH_DIR}/*.tif; do
  base=$(basename "$tif" .tif)
  tesseract "$tif" "${GROUND_TRUTH_DIR}/$base" --psm 6 lstm.train
done

# === 3. list.train / list.eval 생성 ===
echo "[4] list.train / list.eval 생성"
ls ${GROUND_TRUTH_DIR}/*.lstmf | shuf > all.txt
head -n 80 all.txt > ${TRAIN_LIST}
tail -n 20 all.txt > ${EVAL_LIST}
rm all.txt

# === 4. wordlist/punc/numbers 파일 생성 ===
echo "[5] wordlist/punc/numbers 파일 생성 (빈 파일 또는 샘플)"
touch data/${LANG}/${LANG}.wordlist
touch data/${LANG}/${LANG}.punc
touch data/${LANG}/${LANG}.numbers

# === 5. korLicense.config 생성 (선택 사항) ===
echo "[6] korLicense.config 생성"
cat <<EOL > ${LANGDATA_DIR}/${LANG}.config
LangConfigFileVersion=1
ClassifyEnableLearning=1
EOL

# === 6. traineddata 생성 ===
echo "[7] traineddata 생성"
combine_lang_model \
  --input_unicharset data/${LANG}/unicharset \
  --script_dir data/langdata \
  --numbers data/${LANG}/${LANG}.numbers \
  --puncs data/${LANG}/${LANG}.punc \
  --words data/${LANG}/${LANG}.wordlist \
  --output_dir data/${LANG} \
  --lang ${LANG}

# === 7. 학습 시작 ===
echo "[8] 학습 시작"
lstmtraining \
  --debug_interval 0 \
  --traineddata ${TRAINEDDATA_PATH} \
  --old_traineddata ${TESSDATA} \
  --continue_from ${LSTM_MODEL} \
  --learning_rate 0.0001 \
  --model_output ${CHECKPOINT_DIR}/${LANG} \
  --train_listfile ${TRAIN_LIST} \
  --eval_listfile ${EVAL_LIST} \
  --max_iterations 4000 \
  --target_error_rate 0.01 \
2>&1 | tee data/${LANG}/training.log

# === 8. 학습 종료 후 모델 저장 ===
echo "[9] 학습 완료 모델 저장"
lstmtraining \
  --stop_training \
  --continue_from ${CHECKPOINT_DIR}/${LANG}_checkpoint \
  --traineddata ${TRAINEDDATA_PATH} \
  --model_output ${OUTPUT_MODEL}

echo "[✅ 완료] 최종 모델: ${OUTPUT_MODEL}"
