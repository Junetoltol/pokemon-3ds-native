# pokemon-3ds-native

C++20 / SDL3 launcher and common runtime interface for a future local 3DS Pokémon port workflow. Separate from the Nintendo Switch nxnative project.

**The eight-profile SDL application is MOCK ONLY. The separate private Ultra Sun port reached its real language-selection screen on macOS ARM64 on 2026-11-09.** See [execution evidence](docs/2026-11-09-ultra-sun.md).
All eight profiles are listed; none is certified compatible. Enter reports the missing backend instead of pretending to launch a game. No ROM, extracted asset, key, translated game code, or generated game binary is distributed.

## Build on macOS ARM64

Requires CMake 3.24+, C++20 compiler, SDL3 development package, and Python 3 for local tools.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure
open build/pokemon-3ds-native.app
```

Use ↑/↓ to select a profile, F for 30/60 display FPS, S for 1/2/4/8 synthetic clock speed, Enter for backend status. Gamepad D-pad selection is implemented; game input mapping and touch forwarding are pending.

```sh
build/pokemon-3ds-native.app/Contents/MacOS/pokemon-3ds-native --headless --frames 600 --fps 60 --speed 8
python3 tools/package_macos.py build/pokemon-3ds-native.app dist/pokemon-3ds-native.app
```

Packaging copies SDL3 into the bundle and signs it ad hoc. It is not notarized. The development build uses the installed SDL3 library. Windows CMake builds create `.exe` and copy runtime DLLs; Windows build/run has not been verified locally.

## Private conversion workflow: Y and Ultra Sun

Requires Cargo/Rust stable (upstream Zakuro declares Rust >=1.95), a C compiler and network access for public dependencies.

```sh
python3 tools/bootstrap.py
python3 tools/port.py --rom /absolute/path/to/owned-y.3ds \
  --sha256 YOUR_EXPECTED_SHA256 --program-id YOUR_EXPECTED_PROGRAM_ID \
  --version YOUR_DECLARED_VERSION \
  --recompiler private/upstream/3dsrecomp --zakuro private/upstream/zakuro
```

This validates container magic, selected profile ID and expected full-file SHA-256, then prints the command. The default profile remains Y; use `--game ultra-sun --program-id 00040000001B5000` for the supplied Ultra Sun input. Y has not been tested with a retail dump. Add `--execute` to generate and build a standalone local port under `private/ports/<game>`. Output is ignored by Git. Only NCSD/NCCH containers are accepted; no key acquisition or decryption service is implemented. A hash supplied by the user binds a local input; it does not independently certify that the dump is Pokémon Y or that its game/update version is correct. Trusted regional/version manifests and retail execution tests remain pending.

The pipeline invokes pinned 3dsrecomp `port … --zakuro …`, then Cargo. The generated program still requires the local game data. The launcher deliberately refuses `--run` until a verified backend and game-specific input contract are integrated. No silent interpreter fallback is presented as a native-only port.

## Save import

```sh
python3 tools/saves.py /path/to/user/main --game y
```

Each import creates a unique private backup, verifies SHA-256 after copying, and never replaces a previous backup. It does not validate save format, migrate between versions, or attach a save to a running game. Save/load safety in retail Pokémon remains unverified.

## Evidence and next gate

See [development status](docs/STATUS.md), [upstream audit](docs/UPSTREAM.md), and [timing and validation plan](docs/TIMING.md). GitHub Actions covers launcher builds/tests on macOS ARM64 and Windows x64; a workflow definition is not evidence of a passing hosted build.

## Bounded real-port execution

After a successful local build, run the private executable separately from the mock frontend:

```sh
python3 tools/run_local.py --game ultra-sun --rom /absolute/path/to/owned-ultra-sun.cci --frames 120 --timeout 120
```

This uses the locally linked game code and the Zakuro compatibility runtime, which can interpret instructions that were not recompiled. It rechecks the dump hash, keeps runtime data/logs under `private/`, mutes audio, and uses software rasterization by default. `--window --renderer gl` requests a visible window. Software rendering does not establish GPU performance. A completed headless slice does not verify the title screen, gameplay, audio or saves. `--rasterizer hardware --renderer vulkan` requires a working Vulkan stack; the tested Mac currently has no Homebrew Vulkan loader/MoltenVK installation.

The `cia/` input folder, all generated ports and runtime output are excluded from Git. CIA conversion remains unsupported by this wrapper; the current experiment uses the supplied NCSD CCI directly. Free disk space is checked before generation; full retail builds need significantly more space than the synthetic smoke test.

To create a private, double-clickable macOS app after conversion:

```sh
python3 tools/package_local_macos.py --game ultra-sun --rom /absolute/path/to/owned-ultra-sun.cci
```

The app is created under `private/apps/`, includes locally generated game code, and must stay private. It references the original CCI instead of copying game assets. Default test launch uses muted audio, software rasterization and OpenGL presentation. It does not change the mock SDL frontend into a real game frontend.
