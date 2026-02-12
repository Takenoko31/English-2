import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps
from urllib.parse import parse_qs, urlparse

from transcript_service import TranscriptError, extract_video_id, fetch_english_transcript


class ApiHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == '/health':
            self._respond_json({'ok': True})
            return

        if parsed.path in {'/api/transcript', '/transcript'}:
            video_input = query.get('video', [''])[0].strip()
            if not video_input:
                video_input = query.get('video_id', [''])[0].strip()
            self._handle_transcript(video_input)
            return

        self._respond_json({'error': 'Not found'}, status=HTTPStatus.NOT_FOUND)

    def _handle_transcript(self, video_input: str):
        if not video_input:
            self._respond_json({'error': 'video パラメータを指定してください。'}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            video_id = extract_video_id(video_input)
            transcript = fetch_english_transcript(video_id)
        except TranscriptError as exc:
            self._respond_json({'error': str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._respond_json({'videoId': video_id, 'language': 'en', 'transcript': transcript})

    def _respond_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK):
        body = dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):  # noqa: A003
        return


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), ApiHandler)
    print(f'API server running on http://0.0.0.0:{port}')
    server.serve_forever()
