"""Protocol and actual decode/remux checks against the loopback frame server.

Creates clearly identified synthetic pilot fixtures, never a claimed museum tour.
"""
from pathlib import Path
import hashlib
import http.client
import json
import math
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'http://127.0.0.1:8768'
checks = []
fixture_results = []


def request(path, data=None, body=None, origin=ORIGIN, host=None, length=None):
    connection = http.client.HTTPConnection('127.0.0.1', 8768, timeout=300)
    headers = {'Origin': origin}
    if host:
        headers['Host'] = host
    if body is None and data is not None:
        body = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    if length is not None:
        headers['Content-Length'] = str(length)
    connection.request('GET' if data is None and body is None else 'POST', path, body, headers)
    response = connection.getresponse()
    payload = response.read()
    status = response.status
    connection.close()
    return status, json.loads(payload)


def check(name, expected, response):
    status, data = response
    checks.append({'test': name, 'passed': status == expected, 'status': status})
    assert status == expected, (name, expected, status, data)
    return data


def canonical(count):
    return hashlib.sha256(''.join(f'{(i*1000000+15)//30}\n' for i in range(count)).encode()).hexdigest()


raw = (ROOT/'reconstruction/full-tour-path-2026-10-26.json').read_bytes()
route = json.loads(raw)
start = {'route_sha256': hashlib.sha256(raw).hexdigest(), 'fps': 30,
         'width': 1280, 'height': 720, 'total_frames': 600,
         'duration_seconds': 20, 'codec': 'avc1.42001f', 'mode': 'pilot', 'speed': 1.5}

check('status', 200, request('/__frames/status'))
check('reject_foreign_origin', 403, request('/__frames/start', start, origin='https://example.com'))
check('reject_rebound_host', 403, request('/__frames/start', start, host='example.com:8768'))
check('reject_path_field', 400, request('/__frames/start', {**start, 'path': '/tmp/not-allowed'}))
check('reject_unapproved_codec', 400, request('/__frames/start', {**start, 'codec': 'vp09.00.10.08'}))
check('reject_wrong_speed', 400, request('/__frames/start', {**start, 'speed': 1}))
check('reject_wrong_fps', 400, request('/__frames/start', {**start, 'fps': 60}))
check('reject_stale_route', 409, request('/__frames/start', {**start, 'route_sha256': '0'*64}))
check('reject_wrong_pilot_frames', 400, request('/__frames/start', {**start, 'total_frames': 599}))
check('reject_oversized_chunk_header', 413, request('/__frames/chunk?sessionId=invalid&index=0', body=b'x', length=16*1024*1024+1))
check('reject_unknown_session', 409, request('/__frames/chunk?sessionId=invalid&index=0', body=b'\0\0\0\1abc'))

