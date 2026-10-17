#!/usr/bin/env bash
# Rebuild engine/lms.js + engine/lms.wasm from source.
#
# The engine is Cloudflare's doom-wasm (a Chocolate Doom port, GNU GPL v2)
# plus doom-wasm.patch, which:
#   - updates Emscripten flags for current SDKs and enables memory growth,
#   - fixes music (OPL) startup hanging the single-threaded browser build,
#   - fixes `boolean` having different sizes in different files, which
#     corrupted globals (single-player games started in deathmatch mode).
#
# Requires: an activated Emscripten SDK (emcc on PATH), autotools, git.
set -euo pipefail

DOOM_WASM_COMMIT=65e0d3ae2ffa604155eebd96ed40da6567bd08f4
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HERE/.build}"

rm -rf "$WORK" && mkdir -p "$WORK"
git clone https://github.com/cloudflare/doom-wasm "$WORK/doom-wasm"
git -C "$WORK/doom-wasm" checkout -q "$DOOM_WASM_COMMIT"
git -C "$WORK/doom-wasm" apply "$HERE/doom-wasm.patch"

(cd "$WORK/doom-wasm" && ./scripts/clean.sh && ./scripts/build.sh)

cp "$WORK/doom-wasm/src/websockets-doom.wasm" "$HERE/../lms.wasm"
sed 's/websockets-doom\.wasm/lms.wasm/g' "$WORK/doom-wasm/src/websockets-doom.js" > "$HERE/../lms.js"
echo "Engine rebuilt into engine/lms.js and engine/lms.wasm"
