# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-15

### Added

- Configurable Docker base image through the `BASE_IMAGE` variable in
  `build-config`.
- Dedicated `custom/` folder for build customization files
  (`pre-install.sh`, `requirements.txt`, `post-install.sh`).
- README documentation for the prebuilt releases, the compression variants
  and the base image option.
- This changelog.

### Changed

- Default base image is now `python:3.12.8-bullseye` (GLIBC 2.31), so a
  single runtime runs on both older-libc devices (for example MinUI) and
  newer CFWs (for example Knulli).
- Build customization files are now read from `custom/` instead of `build/`,
  so they are no longer removed by `make clean`.

## [0.2.0] - 2026-07-14

### Added

- gzip-compressed runtime variant, built alongside the xz image, for device
  kernels without xz SquashFS support. The compressions are configured via
  the `COMP` variable in `build-config`.

## [0.1.0] - 2026-07-14

First public release: a portable, self-contained pygame-ce runtime packaged
as a SquashFS image for Linux based handheld game consoles.

### Added

- arm64 pygame-ce runtime, built in a Debian based Docker container and
  packed into an xz-compressed SquashFS image.
- `make build-package` target that bundles the runtime, the example game and
  a PortMaster-compatible startup script into `MyGame.zip`.
- Example game demonstrating controller/keyboard input, a Tiled map loaded
  with PyTMX, and on-screen system and joystick information.
- Hooks to customize the runtime (`pre-install.sh`, `requirements.txt`,
  `post-install.sh`).
- GitHub Actions workflow that builds on a native arm64 runner and publishes
  the runtime and package as release assets on tag push.
- Runtime versions sourced from `build-config`.

[0.3.0]: https://github.com/viniciusfs/pygame-ce-runtime/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/viniciusfs/pygame-ce-runtime/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/viniciusfs/pygame-ce-runtime/releases/tag/v0.1.0
