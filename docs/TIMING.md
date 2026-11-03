# Timing contract and retail validation gates

The current runtime interface exposes synthetic stepping and an explicit `is_game()` capability. Its mock always returns false. Guest clock is fixed at 30 synthetic ticks/second; speed multiplies elapsed guest time. Display pacing at 30/60 FPS is independent. Unit tests exercise 10 simulated seconds at all eight combinations. These tests neither benchmark CPU/GPU performance nor establish a Pokémon title's actual guest tick rate.

For real integration, expose input, audio, frame-ready, save-quiescence and error capabilities through a versioned backend ABI. Run guest scheduling independently from presentation with bounded catch-up and explicit overload telemetry. Real 60 FPS requires per-title/version patches and animation/event checks; doubling guest execution is not that patch. Define whether audio resamples or mutes at each speed. No retail 60 FPS or speed toggle is enabled today.

Y validation matrix before expansion: region + title ID + base version + updates + dump hash; renderer/OS/architecture; intro, field movement, battles, cutscenes, menus and event triggers; audio synchronization; save/load and repeated backup restoration; 30/60 display × 1/2/4/8 speed. Compare game-time and wall-time, event completion, animation duration and semantic save state. Keep test saves private. Record failures as failures.

Performance protocol: fixed scene/save, warmup, at least three runs, hardware/OS/renderer/toolchain versions, power and thermal state, wall duration, guest frame counts, frame-time percentiles and memory use. Synthetic clock arithmetic is excluded from game performance claims. 60 FPS, 4× and 8× remain unmeasured. Windows must pass the same runtime and save gates independently.
