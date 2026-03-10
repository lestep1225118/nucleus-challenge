## Nucleus Calculator

A small calculator web application built for the Nucleus Security engineering intern exercise.

### Stack

- Backend: Python + Flask
- Frontend: HTML + CSS + vanilla JavaScript
- Features:
  - Basic arithmetic (+, −, ×, ÷, parentheses, powers)
  - Safe server-side evaluation of expressions (no `eval`)
  - Simple, modern UI

### Running locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

