# Publishing on claude.ai

A published artifact page runs under a content-security policy. The template already complies; keep
it that way when you add things.

## What the page may load

- Scripts: only from `https://cdnjs.cloudflare.com` (preferred), `https://cdn.jsdelivr.net/npm/`,
  `https://cdn.tailwindcss.com`, `https://code.jquery.com`. Load libraries as UMD builds with a pinned
  version, in a `<script>` tag before the inline script. three.js: `.../three.js/r128/three.min.js`.
  Its add-ons (OrbitControls, loaders) are not in that UMD file; write what you need inline.
- Styles: only Google Fonts (`fonts.googleapis.com`, font files from `fonts.gstatic.com`). Every font
  stack ends in a basic face and a generic.
- Nothing else: no remote images, no fetches to other sites, no models from a URL. Embed small images
  or textures as `data:` URIs; generate everything else procedurally in the scene.
- Total file under 16 MB.

## Required page details

- `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`
- Safe-area padding on `:root` and offsets on fixed elements (`env(safe-area-inset-top, 0px)` and
  `-bottom`). The template's header, topbar, opening, HUD and reader already add them.
- An explicit `body` background, and colour tokens on `:root` restated for `prefers-color-scheme:
  dark` and `[data-theme="dark"]`. The page is dark by design; `color-scheme: dark` says so.
- Browser storage works but is per viewer; wrap it in try/catch if you use it (the template does not).

## How to publish

1. Write the finished file to `/mnt/user-data/outputs/<name>.html`.
2. Run `scripts/check_page.py` against it and look at the screenshots.
3. Publish it with the Artifact tool (action "publish", that file path, an emoji favicon). To update
   later, republish the same path in the same reply, or pass the artifact's URL in a later reply.

If the user wants a file to send instead of a link, present the HTML file. It still needs internet
for three.js and fonts; if it must work offline, inline three.min.js into the file (about 600 KB) and
drop the Google Fonts link in favour of the basic-face fallbacks.
