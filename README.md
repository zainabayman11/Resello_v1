# Explainable Dynamic Pricing — Prototype

Run the Streamlit prototype (2-view) locally. This minimal prototype uses CLIP for simple view checks and damage detection.

Setup

1. Create a Python environment and install requirements:

```bash
python -m venv .venv
.
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```

Notes
- The prototype adds a "Prototype (2 views)" mode for quick testing.
- `cv_utils.py` loads a CLIP model from Hugging Face; the first run downloads model weights.
- LLM-based explanation is left as a placeholder string; integrate a local LLaMA or external API later.
