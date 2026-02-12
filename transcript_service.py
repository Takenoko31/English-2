import html
import json
import re
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree


class TranscriptError(Exception):
    """Raised when transcript extraction fails."""


def extract_video_id(url_or_id: str) -> str:
    if not url_or_id:
        raise TranscriptError('YouTubeのURLまたは動画IDを入力してください。')

    value = url_or_id.strip()

    if len(value) == 11 and '/' not in value and '?' not in value:
        return value

    parsed = urlparse(value)

    if parsed.netloc in {'youtu.be', 'www.youtu.be'}:
        video_id = parsed.path.strip('/')
        if video_id:
            return video_id

    if 'youtube.com' in parsed.netloc or 'youtube-nocookie.com' in parsed.netloc:
        if parsed.path == '/watch':
            query = parse_qs(parsed.query)
            video_id = query.get('v', [None])[0]
            if video_id:
                return video_id

        if parsed.path.startswith('/shorts/') or parsed.path.startswith('/embed/'):
            parts = [segment for segment in parsed.path.split('/') if segment]
            if len(parts) >= 2:
                return parts[1]

    raise TranscriptError('有効なYouTube動画URLまたは11文字の動画IDを入力してください。')


def fetch_english_transcript(video_id: str) -> str:
    page_html = _download_text(f'https://www.youtube.com/watch?v={video_id}&hl=en')
    player_response = _extract_player_response_json(page_html)

    captions = (
        player_response.get('captions', {})
        .get('playerCaptionsTracklistRenderer', {})
        .get('captionTracks', [])
    )

    if not captions:
        raise TranscriptError('この動画には英語字幕が見つかりませんでした。')

    track = _select_english_track(captions)
    if not track:
        raise TranscriptError('この動画には英語字幕が見つかりませんでした。')

    transcript_xml = _download_text(_with_query(track['baseUrl'], fmt='srv3'))
    lines = _extract_lines_from_transcript_xml(transcript_xml)

    if not lines:
        raise TranscriptError('字幕は取得できましたが、内容が空でした。')

    return '\n'.join(lines)


def _download_text(url: str) -> str:
    request = Request(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            )
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as exc:  # noqa: BLE001
        raise TranscriptError(f'字幕の取得中に通信エラーが発生しました: {exc}') from exc


def _extract_player_response_json(page_html: str) -> dict:
    marker = 'ytInitialPlayerResponse'
    idx = page_html.find(marker)
    if idx == -1:
        raise TranscriptError('動画情報を取得できませんでした。')

    start = page_html.find('{', idx)
    if start == -1:
        raise TranscriptError('動画情報を解析できませんでした。')

    depth = 0
    in_string = False
    escape = False

    for pos in range(start, len(page_html)):
        ch = page_html[pos]

        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                blob = page_html[start : pos + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError as exc:
                    raise TranscriptError('動画情報のJSON解析に失敗しました。') from exc

    raise TranscriptError('動画情報を最後まで解析できませんでした。')


def _select_english_track(caption_tracks: list[dict]) -> dict | None:
    english = [
        track
        for track in caption_tracks
        if str(track.get('languageCode', '')).lower().startswith('en')
    ]

    if not english:
        return None

    manual = [track for track in english if track.get('kind') != 'asr']
    return manual[0] if manual else english[0]


def _with_query(url: str, **params: str) -> str:
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}{urlencode(params)}"


def _extract_lines_from_transcript_xml(xml_text: str) -> list[str]:
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        raise TranscriptError('字幕データの解析に失敗しました。') from exc

    lines = []
    for node in root.findall('text'):
        text = ''.join(node.itertext())
        cleaned = _normalize_text(text)
        if cleaned:
            lines.append(cleaned)
    return lines


def _normalize_text(text: str) -> str:
    decoded = html.unescape(text)
    decoded = re.sub(r'\s+', ' ', decoded)
    return decoded.strip()
