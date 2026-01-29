#!/bin/bash

# 스크립트 위치로 이동 (어디서 실행하든 안전하게)
cd "$(dirname "$0")"

# 가상환경 디렉토리 이름
VENV_DIR="venv"

# 가상환경이 없으면 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# 가상환경 내의 pip와 python 경로
PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python"

# 패키지 설치 (requirements.txt가 변경되었을 때를 대비해 항상 확인)
echo "Installing dependencies..."
"$PIP" install -r requirements.txt > /dev/null

# 메인 스크립트 실행
echo "Starting SEO Tool..."
"$PYTHON" main.py
