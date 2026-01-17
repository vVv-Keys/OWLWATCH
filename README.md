# OWLWATCH 🦉

**A vigilant daily reporting and automation tool for cybersecurity teams.**

Owlwatch automates your morning and evening security reviews so your team stays informed and ready. It generates polished Markdown notes from a Jinja2 template, sends concise posture reports to a Discord channel, and stores artifacts for historical tracking.

## ✨ Features

- **Daily notes rendering** – Create structured daily logs from `templates/daily.md` into `output/YYYY-MM-DD.md`.
- **Threat posture reports** – Generate comprehensive AM/PM reports that summarise top priorities, recent patches, and trending attacks.
- **Discord integration** – Automatically post reports to one or more Discord channels via secure webhooks.
- **Scheduled workflows** – Use GitHub Actions to run the generator every morning and evening (8 AM / 10 PM America/Chicago).
- **Idempotent & stateful** – Scripts write artifacts to `output/` and track last run in `state/` so you never send duplicate reports.
- **Fully customisable** – Modify the Jinja2 templates or extend `build_report()` in `owlwatch_report.py` to fit your needs.

## 🚀 Quickstart

### 1. Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r owlwatch/requirements.txt
```

### 2. Run a report locally

Set your Discord webhook and optional run slot (AM or PM), then run the report script:

```bash
export OWLWATCH_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export OWLWATCH_RUN_SLOT=AM
python owlwatch/owlwatch_report.py
```

Or render the daily note template:

```bash
python owlwatch/owlwatch_automation.py
```

### 3. GitHub Actions

This repository includes a workflow in `.github/workflows/owlwatch.yml` that runs at 8 AM and 10 PM America/Chicago. To enable posting to Discord, add these secrets in **Settings → Secrets and variables → Actions**:

- `OWLWATCH_WEBHOOK_URL` – your Discord webhook URL.
- (Optional) `OWLWATCH_WEBHOOK_URLS` – a semicolon-separated list of multiple webhook URLs.

## ❤️ Contributing

We welcome ideas and contributions! Feel free to open issues or pull requests for new features, templates, or integrations.

Stay wise. Stay secure.
