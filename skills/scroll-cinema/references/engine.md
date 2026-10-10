# Engine reference

How `assets/template.html` works, and how to extend it without breaking it.

## Contents
1. Layers and layout
2. The timeline
3. Playback modes and the two kinds of state
4. The frame loop
5. The scene interface
6. Scene recipes (terrain, planting, flows, camera on a curve, model animation, close-up set and cuts, labels)
7. Resize, deep links, debug HUD, adaptive quality
8. Adding things safely
9. Performance budget

## 1. Layers and layout

| z | id | role | zone |
|---|----|------|------|
| 0 | `#scene` | WebGL canvas | full screen |
| 1 | `#veil` | gradient that keeps text readable | full screen, no pointer |
| 5 | `#labels` | 3D-anchored callouts | full screen, no pointer |
| 6 | `#opening` | title, lede, hint; fades out early | centre, padded below header |
| 8 | `#hud` | stage card (left) + data panel (right) | bottom row |
| 10 | `#rail` | stage navigation | right edge, centred |
| 12 | `header` | brand + all controls | top bar |
| 14 | `#cut` | black for fade cuts between sets | full screen |
| 20 | `#reader` | text dialog | full screen |

`#track` is an empty block whose height (`100vh + N × scrollPerStage vh`) creates the scroll length.
`#article` is empty until static mode fills it.

On phones (≤820px) the HUD becomes a column (panel above card), the rail hides, the time code hides,
and panels scroll inside a 38vh cap. Under 560px of height the card body and panels hide so the scene
stays visible.

## 2. The timeline

`progress` p runs 0 to 1.

- `[0, introShare]` is the opening (default 5%).
- The rest splits into N equal stage slots of width `W`.
- Inside a slot the camera **arrives** at 30% and starts **leaving** at 88%. Between arrive and leave
  it holds still (the scene can still animate through `uTime`), so the reader has time to read.

`KEYS` is built once from `STORY`: intro key, then an arrive key and a leave key per stage, each
carrying a camera and a full scene-value snapshot (values carry forward). `sampleKeys(p)` finds the
two surrounding keys and a smoothstepped `u`; camera position, look-at and every scene value
interpolate with it. Change `arrive`/`leave` in `CONFIG` to make moves longer or holds longer.

`activeStageAt(p)` decides which card, panel, rail item and labels are on. A stage is active for its
whole slot, so the card appears as the camera starts moving toward it.

## 3. Playback modes and the two kinds of state

- `target` is the **exact** position: scroll fraction in manual mode, the autoplay clock in auto mode.
  It decides meaning: active stage, card, panel, rail item, `#stage-N` hash, progress bar, time code.
- `progress` is the **render** position, eased toward `target` by `damping` (instant under reduced
  motion). It drives only pictures: camera, scene values, opening fade.

Deciding the stage from the smoothed value makes cards lag the scroll and lets a resize or reload land
on the wrong stage; keep the split.

- **auto**: an internal clock advances `autoT`; `pAtTime` maps it to progress (intro seconds, then
  `secondsPerStage` per stage) and the engine writes the matching scroll position, so the scrollbar
  and the progress bar stay honest.
- **manual**: progress eases toward the scroll position (`damping`).

Autoplay starts 0.9 s after load if the reader has not moved. Wheel, touch, and navigation keys switch
to manual; the Play button resumes from the current point. Rail clicks switch to manual and smooth-
scroll to that stage's arrive point. `window.__goManual` exists so tests and embeds can stop autoplay.

## 4. The frame loop

Every frame: advance the clock → update `target` and `progress` → sample keys with `progress` →
`SCENE.draw(values, elapsed, camPos, camLook)` → fade the opening → progress bar and time code from
`target` → on stage change (from `target`) toggle card/panel/rail, `aria-hidden` and the URL hash →
project labels → measure frame time for adaptive quality. The loop returns early while the tab is
hidden or in static mode.

Keep the loop allocation-free: camera vectors are plain reused arrays.

## 5. The scene interface

`buildThreeScene()` and `buildFrameScene()` each return the same four functions, so the engine never
knows which one it is driving:

```js
{
  draw(values, time, camPos, camLook),  // every frame; values = interpolated STORY scene numbers
  resize(w, h),                         // after a real resize (not the phone address bar)
  setDPR(ratio),                        // adaptive quality hook
  project([x,y,z]) -> {x, y, visible}   // screen position for 3D labels; frames mode returns visible:false
}
```

Write a new world as another `buildXScene()` returning this object. Throw from it on any setup
failure; the caller turns a throw into static mode. Honour `?fail=scene` at its top so the checker can
prove the fallback.

## 6. Scene recipes

### Terrain that changes state
One `PlaneGeometry`, heights baked once from a height function, a `ShaderMaterial` whose uniforms are
the story's state (`uLife`, `uBands`, ...). Colour transitions belong in the shader as `mix()` driven by
a uniform, often with a spatial term (distance from centre, noise) so the change spreads rather than
fades. Bake a shared `vnoise` into the shader for texture. Lighting: one `dot(normal, sun)` term is
enough at this camera distance.

