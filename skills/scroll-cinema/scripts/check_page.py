#!/usr/bin/env python3
"""
check_page.py — QA for scroll-cinema pages.

Renders the page in Chromium at several viewports, in motion mode (WebGL) and
static mode (WebGL disabled), scrubs through the timeline, and reports:
  * JavaScript errors and failed requests
  * fixed UI layers that overlap each other (header, opening headline, HUD, rail)
  * text that is visible on top of the static article in static mode
  * whether each stage card actually appears
Screenshots go to --out so a human can look at every state.

Usage:
  python3 check_page.py page.html --out /tmp/qa [--three-js /path/three.min.js]

--three-js serves a local copy of three.min.js when the sandbox cannot reach
cdnjs. Exit code 1 when any check fails.
"""
import argparse, json, os, sys, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--out", default="qa")
    ap.add_argument("--three-js", default=None)
    ap.add_argument("--modes", default="motion,static", help="comma list: motion,static")
    ap.add_argument("--viewports", default="desktop,short,mobile", help="comma list: desktop,short,mobile")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed: pip install playwright --break-system-packages"); sys.exit(2)
    if os.path.isdir("/opt/pw-browsers") and not os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/pw-browsers"

    page_url = pathlib.Path(args.page).resolve().as_uri()
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
    three_bytes = pathlib.Path(args.three_js).read_bytes() if args.three_js else None

    VIEWPORTS = [v for v in [("desktop", 1440, 900), ("short", 1200, 630), ("mobile", 390, 844)] if v[0] in args.viewports.split(",")]
    failures, report = [], []

    OVERLAP_JS = """
    () => {
      const vis = el => { if(!el) return null; const s=getComputedStyle(el);
        if(s.display==='none'||s.visibility==='hidden') return null;
        let op=1; for(let a=el; a && a.nodeType===1; a=a.parentElement){ op*=parseFloat(getComputedStyle(a).opacity); }
        if(op<0.15) return null;
        const r=el.getBoundingClientRect(); return (r.width>2&&r.height>2)?r:null; };
      const boxes = {
        header: vis(document.querySelector('header .controls')),
        brand: vis(document.querySelector('header .brand')),
        headline: vis(document.querySelector('#opening h1')),
        lede: vis(document.querySelector('#opening p')),
        card: vis(document.querySelector('#cards .on')),
        panel: vis(document.querySelector('#panels .on')),
        rail: vis(document.querySelector('#rail')),
      };
      const hits=[]; const k=Object.keys(boxes);
      for(let i=0;i<k.length;i++) for(let j=i+1;j<k.length;j++){
        const a=boxes[k[i]], b=boxes[k[j]]; if(!a||!b) continue;
        const ix=Math.min(a.right,b.right)-Math.max(a.left,b.left), iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
        if(ix>4&&iy>4) hits.push(k[i]+' x '+k[j]+' ('+Math.round(ix)+'x'+Math.round(iy)+'px)');
      }
      const offscreen=[]; for(const n of k){ const r=boxes[n]; if(r && (r.left<-2||r.right>innerWidth+2||r.bottom>innerHeight+2)) offscreen.push(n); }
      return {hits, offscreen, isStatic: document.documentElement.classList.contains('static'),
              cardText: (document.querySelector('#cards .on h2')||{}).textContent||null};
    }"""

    with sync_playwright() as pw:
        for mode in [m for m in ("motion", "static") if m in args.modes.split(",")]:
            gl_args = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] if mode == "motion" else ["--disable-webgl", "--disable-3d-apis"]
            browser = pw.chromium.launch(args=gl_args)
            for name, w, h in VIEWPORTS:
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="no-preference")
                pg = ctx.new_page()
                errors = []
                pg.on("pageerror", lambda e, errors=errors: errors.append("pageerror: " + str(e)))
                pg.on("console", lambda m, errors=errors: errors.append("console: " + m.text) if m.type == "error" else None)
                if three_bytes:
                    pg.route("**/three.min.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=three_bytes))
                pg.route("**/fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=""))
                pg.goto(page_url, wait_until="load")
                pg.wait_for_timeout(600)
                tag = f"{mode}-{name}"
                states = []
                if mode == "motion":
                    # stop autoplay, then scrub to the opening and to the middle of every stage
                    pg.evaluate("() => window.__goManual && window.__goManual()")
                    n = pg.evaluate("() => document.querySelectorAll('#cards .card').length")
                    stops = [("opening", 0.0)]
                    p0 = 0.05
                    for i in range(n):
                        stops.append((f"stage{i+1:02d}", p0 + (1 - p0) / n * (i + 0.6)))
                    pg.wait_for_timeout(700)  # let a delayed autoplay start, then take over like a reader would
                    for label, p in stops:
                        pg.evaluate("() => window.__goManual && window.__goManual()")
                        pg.evaluate(f"() => window.scrollTo(0, {p} * (document.getElementById('track').offsetHeight - innerHeight))")
                        pg.wait_for_timeout(1400)
                        res = pg.evaluate(OVERLAP_JS)
                        pg.screenshot(path=str(out / f"{tag}-{label}.png"))
                        states.append((label, res))
                        if res["isStatic"]:
                            failures.append(f"{tag}: fell back to static mode although WebGL was available")
                            break
                        if label.startswith("stage") and not res["cardText"]:
                            failures.append(f"{tag}/{label}: no stage card visible")
                    if name == "desktop" and pg.evaluate("() => !!window.__cinema") and n >= 3:
                        # 1. resize mid-journey keeps the exact stage
                        pg.evaluate("() => { window.__cinema.goManual(); window.scrollTo(0, window.__cinema.stageArrive(2) * (document.getElementById('track').offsetHeight - innerHeight)); }")
                        pg.wait_for_timeout(900)
                        before = pg.evaluate("() => window.__cinema.state().stage")
                        pg.set_viewport_size({"width": 1024, "height": 700}); pg.wait_for_timeout(900)
                        after = pg.evaluate("() => window.__cinema.state().stage")
                        pg.set_viewport_size({"width": w, "height": h})
                        if before != after:
                            failures.append(f"{tag}: resize moved the story from stage {before+1} to stage {after+1}")
                        # 2. deep link opens on its stage without autoplay
                        pg.goto(page_url + "#stage-3", wait_until="load"); pg.wait_for_timeout(1500)
                        st = pg.evaluate("() => window.__cinema.state()")
                        if st["stage"] != 2 or st["mode"] != "manual":
                            failures.append(f"{tag}: #stage-3 opened at stage {st['stage']+1} in {st['mode']} mode")
                        # 3. injected scene failure must land in static mode
                        pg.goto(page_url + "?fail=scene", wait_until="load"); pg.wait_for_timeout(500)
                        if not pg.evaluate("() => document.documentElement.classList.contains('static')"):
                            failures.append(f"{tag}: ?fail=scene did not switch to static mode")
                        pg.screenshot(path=str(out / f"{tag}-injected-failure.png"))
                    elif name == "desktop":
                        report.append({"run": tag, "note": "no window.__cinema hook: resize, deep-link and failure-injection checks skipped"})
                else:
                    # frame-sequence pages do not need WebGL, so test their static path with ?static=1
                    if pg.evaluate("() => !!(window.__cinema && window.__cinema.state().sceneMode === 'frames' && !window.__cinema.state().isStatic)"):
                        pg.goto(page_url + "?static=1", wait_until="load"); pg.wait_for_timeout(500)
                    res = pg.evaluate(OVERLAP_JS)
                    pg.screenshot(path=str(out / f"{tag}.png"), full_page=True)
                    states.append(("article", res))
                    if not res["isStatic"]:
                        failures.append(f"{tag}: WebGL disabled but page did not switch to static mode")
                    fixed_left = pg.evaluate("""() => [...document.querySelectorAll('#opening,#hud,#rail,#ctrl,#fallback,#topbar')]
                        .filter(e => { const s=getComputedStyle(e); return s.display!=='none' && s.visibility!=='hidden' && parseFloat(s.opacity)>0.1; })
                        .map(e => '#'+e.id)""")
                    if fixed_left:
                        failures.append(f"{tag}: motion layers still visible in static mode: {fixed_left}")
                for label, res in states:
                    for hit in res["hits"]:
                        failures.append(f"{tag}/{label}: overlap {hit}")
                    for o in res["offscreen"]:
                        failures.append(f"{tag}/{label}: '{o}' runs off screen")
                real_errors = [e for e in errors if "favicon" not in e]
                for e in real_errors:
                    failures.append(f"{tag}: {e}")
                report.append({"run": tag, "states": [{"at": l, **r} for l, r in states], "errors": real_errors})
                ctx.close()
            browser.close()

    (out / "report.json").write_text(json.dumps(report, indent=1))
    print(f"screenshots + report.json in {out}")
    if failures:
        print("\nFAIL")
        for f in dict.fromkeys(failures):
            print("  -", f)
        sys.exit(1)
    print("PASS: no overlaps, no errors, static fallback clean")

if __name__ == "__main__":
    main()
