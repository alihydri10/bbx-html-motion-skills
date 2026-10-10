# Pitfalls, and the fix for each

Collected from reviewing real scroll-cinema pages, including one that reached a client looking broken.
When repairing someone else's page, walk this list top to bottom.

## Fallback

**Fallback message laid over the live layout.** The page detects no WebGL, shows "This page needs
WebGL" in a fixed box, and leaves the opening, controls, rail and progress bar in place. The message
lands on top of the headline and the page looks shattered.
Fix: one `goStatic()` that adds `html.static`, hides every motion layer, and renders the whole story
as an article. Detection uses a real `getContext` probe, `typeof THREE`, a try/catch around scene
construction, and `webglcontextlost`.

**Detection by constructor only.** `new THREE.WebGLRenderer()` can log an error and still return an
object on some browsers, or throw on others. Probe a canvas first, then wrap construction.

**Reader that only works in motion mode.** If the text version is built inside the WebGL branch, the
one mode that needs it most never gets it. Build it before any WebGL code.

## Layout

**Controls floating mid-screen.** A play/scrub bar fixed at `top: 92px; left: 50%` sits exactly where
a large headline lands on a 630 px tall laptop window. Put every control in the header.

**Opening not padded for the header.** A vertically centred headline on a short screen rides up under
the header. Pad the opening by header height plus safe-area plus a margin.

**Absolutely stacked cards.** `position:absolute; bottom:0` cards in a fixed container give the
container zero height, so nothing else can lay out against it and long cards grow upward into the
scene unchecked. Stack them in one grid cell.

**Panels and rail on the same edge.** A 390 px panel at `right: 96px` next to a rail at `right: 26px`
collides when the rail labels expand. Keep the HUD's right edge clear of the rail (`right: gutter +
56px`) and hide the rail on phones.

**Text sizes under 12 px.** Tiny type (10–11 px) in tables and labels reads as unfinished on a projector
and fails on phones. Tables at 12 px minimum, card body 14.5 px, labels 11.5 px.

## Content

**Body text that overclaims the table.** "The post-treatment plot has the highest phosphorus" while
the table shows another plot higher. Check every comparative claim against the data before building;
when they disagree, write only what the data supports and tell the user.

**Draft lab reports presented as final.** If reports carry a DRAFT watermark, say so in the panel's
source line.

**Inventing detail in the 3D.** Equipment layouts, planting densities or terrain that are not from the
user's drawings should be labelled indicative in the footnote, as good pages already do.

**Typography off brand.** Serif display fonts and warm sand palettes can be beautiful and still wrong
for the brand. Theme from the brand's tokens, not from the mood of the scene.

## Behaviour

**Autoplay that fights the reader.** Autoplay writes the scroll position every frame; if user input
does not switch it off, the page snaps back. Switch to manual on wheel, touch and navigation keys.

**No reduced-motion path.** Readers who ask for reduced motion get no autoplay, no smoothing, and
static `uTime`.

**Rendering in a hidden tab.** Stop the loop on `visibilitychange`, and reset the clock on return so
the first frame does not jump.

**Uncapped pixel ratio.** A 3× phone renders nine times the pixels of 1×. Cap it.

**Stage decided from the smoothed value.** Cards lag the scroll, and after a reload or resize the page
can land on the neighbouring stage. Meaning comes from the exact position; only pictures are eased.

**Resize that loses the place.** The track is measured in vh, so a resize changes the scroll length
and the same scrollY now means a different stage. Store the exact progress and scroll back to it.

**Canvas reallocated by the phone address bar.** Every scroll that shows or hides the bar fires a
resize; reallocating the drawing buffer each time stutters. Ignore height-only changes under ~160 px.

**Quality that flickers.** Raising and lowering resolution every few seconds is more visible than a
steady lower setting. Step down after sustained slow windows, never back up within a visit.

**Fallbacks never exercised.** A static path that has never been triggered usually has a bug. Keep a
`?fail=scene` switch and run it in QA every time.

**Shared links that open at the start.** A reader sending "look at stage 6" needs `#stage-6` to work,
in motion and static mode.

**Video scrubbed by `currentTime`.** Reverse scrubbing stutters and phones seek slowly; use an image
sequence for scroll-driven footage.

**Seams between generated shots.** Two AI shots that "match" by prompt jump at the cut under scroll.
Generate each from the previous shot's real last frame and check the seam before continuing.

## Delivery

**Unpinned or ES-module three.js.** Imports from unpkg/esm.sh are blocked on claude.ai published
pages, and `three@latest` changes under you. Use the pinned UMD build from cdnjs (r128).

**Never tested at short heights.** 1200×630 (a laptop with browser chrome and a dock) is where most
collisions appear. The checker includes it for this reason.
