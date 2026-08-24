# Roadmap

## Q1 — Foundation

- [x] Core DreamBooth pipeline (notebook + Google Colab workflow)
- [x] Initial release (v0.1.0)
- [x] Extract testable utility functions into `avatar/utils.py`
- [x] 100% test coverage of utility module (25 tests)
- [x] Docker-based local development (test + notebook services)
- [x] Pre-commit hooks (lint, format, test-on-push)
- [x] GitHub Actions CI pipeline

## Q2

- [ ] User feedback integration
- [ ] Performance improvements
- [ ] Align CI Python version (currently 3.9) with Dockerfile base (3.11) and pyproject target (3.10)
- [ ] Add dataset validation step to notebook (enforce 3–10 image limit with user-friendly output)
- [ ] Add model evaluation metrics to notebook (FID score, CLIP similarity) so output quality can be measured objectively

## Q3

- [ ] Advanced features
- [ ] **Batch generation mode** — accept a list of seed values (names, usernames, IDs) and export all generated avatars as a zip archive; useful for seeding test databases or populating user-directory mockups in one step.
- [ ] **Seed interpolation / morph frames** — given two seeds, generate an N-frame interpolation sequence between the two avatars and export as GIF or PNG strip; enables smooth avatar transition animations in UIs.
- [ ] Web UI for non-technical users (Gradio or Streamlit interface wrapping the notebook workflow)
- [ ] Support for alternative base models (Stable Diffusion XL, SDXL-Turbo)

## Q4

- [ ] Enterprise features
- [ ] Multi-user training job queue
- [ ] API endpoint for programmatic avatar generation from trained models

<!--
AGENT INSTRUCTIONS:
This file tracks the project's high-level goals.
1. Organize items by Quarter (Q1, Q2, etc.) or Milestone.
2. Mark items as [x] when completed.
3. Add new strategic goals as they emerge.
4. Ensure items are high-level features or milestones, not individual bug fixes.
-->
