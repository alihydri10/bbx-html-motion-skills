#!/usr/bin/env python3
"""
make_frames.py — turn one or more video shots into a WebP frame sequence for
CONFIG.sceneMode = "frames".

  python3 make_frames.py shot1.mp4 shot2.mp4 --out frames --fps 12 --width 1600 --mobile-width 900

Writes frames/desktop/f_0001.webp ..., frames/mobile/f_0001.webp ..., and
frames/manifest.json with the frame count, the index where each shot starts
(use these to set each stage's scene.frame), and the total size. Shots are
concatenated in the order given, so render or generate them as one continuous
camera move (last frame of a shot = first frame of the next).

Size guide: 12 fps is enough for slow cinematic moves under scroll; total
desktop weight should stay under ~6 MB and mobile under ~3 MB. Lower --fps or
--quality before lowering --width.
"""
import argparse, json, pathlib, subprocess, sys

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)

def extract(shots, outdir, fps, width, quality):
    outdir.mkdir(parents=True, exist_ok=True)
    starts, n = [], 0
    for shot in shots:
        tmp = outdir / "_tmp"; tmp.mkdir(exist_ok=True)
        for f in tmp.glob("*.webp"): f.unlink()
        run(["ffmpeg", "-loglevel", "error", "-i", str(shot), "-vf", f"fps={fps},scale={width}:-2:flags=lanczos",
             "-c:v", "libwebp", "-quality", str(quality), "-compression_level", "6", str(tmp / "t_%05d.webp")])
        frames = sorted(tmp.glob("t_*.webp"))
        starts.append(n)
        for f in frames:
            n += 1; f.rename(outdir / f"f_{n:04d}.webp")
        tmp.rmdir()
    size = sum(f.stat().st_size for f in outdir.glob("f_*.webp"))
    return n, starts, size

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--out", default="frames")
    ap.add_argument("--fps", type=float, default=12)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--mobile-width", type=int, default=900)
    ap.add_argument("--quality", type=int, default=72)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    n, starts, size = extract(a.shots, out / "desktop", a.fps, a.width, a.quality)
    m, _, msize = extract(a.shots, out / "mobile", a.fps, a.mobile_width, a.quality - 4)
    manifest = {"frames": n, "fps": a.fps, "shot_start_index": starts,
                "shot_start_frame_value": [round(s / max(n - 1, 1), 4) for s in starts],
                "desktop_bytes": size, "mobile_bytes": msize}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))
    if size > 6_000_000: print("WARNING: desktop sequence over 6 MB; lower --fps or --quality")
    if msize > 3_000_000: print("WARNING: mobile sequence over 3 MB")

if __name__ == "__main__":
    main()
