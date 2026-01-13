from __future__ import annotations

import os
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import pytz
import requests


@dataclass(frozen=True)
class OwlwatchReport:
    date_label: str
    date_iso: str
    run_slot: str
    tz_label: str
    title: str
    executive_summary: str
    critical_alerts: List[str]
    threat_landscape: str
    technical_intel: List[str]
    iocs: List[str]
    industry_impact: List[str]
    defensive_actions: List[str]
    detections_hunts: List[str]
    trend_analysis: str
    patch_priorities: List[str]
    attribution_scoring: str
    playbook_updates: List[str]
    sources: List[str]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def now_local(tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    safe_mkdir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_webhooks() -> List[str]:
    urls: List[str] = []
    single = env("OWLWATCH_WEBHOOK_URL")
    if single:
        urls.append(single)
    many = env("OWLWATCH_WEBHOOK_URLS")
    if many:
        urls.extend([u.strip() for u in many.split(";") if u.strip()])
    # dedupe
    out: List[str] = []
    for u in urls:
        if u not in out:
            out.append(u)
    return out


def clamp(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def bullets(items: List[str], max_items: int = 999) -> str:
    if not items:
        return "- None"
    items = items[:max_items]
    return "\n".join([f"- {x}" for x in items])


def render_markdown(r: OwlwatchReport) -> str:
    return f"""# {r.title}
**Date:** {r.date_label} ({r.tz_label})
**Run Slot:** {r.run_slot}

## Executive Summary
{r.executive_summary}

## Critical Alerts
{bullets(r.critical_alerts)}

## Threat Landscape
{r.threat_landscape}

## Technical Intelligence
{bullets(r.technical_intel)}

## Technical Intelligence with IoCs
{bullets(r.iocs)}

## Industry Impact
{bullets(r.industry_impact)}

## Defensive Actions
{bullets(r.defensive_actions)}

## Detection & Hunts
{bullets(r.detections_hunts)}

## Trend Analysis
{r.trend_analysis}

## Patch Priorities
{bullets(r.patch_priorities)}

## Attribution Confidence & Threat Scoring
{r.attribution_scoring}

## Playbook Updates
{bullets(r.playbook_updates)}

## Sources to Monitor
{bullets(r.sources)}
"""


def render_discord_payload(r: OwlwatchReport) -> dict:
    max_alerts = int(env("OWLWATCH_MAX_ALERTS", "8") or "8")
    desc = (
        f"Date: {r.date_label} ({r.tz_label})\n"
        f"Run: {r.run_slot}\n\n"
        f"{clamp(r.executive_summary, 900)}"
    )

    fields = [
        {"name": "Critical Alerts", "value": clamp(bullets(r.critical_alerts, max_alerts), 1024), "inline": False},
        {"name": "Defensive Actions", "value": clamp(bullets(r.defensive_actions, 8), 1024), "inline": False},
        {"name": "Patch Priorities", "value": clamp(bullets(r.patch_priorities, 8), 1024), "inline": False},
        {"name": "Detection & Hunts", "value": clamp(bullets(r.detections_hunts, 8), 1024), "inline": False},
    ]

    return {
        "content": "",
        "embeds": [
            {
                "title": clamp(r.title, 256),
                "description": clamp(desc, 4096),
                "fields": fields,
                "footer": {"text": "KeysGuard OWLWATCH"},
            }
        ],
        "allowed_mentions": {"parse": []},
    }


def post_discord(webhook_url: str, payload: dict) -> None:
    resp = requests.post(webhook_url, json=payload, timeout=25)
    if resp.status_code >= 300:
        raise RuntimeError(f"Discord webhook failed: {resp.status_code} {resp.text}")


def build_report(tz_name: str, run_slot: str) -> OwlwatchReport:
    now = now_local(tz_name)
    date_label = now.strftime("%B %d, %Y")
    date_iso = now.strftime("%Y-%m-%d")

    title = env("OWLWATCH_TITLE", "KEYSGUARD OWLWATCH — Daily Cyber Intelligence Brief")

    # You can later swap this builder to pull from your intel pipeline / feeds.
    # This keeps the baseline structure stable for automation.
    exec_summary = (
        "Operational risk remains elevated. Primary drivers include trusted-infrastructure abuse for credential capture, "
        "KEV-prioritized exploitation pressure, and identity hygiene gaps that enable rapid access and persistence."
    )

    # AM vs PM: allow slightly different emphasis if you want
    if run_slot.upper() == "AM":
        exec_summary = (
            "Morning posture: prioritize patch validation, identity hygiene, and new phishing infrastructure. "
            + exec_summary
        )
    else:
        exec_summary = (
            "Evening posture: review detection outcomes, confirm remediation closure, and assess overnight exploitation risk. "
            + exec_summary
        )

    return OwlwatchReport(
        date_label=date_label,
        date_iso=date_iso,
        run_slot=run_slot.upper(),
        tz_label=tz_name,
        title=title,
        executive_summary=exec_summary,
        critical_alerts=[
            "Trusted cloud and SaaS sender abuse increasing delivery success for credential capture",
            "KEV-driven exploitation pressure persists against management and identity surfaces",
            "Credential replay and token reuse remain top causes of secondary compromise",
        ],
        threat_landscape=(
            "Initial access is dominated by phishing and credential abuse, with attackers optimizing trust signals and low-noise execution "
            "paths rather than relying on novel malware families."
        ),
        technical_intel=[
            "HTML and archive-based delivery chains followed by script proxy execution",
            "Living-off-the-land execution via native binaries and scripting engines",
            "Cloud token and OAuth permission misuse enabling persistence",
        ],
        iocs=[
            "Populate with campaign-specific senders/domains/URLs from your telemetry",
            "Populate with prioritized CVEs and exposed surfaces from your environment",
        ],
        industry_impact=[
            "SaaS-heavy organizations face elevated identity compromise risk without strict OAuth governance",
            "Organizations with patch lag remain exposed to exploit-in-the-wild pressure",
        ],
        defensive_actions=[
            "Audit OAuth app grants and revoke high-privilege permissions not explicitly required",
            "Validate patch completion for prioritized surfaces; close exceptions with compensating controls",
            "Increase monitoring for LOLBin execution and abnormal parent-child process chains",
        ],
        detections_hunts=[
            "Hunt: first-seen OAuth apps and new high-privilege grants in last 14 days",
            "Hunt: attachment open events followed by mshta/rundll32/script execution within 5 minutes",
            "Detect: suspicious command-lines containing javascript/http/.hta launched by Office or browsers",
        ],
        trend_analysis=(
            "The dominant operational trend is attacker optimization of legitimacy. Defensive advantage comes from identity hygiene, "
            "execution telemetry, and behavioral correlation rather than signature dependence."
        ),
        patch_priorities=[
            "Identity providers, SSO, and authentication infrastructure",
            "Edge devices (VPN/firewalls/remote access) and exposed management planes",
            "Email security inspection engines and attachment detonation coverage",
        ],
        attribution_scoring=(
            "Confidence: high on trusted-infrastructure abuse and credential replay patterns. Overall operational risk: elevated."
        ),
        playbook_updates=[
            "Trusted sender abuse triage: verify origin, redirect depth, destination integrity",
            "Token invalidation and session purge workflow for suspected OAuth compromise",
        ],
        sources=[
            "CISA KEV and relevant exploitation advisories",
            "Vendor patch analysis and security response updates",
            "Threat research on cloud workflow and identity abuse patterns",
        ],
    )


def main() -> None:
    tz_name = env("OWLWATCH_TZ", "America/Chicago")
    run_slot = env("OWLWATCH_RUN_SLOT", "AM").upper()
    if run_slot not in ("AM", "PM"):
        raise RuntimeError("OWLWATCH_RUN_SLOT must be AM or PM")

    out_root = Path(env("OWLWATCH_OUTPUT_DIR", "output"))
    state_root = Path(env("OWLWATCH_STATE_DIR", "state"))
    safe_mkdir(out_root)
    safe_mkdir(state_root)

    report = build_report(tz_name, run_slot)

    # Idempotency per date+slot
    report_id = sha256_text(f"{report.title}|{report.date_iso}|{report.run_slot}|{report.tz_label}")
    state_path = state_root / "owlwatch_state.json"
    state = load_json(state_path)
    posted_ids = set(state.get("posted_ids", []))

    # Write artifacts
    out_dir = out_root / report.date_iso
    safe_mkdir(out_dir)
    md_path = out_dir / f"{report.run_slot}_owlwatch.md"
    md_path.write_text(render_markdown(report), encoding="utf-8")

    # Post
    if report_id in posted_ids:
        print(f"Already posted: {report.date_iso} {report.run_slot}. Artifact saved: {md_path}")
        return

    webhooks = get_webhooks()
    if not webhooks:
        raise RuntimeError("No Discord webhook configured. Set OWLWATCH_WEBHOOK_URL or OWLWATCH_WEBHOOK_URLS.")

    payload = render_discord_payload(report)
    for url in webhooks:
        post_discord(url, payload)

    # Mark posted
    posted_ids_list = state.get("posted_ids", [])
    posted_ids_list.append(report_id)
    state["posted_ids"] = posted_ids_list[-800:]
    save_json(state_path, state)

    print(f"Posted {report.date_iso} {report.run_slot} to {len(webhooks)} webhook(s). Artifact saved: {md_path}")


if __name__ == "__main__":
    main()