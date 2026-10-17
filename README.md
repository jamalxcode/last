# Last Marine Standing

*One marine. One base. No backup.*

A classic 90s-style first-person shooter that runs entirely in your browser: no install, no server, no plugins.

**▶ Play:** https://jamalxcode.github.io/last/

It is the real [Chocolate Doom](https://github.com/chocolate-doom/chocolate-doom) engine compiled to WebAssembly, playing the free [Freedoom: Phase 1](https://freedoom.github.io/) game data (4 episodes, 36 levels, full sound and music), rebranded as *Last Marine Standing*.

## Controls

| Key | Action |
|---|---|
| `W` `A` `S` `D` | Move / strafe |
| Mouse | Turn |
| Left click / `Space` | Fire |
| `E` | Open doors / use switches |
| `Shift` | Run |
| `1`–`7` | Switch weapon |
| `Tab` | Automap |
| `Esc` | Menu (and release the mouse) |
| `Enter` / `Space` | Select in menus |
| `F` | Fullscreen |

Click the game to capture the mouse again after pressing `Esc`.

**Saving:** Esc → Save Game → pick a slot → type a name → `Enter`. Saves and settings are kept in your browser (IndexedDB), so they survive reloads. Clearing site data deletes them.

## Project layout

```
index.html              web page: loader, click-to-play screen, controls
engine/lms.js, lms.wasm the compiled game engine
freedoom1.wad           Freedoom: Phase 1 game data (levels, art, sound, music)
lms.wad                 branding patch: title screen + menu logo
default.cfg             default controls and sound settings
title.png               title art shown on the start screen
tools/make_branding.py  regenerates lms.wad (and title.png) from freedoom1.wad
engine/source/          engine changes (patch) + script to rebuild the engine
licenses/               GPL (engine) and Freedoom license + credits
```

## Run locally

Browsers won't load WebAssembly from `file://`, so serve the folder:

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Change the branding

Edit the text/colors in `tools/make_branding.py`, then:

```sh
pip install pillow numpy
python3 tools/make_branding.py freedoom1.wad lms.wad
mv lms-title-preview.png title.png
```

To replace characters, sounds or levels, add lumps to `lms.wad` (or another patch WAD loaded with `-file` in `index.html`) using a WAD editor such as [SLADE](https://slade.mancubus.net/).

## Rebuild the engine

The engine is [cloudflare/doom-wasm](https://github.com/cloudflare/doom-wasm) plus [`engine/source/doom-wasm.patch`](engine/source/doom-wasm.patch), which:

- updates the Emscripten build flags for current SDKs,
- fixes the music synth (OPL) hanging the browser on startup, so music works,
- lets Space select menu items, and links IndexedDB storage for persistent saves,
- fixes `boolean` being compiled with different sizes in different files, which corrupted memory and made single-player games start in deathmatch mode.

With the [Emscripten SDK](https://emscripten.org/docs/getting_started/downloads.html) activated:

```sh
engine/source/build-engine.sh
```

## Licenses and credits

- **Engine:** Chocolate Doom / doom-wasm, GNU GPL v2. See `licenses/GPL-2.0-engine.md`. Source and changes are in `engine/source/`.
- **Game data:** Freedoom, BSD 3-clause. See `licenses/FREEDOOM-COPYING.txt` and the credits files.
- **Branding and web page:** this repository.

Not affiliated with or endorsed by id Software, Bethesda or ZeniMax. DOOM is a trademark of its owners.
