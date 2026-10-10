---
name: threejs-scroll-cinema-site
description: Build a scroll-driven 3D web page (Three.js) from scratch with Blender models, like the Tierris Section B site diorama with its soil chapter, publish it as an artifact, then refine it in edit rounds.
---

# Three.js scroll-cinema site

**Version 1.0.0** (2026-10-10). Bump the version when you change this skill.

This is the workflow from the Tierris Genesis Section B page: an isometric site diorama plus a soil cutaway chapter. The models come from Blender (through the Blender MCP on Ali's PC). The page is one self-contained HTML file, published as a claude.ai artifact.

## Build from scratch (do these in order)
1. **Brief.** Read the source material (product PDFs, lab data, the story he wants told). Write the story as a list of stages: what the camera shows, what moves, which labels and lab figures appear in each stage. Confirm the stage list with Ali.
2. **Layout.** Fix a SPEC: the position and size of every building, the roads, gates and the ground area, in meters. Every model and camera uses this SPEC.
3. **Models.** Build each building in Blender as its own object (section 1), export GLBs, and pack them (section 2).
4. **Page skeleton.** One HTML file: inlined libraries, embedded models, scene, lights, ground, and the story engine (section 3) with a camera for each stage.
5. **Motion.** Add the animated pieces (vehicles, loader, materials moving) as beats and late keys, or with their own clock when the speed must stay constant.
6. **Text layer.** Labels, stamps with the lab figures, and the hidden Lab data panel. Embed the brand font.
7. **Special chapters.** Heavy close-up scenes (like the soil) as live 3D (section 5).
8. **Quality pass.** MSAA, depth of field, shadows and flicker fixes (section 4).
9. **QA** (section 6), then **publish** (section 7) and send Ali the link.
10. **Edit rounds.** From here on, follow the rules in section 8.

## 1. Models (Blender MCP)
- Run Blender through `mcp__remote-devices__blender__execute_blender_code`. Check `get_scene_info` first, because the open file may not be the right one.
- Model each building as its own object at the origin. Export a GLB with `export_yup=True`, applying modifiers, one file per object.
- Drivers: use simple expressions only (no `**`). Turn on auto-run Python scripts if a driver shows as invalid.
- Heavy renders: run them in the background with `subprocess` → `blender -b file.blend -S Scene --python-expr ... -a`, using Cycles OptiX.
- Moving files: zip them in parts of 11 MB or less, then stage them with `device_stage_files`. Large zips (around 47 MB) time out.

## 2. Packing and embedding
- Use gltf-transform with meshopt (`pack.mjs`): dedup, prune, meshopt. **Don't quantize** meshes with large coordinates or many instanced points, because quantize scaled the soil_lite positions wrongly.
- Embed each GLB as base64 in `window.TIERRIS_MODELS={name:'...'}` and load it with `GLTFLoader.parse`. Then run `prepModel` (linear→sRGB colors) and `collectGlows` (light sprites).
- **Inline the libraries:** three r128, meshopt_decoder, and GLTFLoader. CDNs (jsdelivr) fail for Ali in Iran.
- Textures: embed them as **data URIs**. The artifact runs in a sandboxed iframe, so `TextureLoader` with a URL and crossOrigin gives black textures.
- Fonts: convert them to WOFF2 (`pip install fonttools brotli --break-system-packages`) and embed them with `@font-face` (Neue Montreal Regular/Medium, weights 400/500).

## 3. Story engine (scroll timeline)
- `STORY.stages[]`: each stage has `cam`/`scam` (`{p:[x,y,z], l:[x,y,z]}`), `len` (slot weight), `beats` (keys before arrive), `late` (keys after arrive, which can also move the camera), `labels` (`win:[f0,f1]`, `space:"soil"`, `hot` = opens lab data), and `stamps` (big lab figures; `light:true` on dark backgrounds).
- Timeline: `LENS / SUMW / STARTS`, `Wd(i)`, `stageStart / Arrive / Leave`, `stageFrac`. The track height is `100 + SUMW*170` vh.
- Smoothness: scroll damping is about 2.6/s, exponential. The camera glides toward its goal at about 3.2/s and snaps on big jumps (`jump()` resets `camInit`).
- Objects that need a constant speed (the loader) get their **own clock** over a time span. Don't drive them with stage keys, or the speed jumps.
- Vehicles shouldn't pop in. Park them out of frame (the truck at z -121), and stop them once the job is done (they stay parked).
- Lab data: keep it hidden behind a "Lab data" button (`openData`, `refreshPanels`, `.pclose`, Esc closes it).
- Labels: clamp them inside the viewport (`labelTop` ≥ 150). Don't use text-shadow; use a radial dark `::before` glow for readability.

## 4. Rendering quality vs. speed
- MSAA: use `WebGLMultisampleRenderTarget` (4 samples) on WebGL2 and **cap DPR at 1.25** when MSAA is on. MSAA plus a DPR of 1.5 caused lag.
- Depth of field: in wide shots the blur is 0. Blur only when the camera is near (`near = 1 - smoothRange(60,170,dist)`), with a depth tolerance relative to distance (this prevents flicker).
- Flicker fixes: snap the shadow frustum to the texel grid (extent in 3 m steps), set the camera near plane to 1.0, lift coplanar paving (y 0.14, no shadows), and remove shadows that jump.
- Lights: dim lamps with k ≈ 0.5 and make sure no lamp sits in front of the camera.

## 5. Heavy scenes (the soil lesson)
- ❌ Image sequences, video (it freezes on the artifact host, and seeking is unreliable), createImageBitmap windows, and 100-frame variants all **lag**. A crossfade of about 19 keyframes is light but looks like a dissolve.
- ✅ Ali prefers **live 3D**. Use a code-built scene (instanced grains, roots, seed), or bake textures in Blender (ortho bake cameras) and add a few instanced moving pieces driven by story values (`sChar/sBio/sSeed/sSoil/sMicro/sRoot/sShoot`).
- Keep soil colors dark and natural, use rounded grains and thin roots, and stop the shoot **under the surface**. The next section shows growth above ground.
- Use a fixed soil camera for those stages, and move to the next stage quickly. Don't linger.

## 6. QA
- Use Playwright on Chromium (SwiftShader) with `?dpr=0.5`. Take a screenshot list `SH=[(name, stage, frac, openData)]` (r1shots.py), and look at every shot.
- Check the console for errors, labels in frame, flicker in wide shots (two frames apart), and frame time (perf.py).

## 7. Publish and hand off
- Limits: the page and each text file must be ≤ 16 MB, binary files ≤ 15 MB, and at most 255 files per publish.
- Republish to the **same artifact URL** (the same file path, or pass `url`). Don't create new links unless he asks for a separate version (v2).
- After a milestone:
  - Copy the HTML, textures, pack.mjs and the QA scripts to `Desktop\Tierris_Models\_handoff\` on his PC.
  - Update the project doc `claude/section-b-page-handoff.md`: links, structure, open items.
  - For delivery, put a short Docs artifact next to the files on Drive that says which file needs which folder. For example, V7 = index.html plus the soiltex folder, and no file needs the Blender folder.

## 8. Edit rounds with Ali
- **Collect edits first.** While he is still sending edits, only list and confirm them. Don't build until he says **"start"**.
- He sends screenshots or videos with marks. Restate each edit as a numbered list before you build.
- Don't guess about performance. Measure it (frame time, file size) before you claim something is "lighter".
- Never log in or type credentials for him. He uploads files himself and sometimes rejects device commands, so ask before you browse his PC.
- Back up before each round: `cp page.html backup_rN.html`.

## Reference (Tierris Section B)
- Main page: https://claude.ai/artifact/UrhD6zxzJxJATnzqo7c19D (code-built soil)
- v2: https://claude.ai/artifact/PHxQyxXuvLPP2UN2qKuKWf (GLB soil plus baked textures, Neue Montreal)
- Layout (SPEC): receiving (-45,-86), kiln (-17,-90.7), silo (-1.5,-89.5), mixer (9,-91.2), blend (30,-89), water (61,-89), office (-80,-85.5), road z -72..-69.
