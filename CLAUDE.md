# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Last Marine Standing** is a 90s-style first-person shooter that runs entirely in the browser, live at https://last.sala.company. It is the Chocolate Doom engine (via Cloudflare's `doom-wasm`) compiled to WebAssembly, playing the free Freedoom: Phase 1 game data, rebranded with a small patch WAD. The web page is a single static `index.html` with inline CSS/JS — no framework, no npm, no build step for the site itself.

## Commands

```sh
# Run locally (WebAssembly will not load from file://)
python3 -m http.server 8000      # then open http://localhost:8000

# Regenerate the branding patch WAD (title screen + menu logo)
pip install pillow numpy
python3 tools/make_branding.py freedoom1.wad lms.wad
mv lms-title-preview.png title.png

# Rebuild the engine (needs an activated Emscripten SDK, autotools, git)
engine/source/build-engine.sh
```

There are no tests or linters in this repo.

## Architecture

```
index.html                 page: loader UI, click-to-play overlay, controls, Emscripten Module config
engine/lms.js, lms.wasm    compiled engine (committed build output)
engine/source/             doom-wasm.patch + build-engine.sh (pins doom-wasm commit 65e0d3ae...)
freedoom1.wad              Freedoom: Phase 1 IWAD (~28.8 MB)
lms.wad                    branding PWAD: replaces TITLEPIC and M_DOOM lumps
default.cfg                default controls/sound config
title.png                  start-screen art (overlay background)
tools/make_branding.py     builds lms.wad from freedoom1.wad (uses DejaVuSans-Bold font path)
licenses/                  GPL v2 (engine) + Freedoom license/credits
```

How `index.html` works:
- Defines a global `Module` (Emscripten) with `noInitialRun: true`; in `preRun` it preloads `freedoom1.wad`, `lms.wad`, `default.cfg` into the virtual FS.
- Saves/settings live in `/saves`, mounted as **IDBFS** (IndexedDB). On first start `default.cfg` is copied to `/saves/lms.cfg`. Engine args: `-iwad freedoom1.wad -file lms.wad -window -nogui -config /saves/lms.cfg -savedir /saves`.
- `FS.syncfs` writes back every 3 s and on `visibilitychange`/`pagehide`. If IndexedDB fails (private windows), the game still runs without persistence.
- Download progress is shown by patching `XMLHttpRequest.prototype.open` for `freedoom1.wad`, with a hard-coded fallback total of `28795076` bytes (the current file size). Update it if `freedoom1.wad` changes.
- Click on the overlay calls `Module.callMain(args)` and requests pointer lock; `F` toggles fullscreen on `#screen`.
- `engine/lms.js` is loaded after the inline script. `build-engine.sh` renames `websockets-doom.wasm` references to `lms.wasm`.

The engine patch updates Emscripten flags, fixes the OPL music startup hang, lets Space select menu items, links IndexedDB, and fixes inconsistent `boolean` sizes (which caused single-player to start in deathmatch).

## Deployment

- `.github/workflows/pages.yml` deploys the whole repo root (`path: .`) to GitHub Pages via Actions on every push to `main` (also `workflow_dispatch`). **Pushing to `main` deploys live.**
- Custom domain from `CNAME` (`last.sala.company`). `.nojekyll` is present so files are served as-is.
- Build artifacts (`engine/lms.js`, `engine/lms.wasm`, `lms.wad`) are committed; CI does not build anything.

## Conventions / gotchas

- Keep the GoatCounter analytics snippet at the end of `index.html` intact (endpoint `https://salacompany.goatcounter.com/count`; skipped on localhost; paths prefixed with `location.host` so all `*.sala.company` apps share one dashboard).
- The canvas must have no border or padding, or mouse coordinates break (noted in the CSS).
- Keep the controls list in `index.html` and the README controls table in sync.
- No cache-busting/version strings are used.
- `.gitignore` excludes `.build/`, `engine/source/.build/`, `__pycache__/`.
- License notes: engine is GPL v2 (source/changes must stay in `engine/source/`); Freedoom is BSD. The footer disclaims affiliation with id Software/Bethesda.
