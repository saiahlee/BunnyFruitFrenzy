# 🐰 Bunny Fruit Frenzy

분홍색 토끼가 과일을 모으고 바퀴벌레를 피하는 아케이드 게임! Python + Pygame으로 만들어졌습니다.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)

## 🎮 게임 소개

은하수 스타일의 배경 위에서 귀여운 분홍 토끼가 떠다니는 과일들을 모으는 60초 아케이드 게임입니다. 바퀴벌레의 추적을 피하면서 최대한 많은 과일을 수집하세요!

### ✨ 주요 특징

- 🍎 **7가지 과일** — 사과, 바나나, 포도, 오렌지, 딸기, 체리, 수박
- 🪲 **추적형 바퀴벌레** — 점수가 오를수록 더 빠르고 집요하게 따라옵니다
- 📈 **점진적 난이도** — 점수에 따라 레벨이 올라가며 게임이 점점 빨라져요
- ⚡ **파워업** — Speed x2 부스터와 Life 회복 아이템
- 🏆 **최고 기록 영구 저장** — 다음 실행 시에도 기록이 유지됩니다
- 🎵 **8-bit 사운드트랙** — 모든 BGM과 효과음을 코드로 절차적 생성
- 🇰🇷 **한국어 UI** — Apple SD Gothic Neo, 맑은고딕 등 자동 감지

## 🕹️ 조작법

| 키 | 동작 |
|---|---|
| ← → ↑ ↓ | 토끼 이동 |
| `SPACE` / `ENTER` | 게임 시작 / 재시작 |
| `P` 또는 `ESC` | 일시정지 / 재개 |
| `Q` (일시정지 중) | 게임 종료 |

## 🎯 난이도 시스템

| 레벨 | 점수 | 변화 |
|---|---|---|
| LV 1 | 0–9 | 기본 |
| LV 2 | 10–19 | 바퀴벌레 약간 빠름 |
| LV 3 | 20–34 | 과일 더 자주, 추적 강화 |
| LV 4 | 35–54 | 본격적인 도전 |
| LV 5+ | 55+ | 끝없이 어려워짐! |

## 🚀 실행 방법

### 옵션 1: 빌드된 앱 실행 (macOS)

`dist/BunnyFruitFrenzy.app` 을 더블클릭하면 바로 실행됩니다.

### 옵션 2: Python으로 직접 실행

```bash
# 1) 가상환경 (선택)
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 2) 의존성 설치
pip install -r requirements.txt

# 3) 실행
python bunny_fruit_frenzy.py
```

## 📦 직접 패키징하기

PyInstaller로 단일 실행 파일/앱 번들을 만들 수 있습니다.

### macOS (.app 번들)

```bash
pip install pyinstaller
pyinstaller BunnyFruitFrenzy.spec
# 결과물: dist/BunnyFruitFrenzy.app
```

### Windows (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name BunnyFruitFrenzy bunny_fruit_frenzy.py
# 결과물: dist/BunnyFruitFrenzy.exe
```

### Linux (단일 실행 파일)

```bash
pip install pyinstaller
pyinstaller --onefile --name BunnyFruitFrenzy bunny_fruit_frenzy.py
```

## 📁 프로젝트 구조

```
BunnyFruitFrenzy/
├── bunny_fruit_frenzy.py     # 메인 게임 코드
├── BunnyFruitFrenzy.spec     # PyInstaller 빌드 스펙
├── requirements.txt          # Python 의존성
├── README.md                 # 이 파일
├── LICENSE                   # MIT 라이선스
└── .gitignore
```

## 💾 데이터 저장 위치

최고 기록은 다음 위치에 저장됩니다:

- **macOS**: `~/Library/Application Support/BunnyFruitFrenzy/highscore.json`
- **Windows**: `%APPDATA%\BunnyFruitFrenzy\highscore.json`
- **Linux**: `~/.local/share/BunnyFruitFrenzy/highscore.json`

기록을 초기화하려면 위 파일을 삭제하면 됩니다.

## 🛠️ 의존성

- Python 3.9+
- pygame ≥ 2.0
- numpy ≥ 1.20

## 📜 라이선스

MIT License — 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 🙌 크레딧

만든 사람: Saiah Lee, Rowan Asher Lee, and Sharon Esther Lee
모든 그래픽과 사운드는 코드로 절차적 생성됩니다 (외부 에셋 없음).
