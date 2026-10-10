# Sources

Open-source work this skill learned from (reviewed October 2026). Ideas were rewritten for this
engine; no code was copied. All three are MIT licensed.

- **elix-scroll-3d** (github.com/ElixIsmael/elix-scroll-3d): "does 3D earn its place", the mechanic
  should demonstrate the client's claim, climax on the call to action, arc-length camera curves,
  scroll-owned animation clip time, a 0..1 debug slider, mobile address-bar handling, device signals
  and Save-Data.
- **scroll-3d-cinematic-stack** (github.com/omarkhandji-commits/scroll-3d-cinematic-stack): exact
  versus rendered progress, proof slices before full production, adaptive quality with hysteresis,
  deliberate failure injection, routing between live 3D and pre-rendered footage, seam continuity for
  generated shot chains.
- **Fluke-Motion** (github.com/luthfierlmbang/Fluke-Motion): broad motion-design reference for UI
  effects; useful when a page needs scroll effects beyond a single scene.

The starting point for this skill was a production page (Tierris Genesis, Section B, by Fred
Korangy's team): its stage/rail/panel/reader structure and its scroll-or-autoplay timeline are the
basis of the template; its fallback and layout failures are the basis of `pitfalls.md`.

Worth reading directly when a project needs more than this skill covers: Three.js docs and examples
(threejs.org), GSAP ScrollTrigger docs (when a page is DOM-led rather than scene-led), and Lenis
(smooth scrolling, only if native scroll truly is not enough).
