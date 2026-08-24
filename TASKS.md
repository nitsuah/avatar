# Tasks

## Done

- [x] Identify repo purpose — DreamBooth fine-tuning on Stable Diffusion v1-5 via Jupyter notebook on Google Colab.
- [x] Add `requirements.txt` — available at `config/requirements.txt`.
- [x] Add README with "how to run the notebook" and expected outputs.
- [x] Extract testable utilities to `avatar/utils.py` (concepts list, image validation, training command builder).
- [x] Create `tests/test_utils.py` — 24 tests covering all utility functions.
- [x] Achieve 100% coverage of `avatar/utils.py`.
- [x] Set up Docker for local development (test + notebook stages).
- [x] Configure pre-commit hooks (ruff, black, flake8, isort, pytest-on-push).
- [x] Set up GitHub Actions CI (lint + test on push/PR to main).

## In Progress

- [ ] Clarify Python version matrix — CI uses 3.9, Dockerfile uses 3.11, `pyproject.toml` targets 3.10; align to one supported version.

## Todo

- [ ] Add dataset validation cell to notebook — surface a clear error when image count is outside the 3–10 recommended range before training starts.
- [ ] Add model evaluation step to notebook — compute CLIP similarity score between generated samples and training images to quantify output quality.
- [ ] Add `nbconvert` step to CI — execute the notebook headlessly to catch broken cells (guard with `@pytest.mark.notebook` or a separate workflow job).
- [ ] Export notebook to `examples/DreamBooth_Stable_Diffusion.html` so users can preview the workflow without running Colab.
- [ ] Document the `build_training_command` utility in README — show how to use it to reproduce the training command locally.
- [ ] Add Gradio or Streamlit inference UI — wrap the trained model in a simple web form for non-technical users.
- [ ] Pin exact versions in `config/requirements.txt` (currently unpinned — adds risk of breakage on fresh installs).
- [ ] Add a `CONTRIBUTING.md` entry (or link to `nitsuah/.github`) to the local repo root for discoverability.
- [ ] Create `run_notebook.sh` helper script:

```bash
#!/usr/bin/env bash
python -m pip install -r config/requirements.txt
NOTEBOOK="${1:-notebooks/DreamBooth_Stable_Diffusion.ipynb}"
jupyter nbconvert --to html "$NOTEBOOK" --ExecutePreprocessor.timeout=600 --execute
```

<!--
AGENT INSTRUCTIONS:
This file tracks specific actionable tasks.
1. Categorize tasks into "Todo", "In Progress", and "Done".
2. Add new tasks identified during code analysis or planning.
3. Mark tasks as [x] when verified as complete.
4. Keep task descriptions concise but actionable.
-->
