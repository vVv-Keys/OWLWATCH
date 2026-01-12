from __future__ import annotations
import argparse
from datetime import datetime, date
from pathlib import Path
import sys
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("owlwatch")

ROOT = Path(__file__).parent.resolve()
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"
STATE_DIR = ROOT / "state"

LAST_RUN_FILE = STATE_DIR / "last_run.txt"
DEFAULT_TEMPLATE = "daily.md"


def render_template(template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(),  # harmless for markdown
        keep_trailing_newline=True,
    )
    template = env.get_template(template_name)
    return template.render(context)


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def write_output(content: str, target_path: Path, force: bool = False) -> bool:
    if target_path.exists() and not force:
        logger.info("Target already exists: %s (use --force to overwrite)", target_path)
        return False
    target_path.write_text(content, encoding="utf-8")
    logger.info("Wrote output: %s", target_path)
    return True


def update_last_run(ts: datetime) -> None:
    LAST_RUN_FILE.write_text(ts.isoformat(), encoding="utf-8")
    logger.debug("Updated last run file: %s", LAST_RUN_FILE)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render daily template to output")
    p.add_argument("--date", "-d", help="Date to render (YYYY-MM-DD). Default: today")
    p.add_argument("--template", "-t", default=DEFAULT_TEMPLATE, help="Template filename in templates/")
    p.add_argument("--force", "-f", action="store_true", help="Overwrite existing file")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ensure_dirs()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD.")
            return 2
    else:
        target_date = date.today()

    iso = target_date.isoformat()
    pretty = target_date.strftime("%A, %B %d, %Y")

    context = {
        "date": iso,
        "pretty_date": pretty,
        "year": target_date.year,
        "month": target_date.month,
        "day": target_date.day,
    }

    try:
        content = render_template(args.template, context)
    except Exception as e:
        logger.error("Failed to render template %s: %s", args.template, e)
        return 3

    target_file = OUTPUT_DIR / f"{iso}.md"
    ok = write_output(content, target_file, force=args.force)
    if not ok:
        return 0

    update_last_run(datetime.utcnow())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())