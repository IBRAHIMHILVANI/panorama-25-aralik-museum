"""Loopback-only deterministic WebCodecs Annex-B export and verified MP4 remux.

Run from any directory: python3 scripts/serve_tour_frames.py
The API accepts no paths. Generated files never replace earlier recordings.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import shutil
import subprocess
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/Gaziantep-Museum-2026-10-25/video/smooth-export'
ROUTE = ROOT / 'reconstruction/full-tour-path-2026-10-26.json'
PORT = 8768
ORIGIN = f'http://127.0.0.1:{PORT}'
CODECS = {'avc1.42001f', 'avc1.42e01f', 'avc1.64001f'}
MAX_CHUNK = 16 * 1024 * 1024
MAX_TOTAL = 2 * 1024 ** 3
MAX_JSON = 32768
records = {}
lock = threading.RLock()
FFMPEG = shutil.which('ffmpeg')
FFPROBE = shutil.which('ffprobe')


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def require(condition, status, message):
    if not condition:
        raise ApiError(status, message)


def sha_file(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def timing_hash(count):
    # Exact positive-integer equivalent of JS Math.round(i * 1000000 / 30).
    canonical = ''.join(f'{(i * 1000000 + 15) // 30}\n' for i in range(count))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


def public(record):
    return {key: value for key, value in record.items()
            if key not in {'handle', 'chunks_meta', 'finish_request_digest'}}


def persist(record):
    destination = OUT / (record['stem'] + '.recording.json')
    temporary = destination.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(public(record), ensure_ascii=False, indent=2))
    temporary.replace(destination)


def validate_start(data):
    allowed = {'route_sha256', 'fps', 'width', 'height', 'total_frames',
               'duration_seconds', 'codec', 'mode', 'speed'}
    require(set(data) == allowed, 400, 'Unexpected or missing start fields.')
    require(data['mode'] in {'pilot', 'full'}, 400, 'Mode must be pilot or full.')
    require(data['codec'] in CODECS, 400, 'Unsupported exact AVC codec.')
    require(numeric(data['speed']) and data['speed'] == 1.5, 400, 'Export speed must be exactly 1.5.')
    require(all(type(data[key]) is int and data[key] == value
                for key, value in [('fps', 30), ('width', 1280), ('height', 720)]),
            400, 'Export format must be 1280x720 at 30 fps.')
    raw = ROUTE.read_bytes()
    route = json.loads(raw)
    require(data['route_sha256'] == hashlib.sha256(raw).hexdigest(),
            409, 'Route changed; reload the current validated path.')
    require(route.get('continuous') is True and route.get('validation', {}).get('passed') is True,
            409, 'Route validation is not successful.')
    for index in range(9):
        part = f'part0{index}'
        require(sha_file(ROOT / f'review/walkthrough/{part}.glb') ==
                route['validation']['glb_sha256'].get(part),
                409, f'{part} changed after route validation.')
    duration = 20.0 if data['mode'] == 'pilot' else route['duration_seconds'] / 1.5
    count = 600 if data['mode'] == 'pilot' else math.ceil(duration * 30) + 1
    require(type(data['total_frames']) is int and data['total_frames'] == count,
            400, f'Expected exactly {count} frames for this mode.')
    require(numeric(data['duration_seconds']) and abs(data['duration_seconds'] - duration) < 1e-6,
            400, f'Expected segment duration {duration}.')
    source_end = 30.0 if data['mode'] == 'pilot' else route['duration_seconds']
    return duration, count, source_end


def verify_and_remux(record):
    raw_path = Path(record['raw_path'])
    temporary = OUT / (record['stem'] + '.remux.partial.mp4')
    final_path = OUT / (record['stem'] + '.mp4')
    result = subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
         '-r', '30', '-i', str(raw_path), '-map', '0:v:0', '-c:v', 'copy',
         '-movflags', '+faststart', str(temporary)],
        capture_output=True, text=True, timeout=180)
    require(result.returncode == 0, 422,
            'H.264 remux failed: ' + result.stderr[-1800:])
    probe = subprocess.run(
        [FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-count_frames',
         '-show_frames', '-show_entries',
         'stream=codec_name,codec_tag_string,profile,has_b_frames,width,height,nb_read_frames,r_frame_rate,avg_frame_rate,duration:format=duration:frame=best_effort_timestamp_time',
         '-of', 'json', str(temporary)],
        capture_output=True, text=True, timeout=240)
    require(probe.returncode == 0, 422, 'Video verification failed: ' + probe.stderr[-1800:])
    info = json.loads(probe.stdout)
    streams = info.get('streams', [])
    require(len(streams) == 1, 422, 'Expected exactly one video stream.')
    stream = streams[0]
    count = record['request']['total_frames']
    decoded = int(stream.get('nb_read_frames', '-1'))
    require(stream.get('codec_name') == 'h264' and stream.get('has_b_frames', 0) == 0,
            422, 'Expected H.264 without reordered B frames.')
    require((stream.get('width'), stream.get('height')) == (1280, 720),
            422, 'Encoded dimensions do not match the export request.')
    require(decoded == count, 422, f'Decoded frame count {decoded} does not match {count}.')
    duration = float(info.get('format', {}).get('duration', stream.get('duration', 0)))
    expected_duration = count / 30
    require(abs(duration - expected_duration) <= 1 / 30 + .005,
            422, f'MP4 duration {duration} does not match frame duration {expected_duration}.')
    require(abs(float(Fraction(stream.get('avg_frame_rate', '0'))) - 30) < .001,
            422, 'MP4 is not 30 fps.')
    timestamps = [float(frame['best_effort_timestamp_time']) for frame in info.get('frames', [])
                  if 'best_effort_timestamp_time' in frame]
    require(len(timestamps) == count, 422, 'Missing decoded-frame timestamps.')
    max_error = max(abs(timestamp - i / 30) for i, timestamp in enumerate(timestamps))
    require(max_error <= .0001, 422, 'MP4 timestamps are not a uniform 30 fps timeline.')
    temporary.replace(final_path)
    return {
        'passed': True, 'decoded_frames': decoded, 'requested_frames': count,
        'width': stream['width'], 'height': stream['height'],
        'codec': stream['codec_name'], 'profile': stream.get('profile'),
        'has_b_frames': stream.get('has_b_frames'), 'fps': 30,
        'duration_seconds': duration, 'expected_video_duration_seconds': expected_duration,
        'maximum_frame_timestamp_error_seconds': max_error,
        'raw_h264_sha256': sha_file(raw_path), 'mp4_sha256': sha_file(final_path),
        'ffmpeg_command_uses_stream_copy': True,
        'content_uniqueness_checked': False,
    }, final_path


class Handler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def json_reply(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if status >= 400:
            self.close_connection = True
            self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{PORT}'

    def translate_path(self, path):
        candidate = Path(super().translate_path(path)).resolve()
        # SimpleHTTPRequestHandler otherwise follows symlinks outside its root.
        return str(candidate if candidate.is_relative_to(ROOT) else ROOT / '__blocked_external_path__')

    def do_GET(self):
        if not self.valid_host():
            self.json_reply(403, {'error': 'Invalid local Host.'})
            return
        parsed = urlparse(self.path)
        if parsed.path == '/__frames/status':
            query = parse_qs(parsed.query)
            with lock:
                sid = query.get('sessionId', [None])[0]
                rows = [public(record) for record in records.values()
                        if sid is None or record['sessionId'] == sid]
                active = next((r['sessionId'] for r in records.values()
                               if r['state'] in {'receiving', 'finalizing'}), None)
            self.json_reply(200 if rows or sid is None else 404,
                            {'exports': rows, 'active_session': active})
            return
        super().do_GET()

    def do_HEAD(self):
        if not self.valid_host():
            self.send_error(403)
            return
        super().do_HEAD()

    def do_POST(self):
        try:
            require(self.valid_host() and self.headers.get('Origin') == ORIGIN,
                    403, 'Export requests require the exact local viewer Origin and Host.')
            parsed = urlparse(self.path)
            require(parsed.path in {'/__frames/start', '/__frames/chunk', '/__frames/finish', '/__frames/abort'},
                    404, 'Unknown endpoint.')
            require(not self.headers.get('Transfer-Encoding'), 400, 'Content-Length is required.')
            length = int(self.headers.get('Content-Length', '0'))
            maximum = MAX_CHUNK if parsed.path.endswith('/chunk') else MAX_JSON
            require(0 < length <= maximum, 413, 'Invalid or oversized payload.')
            body = self.rfile.read(length)
            require(len(body) == length, 400, 'Incomplete request body.')
            if parsed.path.endswith('/chunk'):
                self.chunk(parsed, body)
                return
            data = json.loads(body)
            require(type(data) is dict, 400, 'Expected a JSON object.')
            if parsed.path.endswith('/start'):
                self.start(data)
            elif parsed.path.endswith('/abort'):
                self.abort(data)
            else:
                self.finish(data)
        except ApiError as error:
            self.json_reply(error.status, {'error': str(error)})
        except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as error:
            self.json_reply(400, {'error': str(error)[:500]})

    def start(self, data):
        duration, count, source_end = validate_start(data)
        with lock:
            require(not any(r['state'] in {'receiving', 'finalizing'} for r in records.values()),
                    409, 'An export is already active.')
            sid = uuid.uuid4().hex
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            stem = f'Gaziantep_Smooth_1p5x_{data["mode"]}_{stamp}_{sid[:12]}'
            partial = OUT / (stem + '.h264.partial')
            record = {
                'sessionId': sid, 'state': 'receiving', 'stem': stem,
                'request': data, 'raw_path': str(partial), 'bytes': 0,
                'chunks': 0, 'started_at': time.time(), 'updated_at': time.time(),
                'expected_timing_sha256': timing_hash(count),
                'expected_segment_start_seconds': 0,
                'expected_segment_end_seconds': source_end,
                'video_duration_seconds': duration, 'source_playback_speed': 1.5,
                'handle': partial.open('xb'), 'chunks_meta': {},
            }
            records[sid] = record
            persist(record)
        self.json_reply(200, {'sessionId': sid, 'max_chunk_bytes': MAX_CHUNK,
                              'expected_frame_timing_sha256': record['expected_timing_sha256']})

    def chunk(self, parsed, body):
        query = parse_qs(parsed.query, strict_parsing=True)
        require(set(query) == {'sessionId', 'index'} and all(len(v) == 1 for v in query.values()),
                400, 'Expected sessionId and index only.')
        sid = query['sessionId'][0]
        index = int(query['index'][0])
        digest = hashlib.sha256(body).hexdigest()
        with lock:
            record = records.get(sid)
            require(record is not None and record['state'] == 'receiving', 409, 'No receiving export session.')
            if index < record['chunks']:
                require(record['chunks_meta'].get(index) == [len(body), digest],
                        409, 'Conflicting duplicate chunk.')
                self.json_reply(200, {'duplicate': True, 'chunks': record['chunks'], 'bytes': record['bytes']})
                return
            require(index == record['chunks'], 409, f'Expected chunk index {record["chunks"]}.')
            require(record['bytes'] + len(body) <= MAX_TOTAL, 413, 'Total export byte limit exceeded.')
            if index == 0:
                require(body.startswith(b'\x00\x00\x00\x01') or body.startswith(b'\x00\x00\x01'),
                        422, 'First chunk must contain Annex-B start codes, not AVC length prefixes.')
            record['handle'].write(body)
            record['handle'].flush()
            record['bytes'] += len(body)
            record['chunks'] += 1
            record['chunks_meta'][index] = [len(body), digest]
            record['updated_at'] = time.time()
            self.json_reply(200, {'chunks': record['chunks'], 'bytes': record['bytes']})

    def abort(self, data):
        require(set(data).issubset({'sessionId', 'reason'}) and 'sessionId' in data,
                400, 'Unexpected abort fields.')
        with lock:
            record = records.get(data['sessionId'])
            require(record is not None, 409, 'Unknown export session.')
            if record['state'] == 'aborted':
                self.json_reply(200, {'aborted': True, 'sessionId': record['sessionId']})
                return
            require(record['state'] == 'receiving', 409, 'Export is not receiving; inspect status.')
            record.pop('handle').close()
            record.update(state='aborted', complete=False, completed_route=False,
                          abort_reason=str(data.get('reason', 'client abort'))[:500], finished_at=time.time())
            persist(record)
        self.json_reply(200, {'aborted': True, 'sessionId': record['sessionId']})

    def finish(self, data):
        allowed = {'sessionId', 'chunks', 'frames_rendered', 'frames_encoded',
                   'completed_route', 'frame_timing_sha256', 'elapsed_wall_seconds',
                   'start_seconds', 'end_seconds'}
        require(set(data) == allowed, 400, 'Unexpected or missing finish fields.')
        finish_digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        with lock:
            record = records.get(data['sessionId'])
            require(record is not None, 409, 'Unknown export session.')
            if record['state'] == 'complete':
                require(record['finish_request_digest'] == finish_digest, 409, 'Conflicting finish retry.')
                self.json_reply(200, record['result'])
                return
            require(record['state'] == 'receiving', 409, 'Export is not receiving.')
            count = record['request']['total_frames']
            require(type(data['chunks']) is int and data['chunks'] == record['chunks'] and record['chunks'] > 0,
                    409, 'Chunk count mismatch or no uploaded chunks.')
            require(all(type(data[key]) is int and data[key] == count
                        for key in ['frames_rendered', 'frames_encoded']), 409, 'Client frame counts do not match request.')
            require(type(data['completed_route']) is bool, 400, 'completed_route must be boolean.')
            require(record['request']['mode'] != 'full' or data['completed_route'] is True,
                    409, 'Full export did not complete the route.')
            require(data['frame_timing_sha256'] == record['expected_timing_sha256'],
                    409, 'Frame timing hash does not match the exact 30 fps frame sequence.')
            require(numeric(data['elapsed_wall_seconds']) and data['elapsed_wall_seconds'] >= 0,
                    400, 'Invalid elapsed wall time.')
            require(numeric(data['start_seconds']) and abs(data['start_seconds']) < 1e-6,
                    400, 'Export must begin at route time zero.')
            require(numeric(data['end_seconds']) and
                    abs(data['end_seconds'] - record['expected_segment_end_seconds']) < 1e-6,
                    400, 'Segment end time does not match the requested mode.')
            require(sha_file(ROUTE) == record['request']['route_sha256'],
                    409, 'Route changed during export.')
            record.pop('handle').close()
            raw_path = OUT / (record['stem'] + '.h264')
            Path(record['raw_path']).rename(raw_path)
            record.update(state='finalizing', raw_path=str(raw_path), client_metadata=data,
                          finish_request_digest=finish_digest, finalization_started_at=time.time())
            persist(record)
        try:
            verification, final_path = verify_and_remux(record)
            with lock:
                result = {
                    'sessionId': record['sessionId'], 'complete': True,
                    'completed_route': record['request']['mode'] == 'full',
                    'mode': record['request']['mode'], 'path': str(final_path),
                    'url': '/' + str(final_path.relative_to(ROOT)),
                    'raw_path': str(raw_path), 'metadata_path': str(OUT / (record['stem'] + '.recording.json')),
                    'frames': verification['decoded_frames'], 'duration_seconds': verification['duration_seconds'],
                    'verification': verification,
                }
                record.update(state='complete', complete=True, completed_route=result['completed_route'],
                              result=result, verification=verification, finished_at=time.time())
                persist(record)
            self.json_reply(200, result)
        except Exception as error:
            with lock:
                record.update(state='failed', complete=False, completed_route=False,
                              error=str(error)[:2000], finished_at=time.time())
                persist(record)
            self.json_reply(error.status if isinstance(error, ApiError) else 500,
                            {'error': str(error)[:2000], 'sessionId': record['sessionId'],
                             'raw_path': str(raw_path), 'complete': False})

    def log_message(self, fmt, *args):
        if '/__frames/chunk' not in str(args):
            super().log_message(fmt, *args)


def main():
    if not FFMPEG or not FFPROBE:
        raise SystemExit('ffmpeg and ffprobe are required.')
    OUT.mkdir(parents=True, exist_ok=True)
    print('TOUR_FRAME_EXPORT_SERVER', ORIGIN, flush=True)
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with lock:
            for record in records.values():
                if record.get('handle'):
                    record.pop('handle').close()
                    record.update(state='interrupted', complete=False, completed_route=False)
                    persist(record)
        server.server_close()


if __name__ == '__main__':
    main()
