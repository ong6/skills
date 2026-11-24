#!/usr/bin/env python3
"""Record which model proved each skill, and list the skills whose proof no longer holds.

A proof is one kept gate decision: a skill's exact content, the model that ran it and the date.
`record` appends one after the gate keeps a candidate. `stale` compares every skill on disk with
its latest kept proof and says which need the gate again: never proven, proven on another model, or
edited since. It never calls a model.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys


SKIPPED = {"__pycache__", "tests", "evals", "node_modules", ".venv", "venv", ".DS_Store"}
DECISIONS = ("keep", "retire", "restore")
# Worst first: this is the order in which skills need the gate again.
STATES = ("never proven", "other model", "edited since proof", "current")


def skill_hash(skill_dir: Path) -> str:
    """Hash every file the agent can load: relative path plus content, tests and caches left out."""
    digest = hashlib.sha256()
    for path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
        relative = path.relative_to(skill_dir)
        if SKIPPED.intersection(relative.parts):
            continue
        digest.update(relative.as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode() + b"\n")
    return digest.hexdigest()


def load(ledger: Path) -> dict:
    if not ledger.exists():
        return {"version": 1, "proofs": []}
    data = json.loads(ledger.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("proofs"), list):
        raise ValueError(f"{ledger} is not a version 1 proof ledger")
    return data


def record(ledger: Path, skill_dir: Path, models: list[str], decision: str, evidence: str,
           date: str, sha256: str | None = None) -> dict:
    if not (skill_dir / "SKILL.md").is_file() and sha256 is None:
        raise ValueError(f"{skill_dir} has no SKILL.md")
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {', '.join(DECISIONS)}")
    datetime.date.fromisoformat(date)
    entry = {"skill": skill_dir.name, "sha256": sha256 or skill_hash(skill_dir),
             "models": sorted(set(models)), "decision": decision, "date": date, "evidence": evidence}
    data = load(ledger)
    data["proofs"].append(entry)
    ledger.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return entry


def discover(roots: list[Path]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for root in roots:
        for skill_file in sorted(root.glob("*/SKILL.md")):
            found.setdefault(skill_file.parent.name, skill_file.parent)
    return found


def stale(ledger: Path, roots: list[Path], models: list[str], usage: dict | None = None) -> list[dict]:
    """One row per skill on disk, the ones needing the gate first and the most used first within those."""
    latest: dict[str, dict] = {}
    for proof in load(ledger)["proofs"]:
        if proof["decision"] != "keep":
            continue
        if proof["skill"] not in latest or proof["date"] >= latest[proof["skill"]]["date"]:
            latest[proof["skill"]] = proof
    rows = []
    for name, folder in discover(roots).items():
        proof = latest.get(name)
        missing = sorted(set(models) - set(proof["models"])) if proof else sorted(models)
        if proof is None:
            state = "never proven"
        elif missing:
            state = "other model"
        elif proof["sha256"] != skill_hash(folder):
            state = "edited since proof"
        else:
            state = "current"
        used = (usage or {}).get(name, {})
        rows.append({"skill": name, "state": state, "proven_on": proof["models"] if proof else [],
                     "proven_date": proof["date"] if proof else None, "unproven_models": missing,
                     "edited": bool(proof) and proof["sha256"] != skill_hash(folder),
                     "days_used": used.get("days_used", 0), "last_used": used.get("last"),
                     "path": str(folder)})
    rows.sort(key=lambda r: (STATES.index(r["state"]), -r["days_used"], r["skill"]))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("record", help="append one gate decision")
    add.add_argument("--ledger", type=Path, required=True)
    add.add_argument("--skill-dir", type=Path, required=True)
    add.add_argument("--model", action="append", required=True, help="repeat for each model the gate passed on")
    add.add_argument("--decision", choices=DECISIONS, default="keep")
    add.add_argument("--evidence", required=True, help="where the evaluation bundle is kept")
    add.add_argument("--date", default=datetime.date.today().isoformat())
    add.add_argument("--sha256", help="hash of the proven content when it is no longer what is on disk")
    check = commands.add_parser("stale", help="list skills whose proof does not cover the given models")
    check.add_argument("--ledger", type=Path, required=True)
    check.add_argument("--skills", type=Path, action="append", required=True,
                       help="a folder of skill folders; repeat for each tier or checkout")
    check.add_argument("--model", action="append", required=True, help="repeat for each model that runs skills")
    check.add_argument("--usage", type=Path, help="JSON with a top-level 'skills' map carrying days_used and last")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "record":
            print(json.dumps(record(args.ledger, args.skill_dir.resolve(), args.model, args.decision,
                                    args.evidence, args.date, args.sha256), indent=2))
            return 0
        usage = json.loads(args.usage.read_text(encoding="utf-8")).get("skills", {}) if args.usage else None
        rows = stale(args.ledger, args.skills, args.model, usage)
    except (OSError, ValueError, KeyError) as error:
        print(f"proof_ledger: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            proven = f"{', '.join(row['proven_on'])} on {row['proven_date']}" if row["proven_on"] else "-"
            edited = " (also edited)" if row["edited"] and row["state"] == "other model" else ""
            print(f"{row['state']:<19} {row['skill']:<24} used {row['days_used']:>3} d  proven: {proven}{edited}")
    return 1 if any(row["state"] != "current" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
