---
name: "scroll-cinema"
description: Build cinematic, scroll-driven HTML story pages, where a Three.js scene or a scrubbed footage sequence (AI video, After Effects renders, drone shots) plays like a film as the reader scrolls or presses play, with stage cards, a stage rail, data panels, a text reader, and a clean no-WebGL fallback. Use this whenever the user wants a "scrollytelling" page, a scroll-animated or WebGL story, an interactive site walkthrough, an "Apple-style" scroll experience, a 3D process explainer, an investor or project story told in stages, or asks to rebuild, fix or improve an HTML page like that (including pages with "Plays automatically · scroll to take over", "Read as text", or "This page needs WebGL"). Also use it when someone sends such a page made elsewhere and says it looks broken, overlaps, or needs to look more professional. Prefer it over a generic web page whenever the story has a physical place or process that a camera can move through.
---

# Scroll cinema

A scroll cinema page is a short film the reader drives. A fixed WebGL scene fills the screen; a tall
invisible track gives the page its scroll length; scroll position (or an autoplay clock) becomes one
number, `progress` from 0 to 1, and everything on screen is a function of that number: camera
position, scene state, which stage card shows, which data panel shows, which labels float over the 3D.

The template in `assets/template.html` is a complete, tested engine. Start from it every time. It
already solves the problems that break these pages in practice (see `references/pitfalls.md`), and
`scripts/check_page.py` proves the result before anyone sees it.

## Decide the format and the pipeline first

Use a scroll cinema when the story happens in a place or follows a physical process the camera can
travel through: a site, a plant, a field, a product's insides, a sequence of machines. Ask what the
motion proves: the best mechanic demonstrates the client's claim (dead ground turning into working
land), not decoration. If the content is an argument with numbers and no place, a slide deck or a
normal article serves it better; say so.

Then choose the picture pipeline, and tell the user which and why:

| Pipeline | `CONFIG.sceneMode` | Choose when |
|----------|-------------------|-------------|
| Live Three.js scene | `"three"` | The scene must change with data or many states; weight must stay tiny; a schematic look is right |
| Scrubbed frame sequence | `"frames"` | The look must be photoreal or filmic; the footage exists or can be generated (AI video, AE renders, drone); low-end phones must look as good as desktops. Read `references/frame-sequence.md` |
| Plain article or slides | none | Motion adds less than it costs |

## Workflow

### 1. Write the story before touching code

Before the copy, answer four questions in a line each: what the viewer must understand after one
pass; the one memorable transformation; what stays still while the biggest motion happens; and which
frame must look expensive even as a screenshot. The climax of the motion should land on the closing
call to action, not before it.

Fill the `STORY` object first, on paper or in chat. It is the whole content model:

- `brand`, `brandSub`: header identity, short (the header has one line on phones).
- `eyebrow`, `title`, `lede`: the opening. The title is a statement, 2 to 6 words per line, with `<br>`
  where the line should break. The lede is one or two sentences.
- `stages[]`: 4 to 10 stages. Each has `nav` (2 or 3 words for the rail), `title`, `body` (one short
  paragraph, 35 to 70 words; numbers that need a table go in a panel instead), `cam`, `scene`, and
  optionally `panel`, `labels`, `tone`.
- `PANELS`: evidence. Tables, a big number, a short source line, and a note. Every figure carries its
  source (lab, date, report number). Never invent a figure to fill a panel; leave a visible placeholder
  and list it for the user.
- `foot`: sources, caveats, and what is deliberately left out.

If the user hands you an existing page, extract its copy and data into this shape first (the content
usually lives in a `STAGES`-like array and in panel markup), then check the numbers against each other
before building. Contradictions between body text and tables are common; flag them, do not copy them.

### 2. Direct the camera

For each stage decide one camera move and one change in the scene. Read
`references/motion-direction.md` for the grammar (establish wide, push in for process, go low and
close for evidence, pull back to close). In code a stage is two numbers sets:

```js
cam:{ p:[x,y,z], l:[x,y,z] },   // where the camera is, what it looks at
scene:{ life:0.45, bands:1 }    // targets the scene interpolates toward
```

Scene values carry forward: a stage only lists what changes.

### 3. Build the scene, one proof slice first

Before building every stage, get the opening frame and one stage-to-stage transition to near-final
quality on desktop and phone, and run the checker on them. If that slice does not convince, fix the
idea or the assets before expanding.

Replace section 7 of the template (`SCENE`) with the project's world. The engine talks to the scene
through four functions: `draw(values, time, camPos, camLook)`, `resize(w, h)`, `setDPR(r)` and
`project(point)` for labels. Open the page with `?debug=1` to get a 0 to 1 slider, live fps and a
"Copy cam" button that writes the current camera as a `cam:{...}` line for `STORY`; pose stages by
dragging, not by scrolling. Keep heavy work out of the frame loop: rebuild instance matrices only
when their driving value changes (see `plantsUpdate`). `references/engine.md` covers terrain shaders,
instanced planting, particles, a second "close-up" set reached through a fade cut, and 3D labels.

