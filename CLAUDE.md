# MatCompat Pro — Claude Instructions

## Project Location
`C:\Users\HP\Desktop\material-dashboard\`

## What This App Does
A professional **Material Compatibility & Production Risk Dashboard** built with Python + Streamlit.
Allows a Production Engineer to:
- Select two industrial materials and get a compatibility analysis
- See a Risk Score (1–10), Go/No-Go verdict, CTE delta, galvanic risk, and supply chain risk
- Ask Claude Opus 4.6 specific production engineering questions about the pairing

## Stack
- **Python 3.13** — `C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe`
- **Streamlit 1.55.0** — UI framework
- **Plotly 6.6.0** — Gauge chart for risk score
- **Anthropic 0.86.0** — Claude API integration
- **python-dotenv 1.2.2** — Env var support (optional)

## How to Run
```bash
cd C:\Users\HP\Desktop\material-dashboard
python -m streamlit run app.py --server.port 8501 --server.headless true
```
Then open: http://localhost:8501

## File Structure
```
material-dashboard/
  app.py            # Main Streamlit app (all logic in one file)
  requirements.txt  # pip dependencies
  CLAUDE.md         # This file
```

## Key Design Decisions
- **All ASCII** — No Unicode/emoji in app.py (causes cp1252 decode errors on Windows)
- **No `'use strict'`** — JS-only convention, breaks Python on Windows Streamlit
- **CSS targets specific components only** — Overriding stAppViewContainer breaks rendering
- **Streamlit config** at `C:\Users\HP\.streamlit\config.toml`:
  ```toml
  [browser]
  gatherUsageStats = false
  [server]
  headless = true
  ```

## Materials Covered (8 total)
1. 316 Stainless Steel
2. PEEK
3. Nitrile (NBR)
4. Aluminum 6061
5. Titanium Grade 5
6. Inconel 625
7. PTFE
8. Carbon Steel A36

28 pairings pre-calculated in `COMPAT_MATRIX` dict (symmetric lookup).

## Claude Integration
- Model: `claude-opus-4-6`
- Thinking: `{"type": "adaptive"}`
- Max tokens: 1024
- System prompt: Senior material science / production engineering consultant
- API key entered by user in sidebar at runtime (not stored)

## Bugs Fixed
1. **Blank screen on load** — Caused by non-ASCII chars (emoji, box-drawing) in app.py + aggressive CSS overrides
2. **Port conflict** — Multiple Streamlit processes were launched; use `taskkill /PID <pid> /F` to clear
3. **pip lock error** — Background pip process held pandas .pyd file; fixed with `pip install --user`

## Next Steps / Ideas
- Add file upload (spec sheet PDF → extract materials via Claude)
- Export report as PDF
- Add more materials to the matrix
- Add temperature range input for context-aware risk scoring
- Persist chat history for Consult Claude section
