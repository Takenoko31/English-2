# YouTube English Transcript Extractor

指定したYouTube動画から **英語字幕（Transcript）** を抽出するシンプルなアプリです。

## Features

- YouTube URL または Video ID を入力して字幕を取得
- 対象言語は **英語のみ** (`en`)
- Transcript を画面表示
- `.txt` / `.srt` でダウンロード
- 以下のURL形式に対応
  - `https://www.youtube.com/watch?v=...`
  - `https://youtu.be/...`
  - `https://www.youtube.com/shorts/...`
  - `https://www.youtube.com/embed/...`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開いて使ってください。

## Notes

- 字幕が無効の動画や英語字幕がない動画では取得できません。
- `youtube-transcript-api` を利用しています。
