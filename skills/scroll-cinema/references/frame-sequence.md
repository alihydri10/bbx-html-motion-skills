# Frame-sequence mode: footage scrubbed by scroll

Use this when the picture should look like film rather than real-time 3D: photoreal landscapes,
AI-generated shots (Higgsfield, Kling, Seedance), After Effects renders, drone footage. The engine,
cards, panels, rail, reader, static mode and QA stay identical; only the scene changes.

## When to choose it over the live scene

| Choose frames | Choose live Three.js |
|---------------|----------------------|
| The camera path is fixed and the look must be photoreal | The viewer benefits from data-driven change (bands lighting up, counts growing) |
| You already have, or can generate, the footage | The scene must change with real numbers or many states |
| Low-end phones must look as good as desktops | Weight must stay tiny (a procedural scene is a few KB) |

Hybrid is possible (frames as a backdrop texture, live elements on top) but costs both budgets; only
when one live element is essential.

## Switching the template

```js
var FRAMES = { urls: [...desktop urls], mobileUrls: [...mobile urls], fit: "cover" };
CONFIG.sceneMode = "frames";
// each stage drives the footage position, 0..1, instead of (or as well as) a camera:
{ title:"The kiln", scene:{ frame:0.31 }, ... }
```

The footage holds on that frame while the card is read, then scrubs to the next stage's frame, the
same arrive/hold/leave rhythm as the camera. `cam` can be omitted in frames mode. The three.js script
tag can be removed. Static mode uses `stage.still` (an image URL) as each section's plate; point it at
the stage's own frame.

Loading order: frame 0 and every stage's key frame first, then the rest in order; while a frame is
missing, the nearest loaded frame is drawn, so scrubbing never shows a blank. If more than 20% of
frames fail to load the page goes static.

## Producing the footage

1. **Plan one continuous camera.** Write the stages first, then the shot list: one shot per stage
   transition, each starting exactly where the previous one ends.
2. **Seams are a production contract, not a prompt adjective.** Generate each shot from the previous
   shot's actual last frame (first/last-frame conditioning in the video model, or an image-to-video
   start frame). Check every seam before generating the next shot; a bad seam cannot be fixed by the
   page.
3. **Slow, steady moves.** Scroll scrubbing exposes every jitter. Prefer dolly, crane and slow orbit;
   avoid handheld shake, fast pans and flicker (AI shots: ask for stable lighting and no morphing).
4. **Leave room for the UI.** Keep the subject in the upper two thirds and the left third darker
   where the headline and cards sit, or the veil will have to darken too much.
5. **Mobile variant.** If the composition breaks in a vertical crop, generate a separate 9:16 chain
   rather than cropping; pass it as `mobileUrls`.

## Turning shots into frames

```bash
python3 scripts/make_frames.py shot1.mp4 shot2.mp4 shot3.mp4 --out frames --fps 12
```

Writes desktop (1600 px) and mobile (900 px) WebP sequences plus `manifest.json` with the frame
count and the 0..1 `frame` value where each shot starts, which is what each stage's `scene.frame`
should be set to (usually a little after the shot start, so the hold sits on a settled image).

Budgets: 12 fps is plenty for slow moves under scroll. Aim under 6 MB desktop and 3 MB mobile;
lower fps or quality before width. Image sequences scrub backward perfectly; a `<video>` element
scrubbed through `currentTime` stutters on reverse and seeks slowly on many phones, so the template
uses images.

## Getting frames into a published page

A claude.ai published page cannot load images from other sites. Two ways:

- **Artifact assets** (preferred for more than a few MB): publish the page first, then upload each
  frame as an asset of that artifact and put the returned `/_blob/<id>` URLs into `FRAMES.urls`. The
  page must declare the `assets` capability; check the Artifact tool's capabilities first.
- **Data URIs** for small sequences: base64 grows the file by a third; stay well under the 16 MB
  page limit.
