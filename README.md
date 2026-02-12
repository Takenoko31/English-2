# English YouTube Transcript Extractor

指定したYouTube動画から **英語字幕（en）のみ** を抽出するシンプルなWebアプリです。  
標準ライブラリだけで動くため、`Flask` などの追加依存は不要です。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> `requirements.txt` は最小構成（実質依存なし）です。

## 実行

```bash
python app.py
```

ブラウザで `http://localhost:5000` を開いて、YouTube URLまたは11文字の動画IDを入力してください。

## テスト

```bash
pip install pytest
pytest -q
```
