#!/usr/bin/env bash
set -euo pipefail
# Execute a notebook headlessly and write an HTML copy next to it.
python -m pip install -r config/requirements.txt
NOTEBOOK="${1:-notebooks/DreamBooth_Stable_Diffusion.ipynb}"
jupyter nbconvert --to html "$NOTEBOOK" --ExecutePreprocessor.timeout=600 --execute