with tempfile.TemporaryDirectory(prefix='museum-frame-protocol-') as directory:
    fixture = Path(directory)/'synthetic.h264'
    def encode(count):
        subprocess.run(['/opt/homebrew/bin/ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-f', 'lavfi', '-i', 'color=c=gray:s=1280x720:r=30',
                        '-frames:v', str(count), '-c:v', 'libx264', '-preset', 'ultrafast',
                        '-tune', 'zerolatency', '-profile:v', 'baseline', '-pix_fmt', 'yuv420p',
                        '-bf', '0', '-g', '60', '-f', 'h264', str(fixture)], check=True)
        return fixture.read_bytes()
    video = encode(600)
    begun = check('valid_pilot_start', 200, request('/__frames/start', start))
    sid = begun['sessionId']
    assert begun['expected_frame_timing_sha256'] == canonical(600)
    check('reject_second_active_export', 409, request('/__frames/start', start))
    check('reject_out_of_order_chunk', 409, request(f'/__frames/chunk?sessionId={sid}&index=1', body=video[:30]))
    check('reject_non_annexb_first_chunk', 422, request(f'/__frames/chunk?sessionId={sid}&index=0', body=b'not an annex-b stream'))
    midpoint = len(video)//2
    check('upload_chunk_zero', 200, request(f'/__frames/chunk?sessionId={sid}&index=0', body=video[:midpoint]))
    duplicate = check('idempotent_chunk_retry', 200, request(f'/__frames/chunk?sessionId={sid}&index=0', body=video[:midpoint]))
    assert duplicate['duplicate'] and duplicate['chunks'] == 1
    check('reject_conflicting_duplicate', 409, request(f'/__frames/chunk?sessionId={sid}&index=0', body=video[:midpoint]+b'x'))
    check('upload_chunk_one', 200, request(f'/__frames/chunk?sessionId={sid}&index=1', body=video[midpoint:]))
    finish = {'sessionId': sid, 'chunks': 2, 'frames_rendered': 600, 'frames_encoded': 600,
              'completed_route': False, 'frame_timing_sha256': canonical(600),
              'elapsed_wall_seconds': 1.0, 'start_seconds': 0, 'end_seconds': 30}
    check('reject_finish_chunk_mismatch', 409, request('/__frames/finish', {**finish, 'chunks': 1}))
    check('reject_finish_frame_mismatch', 409, request('/__frames/finish', {**finish, 'frames_encoded': 599}))
    check('reject_finish_timing_hash', 409, request('/__frames/finish', {**finish, 'frame_timing_sha256': '0'*64}))
    check('reject_finish_source_end', 400, request('/__frames/finish', {**finish, 'end_seconds': 20}))
    result = check('remux_and_verify_600_real_decoded_frames', 200, request('/__frames/finish', finish))
    assert result['frames'] == 600 and abs(result['duration_seconds']-20) < .001
    assert result['verification']['maximum_frame_timestamp_error_seconds'] < .0001
    assert result['completed_route'] is False
    check('idempotent_finish_retry', 200, request('/__frames/finish', finish))
    check('reject_conflicting_finish_retry', 409, request('/__frames/finish', {**finish, 'elapsed_wall_seconds': 2}))
    metadata = Path(result['metadata_path'])
    content = json.loads(metadata.read_text())
    content['protocol_test_fixture'] = True
    content['fixture_description'] = 'Synthetic gray frames for server protocol/PTS tests; NOT museum footage.'
    metadata.write_text(json.dumps(content, indent=2))
    fixture_results.append(result)

    # Server must reject missing encoded pictures even when the client claims600.
    short_video = encode(1)
    sid = check('start_decode_count_negative_case', 200, request('/__frames/start', start))['sessionId']
    check('upload_one_frame_negative_case', 200, request(f'/__frames/chunk?sessionId={sid}&index=0', body=short_video))
    check('reject_actual_decoded_frame_shortfall', 422, request('/__frames/finish', {**finish, 'sessionId': sid, 'chunks': 1}))
    status = check('failed_session_status', 200, request(f'/__frames/status?sessionId={sid}'))
    assert status['exports'][0]['state'] == 'failed'

duration = route['duration_seconds']/1.5
full = {**start, 'mode': 'full', 'duration_seconds': duration, 'total_frames': math.ceil(duration*30)+1}
sid = check('valid_full_1p5x_contract', 200, request('/__frames/start', full))['sessionId']
check('abort_full_contract_fixture', 200, request('/__frames/abort', {'sessionId': sid, 'reason': 'Protocol test only; no museum frames uploaded.'}))
check('idempotent_abort', 200, request('/__frames/abort', {'sessionId': sid, 'reason': 'retry'}))
final_status = check('no_active_export_after_tests', 200, request('/__frames/status'))
assert final_status['active_session'] is None
report = {'passed': all(c['passed'] for c in checks), 'checks': checks,
          'test_count': len(checks), 'full_expected_frames': full['total_frames'],
          'full_expected_video_duration_seconds': duration, 'pilot_fixture_results': fixture_results,
          'generated_at_unix': time.time(), 'note': 'Synthetic protocol fixtures are not museum footage.'}
(ROOT/'review/qa/tour-frames-protocol-tests.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'passed': report['passed'], 'tests': len(checks),
                  'full_frames': full['total_frames'], 'pilot_frames_verified': 600}, indent=2))
