# owlwatch
----
INSTRUCTIONS BELOW BUT AM ADDING OFFICIAL COVER PAGE ONCE COMPLETE 
----
Small automation to render daily notes from a template into `output/` and/or post OWLWATCH summaries to Discord.

Files:
- `owlwatch_automation.py` – renders `templates/daily.md` into `output/YYYY-MM-DD.md`
- `owlwatch_report.py` – generates an OWLWATCH report and posts to Discord
- `templates/daily.md` – Jinja2 template used for daily notes
- `requirements.txt` – Python dependency list
- `.github/workflows/owlwatch.yml` – GitHub Actions workflow for scheduled runs
- `output/` – created by scripts or GitHub Actions to store generated files
- `state/` – created by scripts or GitHub Actions for idempotency/last-run tracking

## Quickstart (local)

1. Create a virtual environment and install requirements:

       python -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt

2. Run the report/posting script (configure the webhook environment variables):

       export OWLWATCH_WEBHOOK_URL="https://discord.com/api/webhooks/..."
       export OWLWATCH_RUN_SLOT=AM
       python owlwatch_report.py

3. Or render the daily template locally:

       python owlwatch_automation.py

## CI / GitHub Actions

Workflows are provided in `.github/workflows/`. Ensure you add the repository secret:

- `OWLWATCH_DISCORD_WEBHOOK` (or set `OWLWATCH_WEBHOOK_URL` / `OWLWATCH_WEBHOOK_URLS`)

## Customization

- Edit `templates/daily.md` to change the daily note format or modify `build_report()` in `owlwatch_report.py` to adjust the report contents.
- Both scripts write artifacts to `output/` and use `state/` for idempotency/last‑run tracking.
