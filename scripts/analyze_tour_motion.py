"""Decode video and diagnose held images while the validated camera should move.

This is a content diagnostic, not an automatic judgment that a blank wall is a
freeze. Planned pauses and stationary camera poses are excluded. Synthetic
server protocol fixtures are refused. No renderer/server files are changed.
"""
from pathlib import Path
from bisect import bisect_right
from collections import Counter
from fractions import Fraction
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--route', type=Path, default=ROOT/'reconstruction/full-tour-path-2026-10-26.json')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--speed', type=float)
    parser.add_argument('--near-mad', type=float, default=.08, help='Mean grayscale difference,0–255 units.')
    parser.add_argument('--min-run-seconds', type=float, default=.15)
    args = parser.parse_args()
    video = args.video.resolve()
    if not video.is_file():
        raise SystemExit(f'Video not found: {video}')
    out = args.output_dir or ROOT/'review/qa/tour-motion'/video.stem
    out.mkdir(parents=True, exist_ok=True)
    metadata_file = video.with_suffix('.recording.json')
    metadata = json.loads(metadata_file.read_text()) if metadata_file.exists() else {}
    if metadata.get('protocol_test_fixture'):
        raise SystemExit('Refusing synthetic protocol-test fixture as museum footage.')
    route_bytes = args.route.read_bytes()
    route_hash = hashlib.sha256(route_bytes).hexdigest()
    expected_hash = metadata.get('request', {}).get('route_sha256')
    if expected_hash and expected_hash != route_hash:
        raise SystemExit('Video metadata refers to a different camera path; supply the matching --route.')
    route = json.loads(route_bytes)
    speed = args.speed or metadata.get('request', {}).get('speed', 1.5)
    if not math.isfinite(speed) or speed <= 0:
        raise SystemExit('Speed must be finite and positive.')
    source_start = metadata.get('client_metadata', {}).get('start_seconds', 0)
    samples = route['samples']
    sample_times = [sample['t'] for sample in samples]
    pauses = [(pause['start'], pause['end']) for pause in route.get('pauses', [])]

    probe = subprocess.run([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
        '-show_frames', '-show_entries',
        'stream=width,height,codec_name,nb_read_frames,avg_frame_rate,r_frame_rate:format=duration:frame=best_effort_timestamp_time',
        '-of', 'json', str(video)], capture_output=True, text=True, check=True)
    info = json.loads(probe.stdout)
    stream = info['streams'][0]
    fps = float(Fraction(stream['avg_frame_rate']))
    timestamps = [float(frame['best_effort_timestamp_time']) for frame in info.get('frames', [])
                  if 'best_effort_timestamp_time' in frame]
    expected_frames = metadata.get('request', {}).get('total_frames')
    pts_error = max((abs((value-timestamps[0])-i/fps) for i, value in enumerate(timestamps)), default=None)
    duration = float(info['format']['duration'])

    def pose(index):
        source_time = min(source_start+index/fps*speed, route['duration_seconds'])
        k = max(0, min(len(samples)-2, bisect_right(sample_times, source_time)-1))
        a, b = samples[k], samples[k+1]
        t = np.clip((source_time-a['t'])/(b['t']-a['t']), 0, 1)
        position = np.asarray(a['position'])*(1-t)+np.asarray(b['position'])*t
        target = np.asarray(a['look_target'])*(1-t)+np.asarray(b['look_target'])*t
        direction = target-position
        direction /= max(float(np.linalg.norm(direction)), 1e-12)
        return source_time, position, direction, a['stage']

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit('OpenCV could not open the video.')
    rows = []
    runs = []
    active = None
    previous_gray = previous_pose = None
    index = 0
    excluded = Counter()
    longest_near_run = 0.0
    all_near_runs = 0

    def end_run():
        nonlocal active, longest_near_run, all_near_runs
        if active is None:
            return
        length = (active['end_frame']-active['start_frame'])/fps
        longest_near_run = max(longest_near_run, length)
        all_near_runs += 1
        if length > args.min_run_seconds+1e-9:
            mean_edges = float(np.mean(active.pop('edge_fractions')))
            mean_texture = float(np.mean(active.pop('texture_stds')))
            low_texture = mean_edges < .01 and mean_texture < 12
            active.update(duration_seconds=length,
                          start_video_seconds=active['start_frame']/fps,
                          end_video_seconds=active['end_frame']/fps,
                          mean_thumbnail_mad=float(np.mean(active.pop('mads'))),
                          classification='low_texture_ambiguity' if low_texture else 'suspected_freeze' if length >= .5 else 'review_candidate',
                          automatic_failure=False,
                          explanation='Very low visual detail can stay nearly unchanged during genuine camera motion.' if low_texture else 'Camera motion was expected while decoded thumbnails remained nearly identical; inspect the saved frames.')
            active['stages'] = dict(active['stages'])
            runs.append(active)
        active = None

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), .6).astype(np.float32)
        current_pose = pose(index)
        if previous_gray is not None:
            source_time, position, direction, stage = current_pose
            previous_time, previous_position, previous_direction, _ = previous_pose
            translation = float(np.linalg.norm(position-previous_position))
            rotation = math.degrees(math.acos(float(np.clip(np.dot(direction, previous_direction), -1, 1))))
            planned = any(previous_time < stop and source_time >= start for start, stop in pauses)
            stationary = translation < .0001 and rotation < .02
            reason = 'planned_pause' if planned else 'stationary_pose' if stationary else ''
            if reason:
                excluded[reason] += 1
            difference = np.abs(blurred-previous_gray)
            mad = float(difference.mean())
            changed = float((difference > 1).mean())
            exact = bool(np.array_equal(blurred, previous_gray))
            near = mad <= args.near_mad and changed <= .001
            gx = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
            edge_fraction = float((cv2.magnitude(gx, gy) > 12).mean())
            texture_std = float(blurred.std())
            rows.append([index, index/fps, source_time, stage, translation, rotation,
                         mad, changed, exact, near, reason, edge_fraction, texture_std])
            if near and not reason:
                if active is None:
                    active = {'start_frame': index-1, 'end_frame': index,
                              'source_start_seconds': previous_time, 'source_end_seconds': source_time,
                              'camera_translation_m': 0.0, 'camera_rotation_degrees': 0.0,
                              'exact_thumbnail_intervals': 0, 'stages': Counter(),
                              'mads': [], 'edge_fractions': [], 'texture_stds': []}
                active['end_frame'] = index
                active['source_end_seconds'] = source_time
                active['camera_translation_m'] += translation
                active['camera_rotation_degrees'] += rotation
                active['exact_thumbnail_intervals'] += int(exact)
                active['stages'][stage] += 1
                active['mads'].append(mad)
                active['edge_fractions'].append(edge_fraction)
                active['texture_stds'].append(texture_std)
            else:
                end_run()
        previous_gray = blurred
        previous_pose = current_pose
        index += 1
    end_run()
    cap.release()

    columns = ['frame', 'video_seconds', 'source_seconds', 'stage', 'camera_translation_m',
               'camera_rotation_deg', 'thumbnail_mad_0_255', 'fraction_changed_gt1',
               'exact_thumbnail', 'near_thumbnail', 'excluded_reason', 'edge_fraction', 'texture_std']
    with (out/'frame-motion.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    # Three inspection sheets at most, each showing start/middle/end decoded frames.
    if runs:
        cap = cv2.VideoCapture(str(video))
        for number, run in enumerate(sorted(runs, key=lambda item: item['duration_seconds'], reverse=True)[:3]):
            tiles = []
            indices = [run['start_frame'], (run['start_frame']+run['end_frame'])//2, run['end_frame']]
            for frame_number in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ok, frame = cap.read()
                if not ok:
                    continue
                tile = cv2.resize(frame, (384, 216), interpolation=cv2.INTER_AREA)
                label = np.zeros((30, 384, 3), np.uint8)
                cv2.putText(label, f'frame {frame_number} / {frame_number/fps:.3f}s',
                            (9, 21), cv2.FONT_HERSHEY_SIMPLEX, .55, (235, 235, 235), 1, cv2.LINE_AA)
                tiles.append(np.vstack([tile, label]))
            if tiles:
                destination = out/f'candidate-{number+1}.jpg'
                cv2.imwrite(str(destination), np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 92])
                run['inspection_image'] = str(destination)
        cap.release()

    decoded_probe = int(stream.get('nb_read_frames', -1))
    technical_passed = (index == decoded_probe == len(timestamps) and
                        (expected_frames is None or index == expected_frames) and
                        abs(fps-30) < .001 and pts_error is not None and pts_error <= .0001 and
                        abs(duration-index/fps) < 1/fps+.005)
    moving_rows = [row for row in rows if not row[10]]
    report = {
        'analysis_completed': True, 'video': str(video), 'route_sha256': route_hash,
        'speed': speed, 'video_metadata_found': metadata_file.exists(),
        'technical': {'passed': technical_passed, 'opencv_decoded_frames': index,
                      'ffprobe_decoded_frames': decoded_probe, 'requested_frames': expected_frames,
                      'fps': fps, 'duration_seconds': duration,
                      'maximum_cfr_timestamp_error_seconds': pts_error},
        'content_diagnostic': {'status': 'review_required' if runs else 'no_freeze_candidates_detected',
                               'automatic_failure': False, 'candidate_count': len(runs),
                               'moving_frame_intervals': len(moving_rows), 'excluded_intervals': dict(excluded),
                               'moving_exact_thumbnail_intervals': sum(row[8] for row in moving_rows),
                               'moving_near_thumbnail_intervals': sum(row[9] for row in moving_rows),
                               'longest_near_static_run_seconds': longest_near_run,
                               'near_static_run_count_all_lengths': all_near_runs,
                               'minimum_moving_mad': min((row[6] for row in moving_rows), default=None),
                               'median_moving_mad': float(np.median([row[6] for row in moving_rows])) if moving_rows else None,
                               'candidates': runs},
        'method': {'thumbnail_size': [160, 90], 'gaussian_kernel': [3, 3],
                   'near_mad_threshold_0_255': args.near_mad, 'maximum_changed_fraction_gt1': .001,
                   'minimum_run_seconds_exclusive': args.min_run_seconds,
                   'stationary_translation_threshold_m': .0001, 'stationary_rotation_threshold_deg': .02,
                   'planned_source_pause_intervals_excluded': True,
                   'limitation': 'Low-detail walls and small image motions can produce near-identical thumbnails. Candidates require visual review; CFR and decoded count alone do not prove unique source images.'},
        'frame_metrics_csv': str(out/'frame-motion.csv'),
    }
    report_path = out/'report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'technical_passed': technical_passed, 'decoded_frames': index,
                      'fps': fps, 'duration_seconds': duration, 'content_status': report['content_diagnostic']['status'],
                      'candidate_count': len(runs), 'moving_exact_intervals': report['content_diagnostic']['moving_exact_thumbnail_intervals'],
                      'report': str(report_path)}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
