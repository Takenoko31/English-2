import re
from urllib.parse import parse_qs, urlparse

import streamlit as st
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)


def extract_video_id(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower()

    if host in {"youtu.be", "www.youtu.be"}:
        candidate = parsed.path.lstrip("/").split("/")[0]
        return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else None

    if "youtube.com" in host:
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            candidate = query.get("v", [""])[0]
            return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else None

        if parsed.path.startswith("/shorts/"):
            candidate = parsed.path.split("/shorts/")[-1].split("/")[0]
            return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else None

        if parsed.path.startswith("/embed/"):
            candidate = parsed.path.split("/embed/")[-1].split("/")[0]
            return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else None

    return None


def get_english_transcript(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
    full_text = "\n".join(item["text"] for item in transcript)
    return transcript, full_text


def format_srt_time(seconds: float) -> str:
    millis = int(seconds * 1000)
    h, rem = divmod(millis, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def transcript_to_srt(transcript: list[dict]) -> str:
    lines = []
    for i, item in enumerate(transcript, 1):
        start = format_srt_time(item["start"])
        end = format_srt_time(item["start"] + item["duration"])
        lines.append(f"{i}\n{start} --> {end}\n{item['text']}\n")
    return "\n".join(lines)


st.set_page_config(page_title="YouTube English Transcript Extractor", page_icon="🎬")
st.title("🎬 YouTube English Transcript Extractor")
st.write("YouTube動画のURLまたはVideo IDを入力すると、英語字幕（Transcript）を抽出します。")

input_value = st.text_input("YouTube URL / Video ID", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Extract Transcript"):
    video_id = extract_video_id(input_value)

    if not video_id:
        st.error("有効なYouTube URLまたはVideo IDを入力してください。")
    else:
        try:
            transcript, full_text = get_english_transcript(video_id)
            st.success(f"英語字幕を取得しました（{len(transcript)} lines）。")

            st.subheader("Transcript (plain text)")
            st.text_area("", full_text, height=320)

            srt_text = transcript_to_srt(transcript)

            st.download_button(
                label="Download TXT",
                data=full_text,
                file_name=f"{video_id}_transcript_en.txt",
                mime="text/plain",
            )

            st.download_button(
                label="Download SRT",
                data=srt_text,
                file_name=f"{video_id}_transcript_en.srt",
                mime="application/x-subrip",
            )

        except NoTranscriptFound:
            st.error("この動画には英語字幕が見つかりませんでした。")
        except TranscriptsDisabled:
            st.error("この動画は字幕機能が無効です。")
        except VideoUnavailable:
            st.error("動画が利用できません。URLまたは公開状況を確認してください。")
        except Exception as e:
            st.error(f"取得中にエラーが発生しました: {e}")