Build for the real thing: if the user has a site plan, trace the boundary from it and say the rest is
indicative. If not, keep the scene schematic and honest rather than detailed and invented.

### 4. Theme it

Only the `:root` block changes per brand: colors, two font families, gutter, header height. The
template ships with the Tierris tokens (deep green, accent green, near black, off white; Space Grotesk
with Inter). Keep text on panels at least 4.5:1 contrast against `--panel`.

### 5. Run the checker, look at the screenshots, fix, repeat

```bash
python3 scripts/check_page.py page.html --out qa --three-js /path/to/three.min.js
```

It renders the page in Chromium at desktop (1440×900), short laptop (1200×630) and phone (390×844),
in motion mode and with WebGL disabled, scrubs to the opening and every stage, and fails on overlapping
fixed layers, layers running off screen, stage cards that never appear, JavaScript errors, and a static
mode that is not clean. On desktop it also resizes mid-story (the stage must not change), opens
`#stage-3` (must land there without autoplay) and injects a scene failure with `?fail=scene` (must go
static). A fallback that was never exercised is an assumption. Then open the screenshots and look at them; the script catches collisions, not
ugliness.

In this sandbox cdnjs is not reachable, so fetch three.js once and pass it with `--three-js`:

```bash
cd /tmp && npm pack three@0.128.0 && tar xzf three-0.128.0.tgz && ls package/build/three.min.js
```

A heavy scene can take minutes under software rendering; use `--modes static` or `--viewports short`
to iterate on one case quickly, then run everything once at the end.

### 6. Deliver

On claude.ai, publish the single HTML file as an artifact (the template already follows the hosting
rules: one self-contained file, scripts only from cdnjs, Google Fonts, safe-area padding, explicit
background). See `references/publishing.md` before adding anything that loads from the network.
Tell the user, in a sentence each: what the page does, which figures are placeholders, and anything in
their source material that contradicted itself.

## Non-negotiables

These are the failures that make a page look broken to the one person who matters (an investor on a
laptop, a client on a phone). The template handles all of them; do not undo them.

1. **One failure path.** No WebGL, three.js blocked, the scene throws, the context is lost, or
   `?static=1`: every case calls `goStatic()`, which hides every fixed motion layer and renders the full
   story as a normal article. A message laid over the opening is not a fallback.
2. **Fixed layers own zones.** Header (brand and every control) at the top; opening padded below the
   header; HUD row at the bottom; rail on the right edge. Nothing floats in the middle of the screen
   where the headline lives.
3. **Cards and panels stack in a grid cell**, not with absolute positioning, so the container is always
   as tall as its content and the HUD never grows into the scene unexpectedly.
4. **The reader always works.** "Read as text" opens the same article the static mode shows, built from
   the same `STORY` data, so the two can never drift apart.
5. **Exact state for meaning, smoothed state for pictures.** The scroll position (or autoplay clock)
   is the exact `target`; it decides the stage card, panel, rail and `#stage-N` URL. The eased
   `progress` only moves the camera and scene. Resizing keeps `target`; height-only changes under
   160 px (the phone address bar) are ignored.
6. **Respect the reader and the device.** Autoplay stops on the first wheel, touch or key; reduced-
   motion users get no autoplay, no smoothing and no ambient animation; the loop sleeps in a hidden
   tab; pixel ratio is capped and steps down after sustained slow frames, never back up (oscillating
   quality looks worse than steady lower quality); Save-Data starts at 1×.
7. **Every number is sourced** in the panel that shows it, and the body text never claims more than
   the table supports.

## Files

- `assets/template.html`: the engine plus a 4-stage demo scene. Copy it, then edit `STORY`, `PANELS`,
  `CONFIG`, the theme block and the scene block. Sections are numbered in the source.
- `scripts/check_page.py`: the QA run described above.
- `scripts/make_frames.py`: video shots → desktop and mobile WebP sequences plus a manifest with the
  `frame` value where each shot starts.
- `references/engine.md`: how the engine works and how to extend it (read before changing anything
  outside `STORY` and the scene block).
- `references/motion-direction.md`: camera grammar, pacing, and how to make it feel like film.
- `references/pitfalls.md`: what goes wrong in pages like this, with the fix for each. Read it when
  reviewing or repairing someone else's page.
- `references/frame-sequence.md`: footage pipeline (AI video, AE, drone) scrubbed by scroll,
  including seam continuity between generated shots.
- `references/publishing.md`: claude.ai hosting constraints and how the page meets them.
- `references/sources.md`: open-source work this skill learned from.
