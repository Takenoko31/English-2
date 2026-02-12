from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from transcript_service import TranscriptError, extract_video_id, fetch_english_transcript

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / 'templates' / 'index.html'
STYLE_PATH = BASE_DIR / 'static' / 'style.css'


def render_page(*, transcript: str = '', error: str = '', video_url: str = '') -> str:
    template = TEMPLATE_PATH.read_text(encoding='utf-8')

    transcript_section = ''
    if transcript:
        transcript_section = (
            '<section class="card result">'
            '<h2>Transcript (English)</h2>'
            f'<textarea readonly>{escape_html(transcript)}</textarea>'
            '</section>'
        )

    error_section = ''
    if error:
        error_section = (
            '<section class="card error">'
            '<h2>エラー</h2>'
            f'<p>{escape_html(error)}</p>'
            '</section>'
        )

    return (
        template.replace('{{ video_url }}', escape_html(video_url))
        .replace('{{ error_section }}', error_section)
        .replace('{{ transcript_section }}', transcript_section)
    )


def escape_html(value: str) -> str:
    return (
        value.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;')
    )


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == '/':
            self.respond_html(render_page())
            return

        if self.path == '/static/style.css':
            self.respond_css(STYLE_PATH.read_text(encoding='utf-8'))
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):  # noqa: N802
        if self.path != '/':
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get('Content-Length', '0'))
        raw_body = self.rfile.read(length).decode('utf-8')
        form = parse_qs(raw_body)
        video_url = form.get('video_url', [''])[0].strip()

        transcript = ''
        error = ''

        try:
            video_id = extract_video_id(video_url)
            transcript = fetch_english_transcript(video_id)
        except TranscriptError as exc:
            error = str(exc)

        self.respond_html(render_page(transcript=transcript, error=error, video_url=video_url))

    def log_message(self, format, *args):  # noqa: A003
        return

    def respond_html(self, html: str):
        data = html.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def respond_css(self, css: str):
        data = css.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/css; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 5000), AppHandler)
    print('Server running on http://0.0.0.0:5000')
    server.serve_forever()
