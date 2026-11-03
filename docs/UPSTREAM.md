# Source inspection — 2026-11-03

Public Git checkouts inspected directly; no upstream code copied into this project's source.

- [3dsrecomp](https://github.com/fearkov/3dsrecomp), commit `73b8f9caf3700991c290dd84bccffb92294d6b15`: Cargo declares MIT, Rust >=1.88. No top-level LICENSE text at this commit; preserve provenance and obtain the full notice before redistributing upstream code. README documents Linux/Windows, not verified macOS support. Actual macOS ARM64 release build succeeded here. Its port generator links translated code into Zakuro; remaining instructions may use its interpreter. An ARM64 host binary does not prove a retail port works.
- [Zakuro](https://github.com/fearkov/zakuro), commit `781b4a816e1001977bb76221feab13c43185cbab`: MIT license text present; Rust >=1.95. Uses winit/glutin, OpenGL and Vulkan; macOS-specific camera and path branches exist. Those branches alone do not establish a successful macOS build or Metal game renderer. Our launcher's Metal renderer is SDL3 and is separate from Zakuro's GPU implementation.
- [Nebby](https://github.com/gradenGnostic/Nebby), commit `2e0477382696af505b32a219c3bc87dd64749552`: original launcher MIT; native runtime includes GPL-3.0-or-later TriAevum and separately licensed donor components. Do not treat the entire repository as MIT. README says Linux tested, Windows untested, Android in development; no macOS execution evidence established in this audit. Native Moon and Alpha Sapphire statements are upstream claims, not our validation. No Nebby runtime is incorporated.
- SDL3: launcher links the installed SDL3 library; bundled copy retains SDL's license (zlib). See `docs/SDL-LICENSE.txt`. No Pokémon graphics or Nintendo branding assets are included.

Decision: own minimal C++20 SDL3 frontend; external pinned Rust 3dsrecomp/Zakuro pipeline for Y first. Defer Nebby native runtime adoption until renderer portability and combined licensing are evaluated.
