import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import app


def _start_server():
    server = ThreadingHTTPServer(('127.0.0.1', 0), app.ApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_health_endpoint():
    server, _ = _start_server()
    try:
        port = server.server_address[1]
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health') as resp:
            payload = json.loads(resp.read().decode('utf-8'))
            assert resp.status == 200
            assert payload['ok'] is True
    finally:
        server.shutdown()
        server.server_close()


def test_transcript_endpoint_success(monkeypatch):
    monkeypatch.setattr(app, 'extract_video_id', lambda x: 'dQw4w9WgXcQ')
    monkeypatch.setattr(app, 'fetch_english_transcript', lambda x: 'line1\nline2')

    server, _ = _start_server()
    try:
        port = server.server_address[1]
        url = f'http://127.0.0.1:{port}/api/transcript?video=test'
        with urllib.request.urlopen(url) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
            assert resp.status == 200
            assert payload['videoId'] == 'dQw4w9WgXcQ'
            assert payload['language'] == 'en'
            assert payload['transcript'] == 'line1\nline2'
    finally:
        server.shutdown()
        server.server_close()


def test_transcript_endpoint_legacy_path_and_video_id(monkeypatch):
    monkeypatch.setattr(app, 'extract_video_id', lambda x: 'dQw4w9WgXcQ')
    monkeypatch.setattr(app, 'fetch_english_transcript', lambda x: 'line1\nline2')

    server, _ = _start_server()
    try:
        port = server.server_address[1]
        url = f'http://127.0.0.1:{port}/transcript?video_id=test'
        with urllib.request.urlopen(url) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
            assert resp.status == 200
            assert payload['videoId'] == 'dQw4w9WgXcQ'
            assert payload['language'] == 'en'
            assert payload['transcript'] == 'line1\nline2'
    finally:
        server.shutdown()
        server.server_close()
