# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added batch generation mode and seed interpolation roadmap items (#16).

### Changed

- Documentation audit: corrected inaccuracies in README, FEATURES.md, ROADMAP.md, and TASKS.md to accurately reflect the DreamBooth/Stable Diffusion pipeline.
- Bumped `actions/checkout` from v6 to v7 in CI (#17).
- Bumped `actions/setup-python` from v6 to v7 in CI (#18).

### Fixed

- Added explicit `contents: read` permission to CI build job to resolve GITHUB_TOKEN scope warning (#19).

### Security

## [0.1.0] - 2024-06-01

### Added
- Project initialization

[Unreleased]: https://github.com/nitsuah/avatar/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nitsuah/avatar/releases/tag/v0.1.0