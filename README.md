# Bug Report Triage Bot

AI-powered bug report quality analyser. Scores incoming bug reports against 
a 7-point rubric, classifies severity and category, suggests the responsible 
team, and rewrites vague titles into actionable ones.

## Why this exists

QA teams waste hours triaging low-quality bug reports that are missing 
reproduction steps, environment details, or expected behaviour. This tool 
gives instant feedback so reporters know what's missing before a ticket 
reaches the engineering team.

## Demo

**Try the live app:** [ramya-bug-triage-bot.streamlit.app](https://ramya-bug-triage-bot.streamlit.app)

The tool reliably distinguishes vague reports from well-structured ones:

| Input | Quality Score | Severity | Category |
|---|---|---|---|
| "App crashes when I click the button" | 12 / 100 | High | Other |
| Detailed report with steps, environment, logs | 92 / 100 | Critical | Auth |

## How it works

1. User pastes a bug report into the Streamlit UI
2. The text is sent to Claude (Haiku 4.5) with a structured 7-point rubric
3. Claude returns a JSON response via tool use, guaranteeing schema-conformant output
4. Pydantic validates the response against a strict schema
5. The UI renders quality score, severity, category, suggested owner, missing fields, and improvement suggestions

## Tech stack

- **Python 3.11**
- **Anthropic Claude API** (Haiku 4.5) with tool use for structured output
- **Pydantic** for schema validation and type safety
- **Streamlit** for the web UI
- **Rich** for the CLI

## Run locally

```bash
git clone https://github.com/RamyashreePR/bug-triage-bot.git
cd bug-triage-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
echo ANTHROPIC_API_KEY=your-key-here > .env
streamlit run app.py
```

## Project structure

```
bug-triage-bot/
├── triage.py          # Core engine: Claude call + Pydantic schema
├── app.py             # Streamlit web UI
├── requirements.txt   # Python dependencies
├── .env               # API key (not committed)
└── README.md
```

## Author

Ramya Shree Renukaiah - QA Engineer with experience in manual testing, REST API validation, and AI quality assurance.

[LinkedIn](https://linkedin.com/in/ramyashree-r-022242213)
