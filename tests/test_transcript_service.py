import pytest

from transcript_service import (
    TranscriptError,
    _extract_lines_from_transcript_xml,
    _select_english_track,
    extract_video_id,
)


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/shorts/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
    ],
)
def test_extract_video_id_success(value, expected):
    assert extract_video_id(value) == expected


@pytest.mark.parametrize('value', ['', 'abc', 'https://example.com/video'])
def test_extract_video_id_failure(value):
    with pytest.raises(TranscriptError):
        extract_video_id(value)


def test_select_english_track_prefers_manual():
    tracks = [
        {'languageCode': 'en', 'kind': 'asr', 'baseUrl': 'auto'},
        {'languageCode': 'en', 'baseUrl': 'manual'},
    ]
    selected = _select_english_track(tracks)
    assert selected['baseUrl'] == 'manual'


def test_extract_lines_from_transcript_xml():
    xml = '<transcript><text>hello &amp; welcome</text><text>\nsecond line\n</text></transcript>'
    assert _extract_lines_from_transcript_xml(xml) == ['hello & welcome', 'second line']
