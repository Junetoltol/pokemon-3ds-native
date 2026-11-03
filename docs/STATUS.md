# Development evidence — 2026-11-03

## 실제 구현 완료

- Independent C++20/SDL3 launcher, eight named profiles with Y initially selected.
- Common runtime interface with explicit mock capability; no game backend registered.
- Display FPS and synthetic guest-time separation, keyboard and gamepad profile selection.
- Private local port driver: expected SHA-256/program-ID checks, pinned clean upstream checkout checks, user-declared version explicitly unverified, generation/build commands.
- Unique save import backups with copy hash verification. No live game/save integration.
- macOS bundle dependency packaging and ad-hoc signing; Windows DLL copy rules.
- CI definition for macOS ARM64 and Windows x64 builds/tests.

## 빌드 검증 완료

- Host reports Darwin arm64, AppleClang 21.0.0. M4 model was not independently checked.
- CMake Release launcher `.app`, Mach-O arm64; SDL3 copied into distributable bundle.
- Local project-only Rust stable 1.99.1 installed without modifying shell profiles.
- 3dsrecomp pinned revision: release build succeeded; 62 unit tests + 1 doc test passed.
- Zakuro pinned revision: `cargo build --release --locked -p zakuro` succeeded (75 seconds). Dependency `block 0.1.6` reports a future Rust incompatibility warning.
- Self-authored return-only synthetic NCCH: upstream `port` generated C, compiled static archive, and generated a local Cargo project. No retail input used.

## 실행 검증 완료

- Launcher SDL3 Metal window loop: 30 frames, clean exit. Packaged app also completed a 30-frame Metal window smoke run.
- Headless mock: 600 display frames at 60 FPS / 8× produced 2400 synthetic ticks.
- CTest: runtime-contract and local-tools passed. Runtime checks cover 30/60 × 1/2/4/8; tool tests cover header rejection and non-overwriting backups.
- Real-game launch deliberately exits with status 3 rather than using a fake game screen.

## 미검증

- Pokémon Y retail conversion, boot, field/battle/event correctness, game-specific 60 FPS patches, real 2×/4×/8× speed, audio, save/load and stability.
- All other seven games; Windows build/execution until hosted CI completes; controller/touch game input.
- Trusted regional/version manifests and independent version certification. Current hash checks only match caller-provided values.
- Runtime ABI integration and game-specific settings persistence; the current interface is C++ and mock stepping only.
- Actual game benchmarks, performance percentile logging, unattended retail test harness, notarized distribution.

## 기술적 장애

- No user-owned Y dump is available. User will prepare one; no game input is downloaded or fabricated.
- A decrypted NCSD `.3ds`/`.cci` base-game dump is preferred for first Y test; include known region, language and version. The header also supports standalone NCCH `.cxi`. CIA is intentionally rejected by this wrapper.
- No Pokémon performance or compatibility claim can be made from synthetic tests or an upstream build.

## Next implementation gate

Obtain and fingerprint the user's Y dump privately; validate region/title/version independently, invoke the local pipeline, record boot/renderer failures, then implement a versioned game backend contract. Add persistent settings and measured telemetry before expanding games or enabling retail timing patches.
