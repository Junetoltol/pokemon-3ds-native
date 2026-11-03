# pokemon-3ds-native

C++20 / SDL3 launcher and common runtime interface for a future local 3DS Pokémon port workflow. Separate from the Nintendo Switch nxnative project.

**Current application is MOCK ONLY. No Pokémon game executes inside this launcher.**
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

## Pokémon Y first: private conversion workflow

Requires Cargo/Rust stable (upstream Zakuro declares Rust >=1.95), a C compiler and network access for public dependencies.

```sh
python3 tools/bootstrap.py
python3 tools/port.py --rom /absolute/path/to/owned-y.3ds \
  --sha256 YOUR_EXPECTED_SHA256 --program-id YOUR_EXPECTED_PROGRAM_ID \
  --version YOUR_DECLARED_VERSION \
  --recompiler private/upstream/3dsrecomp --zakuro private/upstream/zakuro
```

This validates container magic, program ID and expected full-file SHA-256, then prints the command. Add `--execute` to generate and build a standalone local port under `private/ports/y`. Output is ignored by Git. Only NCSD/NCCH containers are accepted; no key acquisition or decryption service is implemented. A hash supplied by the user binds a local input; it does not independently certify that the dump is Pokémon Y or that its game/update version is correct. Trusted regional/version manifests and retail execution tests remain pending.

The pipeline invokes pinned 3dsrecomp `port … --zakuro …`, then Cargo. The generated program still requires the local game data. The launcher deliberately refuses `--run` until a verified backend and game-specific input contract are integrated. No silent interpreter fallback is presented as a native-only port.

## Save import

```sh
python3 tools/saves.py /path/to/user/main --game y
```

Each import creates a unique private backup, verifies SHA-256 after copying, and never replaces a previous backup. It does not validate save format, migrate between versions, or attach a save to a running game. Save/load safety in retail Pokémon remains unverified.

## Evidence and next gate

See [development status](docs/STATUS.md), [upstream audit](docs/UPSTREAM.md), and [timing and validation plan](docs/TIMING.md). GitHub Actions covers launcher builds/tests on macOS ARM64 and Windows x64; a workflow definition is not evidence of a passing hosted build.