### Planting that grows
`InstancedMesh` with one matrix per plant. Store each plant's base position, scale and a delay (outer
rings later). In `draw` rebuild matrices only when the driving value moved more than 0.002. Use
several instanced meshes for several species, with simple low-poly geometry (cones, a trunk cylinder
plus a sphere crown). For a specific planting plan, place counts per band from the user's data and
show the species split in a panel.

### Flows (material moving, water, gas)
`THREE.Points` with a `ShaderMaterial`; each point has a random seed; position = `mix(A, B,
fract(seed + time × speed))`, with an `uOn` uniform for visibility. Additive feel without additive
blending: fade alpha at both ends of the path.

### Camera on a curve
For one continuous journey (along a road, down a pipeline) instead of stage-to-stage moves, put the
stage cameras on a `CatmullRomCurve3` (`curveType = "centripetal"` avoids overshoot) and sample it by
arc length with `getPointAt(u)`, not `getPoint(t)`: raw `t` speeds up and slows down by itself where
the curve bends. Look slightly ahead (`getPointAt(u + 0.02)`) so the camera does not appear to drag.
Map each stage's `scene.path` value (0..1) to `u`; pacing then stays in the arrive/hold/leave keys.

### Model animation driven by scroll
If a model ships animation clips, scroll must own their time so they run backward when the reader
scrolls up: `action.play(); action.paused = true;` then each frame `action.time = v.clip *
clip.duration; mixer.update(0);`. Never advance it with the frame delta. (Loading glTF needs the
GLTFLoader, which is not in the r128 UMD file; for claude.ai pages prefer procedural geometry.)

### A close-up set and a fade cut
For "inside the soil" or "inside the machine" shots, build a second group far from the main set (for
example at y = −600) with its own geometry and uniforms, and give stages there `cam` values inside
it. When the camera key jumps between sets, hide the jump: drive `#cut` opacity to 1 over the last
part of the move and back to 0 after it.

```js
// in the frame loop, after sampling keys
var jump = k.a.cam.set !== k.b.cam.set;          // add set:"main"|"close" to cams
$("cut").style.opacity = jump ? String(Math.sin(Math.PI * k.u)) : "0";
camera.position.copy(k.u < 0.5 ? A : B);        // snap at the midpoint, under full black
```

### 3D labels
Per stage, `labels:[{text, sub, at:[x,y,z]}]`. Each frame they project to screen and hide when behind
the camera or outside 90% of the frame. Keep them to 2 or 3 per stage and short; they are signage, not
captions. Do not put labels where the HUD sits (lower 35% of the screen) at the stage's camera.

### Sound (optional, off by default)
If a score is wanted, generate it with Web Audio after a user gesture (a sound button in the header),
never autoplaying. Keep it under the controls group so the header remains the only control zone.

## 7. Resize, deep links, debug HUD, adaptive quality

- **Resize** is debounced 150 ms. If only the height changed by less than 160 px it is the phone
  address bar: ignore it. Otherwise resize the scene, then scroll to `target × new scroll length` so
  the story stays where it was.
- **Deep links**: `#stage-3` opens at stage 3's arrive point in manual mode, without autoplay; in
  manual mode the hash follows the active stage (`history.replaceState`), so a reload or a shared link
  returns to the same place. Static mode scrolls to the matching section.
- **Debug HUD** (`?debug=1`): slider over the whole timeline, current target, stage, pixel ratio and
  fps, and "Copy cam", which logs and copies `cam:{ p:[..], l:[..] }` for the current frame.
- **Adaptive quality**: frame times are averaged over 90-frame windows; two consecutive windows slower
  than `slowFrameMs` (34 ms) step the pixel ratio down by 0.25 to `minDPR`. It never steps back up.
  Save-Data starts at 1×. If the scene is still slow at 1×, cut scene scope (counts, segments) rather
  than adding more tiers.
- `window.__cinema.state()` returns `{target, progress, stage, mode, dpr, isStatic, sceneMode}` for
  tests; keep it.

## 8. Adding things safely

- New fixed UI: give it a zone that no other layer uses, add it to the static-mode hide list, and add
  its selector to the overlap check in `scripts/check_page.py`.
- New data panel: add HTML to `PANELS` and reference its key from a stage; it then appears in the HUD,
  the reader and the static article automatically.
- New stage: add it to `STORY.stages`; track height, keys, rail and reader update themselves.
- Never write copy directly into the HTML body. Everything visible comes from `STORY`/`PANELS`, which
  is what keeps the reader and the static article identical to the motion version.

## 9. Performance budget

- Pixel ratio capped at 1.75 (1.5 on small screens).
- Terrain ≤ 200×200 segments (140 on small screens).
- Instances ≤ ~10k total; halve on small screens.
- One directional light plus a hemisphere light; no shadows unless the story needs them.
- Test under software rendering with the checker; if a frame takes seconds there, it stutters on an
  integrated laptop GPU.
