# English YouTube Transcript Extractor

指定したYouTube動画から **英語字幕（en）のみ** を抽出するアプリです。  
構成を **GitHub Pages向け静的フロント + APIバックエンド** に分離しています。

## 構成

- `docs/`: GitHub Pagesに配置する静的フロント（HTML/CSS/JS）
- `app.py`: APIサーバー（標準ライブラリのみ）
- `transcript_service.py`: YouTube URL解析と英語字幕取得ロジック

## APIバックエンド起動

```bash
python app.py
```

起動後:
- `GET /health`
- `GET /api/transcript?video=<YouTube URL or ID>`

## フロントエンド起動（ローカル確認）

```bash
python -m http.server 8000 -d docs
```

ブラウザで `http://localhost:8000` を開き、`API Base URL` に `http://localhost:5000` を指定してください。

## GitHub Pages公開

`docs/` を Pages 配信対象に設定してください（branch + `/docs`）。

## テスト

```bash
pip install pytest
pytest -q
```
