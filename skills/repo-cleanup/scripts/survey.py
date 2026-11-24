#!/usr/bin/env python3
"""Survey a repository's agent-facing surface. Read-only, standard library only, never calls a model.

    python3 survey.py /path/to/repo [--json] [--mark]

Prints what every session loads, what changed since the last recorded pass, the agent-facing files
with sizes, and mechanical findings (broken links, paths that do not exist, text duplicated across
manuals, procedures and folder-specific rules sitting in the root manual, overlapping skill
descriptions, emphasis and older-model phrasing, dated attributions, folders without an index).
Findings are leads to check, not verdicts. --mark records this pass in the repository's git
directory (never committed) so the next run can report what changed since.
"""
import json
import os
import re
import subprocess
import sys
import time

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "target", ".next",
             ".pytest_cache", ".mypy_cache", "vendor", ".tox", ".idea", ".gradle", "Pods", ".terraform"}
MANUAL_NAMES = {"AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "AGENTS.override.md", "GEMINI.md", ".cursorrules",
                "copilot-instructions.md", ".windsurfrules"}
PROMPT_HINT = re.compile(r"(^|/)(prompts?|briefs?|handoffs?|kickoffs?|commands|agents)(/|$)|handoff|kickoff|brief|\.prompt\.md$", re.I)
OLD_PHRASES = [r"think step[- ]by[- ]step", r"do not hallucinate|don'?t hallucinate", r"you are an? (expert|senior|world[- ]class)",
               r"don'?t be lazy|do not be lazy|never be lazy", r"take a deep breath", r"think (very )?(hard|carefully)", r"double[- ]check everything",
               r"limited context window", r"i will tip|you will be (penali[sz]ed|fired)"]
EMPHASIS = re.compile(r"\b(MUST|NEVER|ALWAYS|IMPORTANT|CRITICAL|MANDATORY|DO NOT|REQUIRED|ABSOLUTELY)\b|!!+")
DATED = re.compile(r"\b(19|20)\d\d-\d\d(-\d\d)?\b|\b(said|asked|told us|requested|decided)\b[^.\n]{0,40}\b(on|in)\b|\bas of (january|february|march|april|may|june|july|august|september|october|november|december|\d{4})", re.I)
LINK = re.compile(r"\]\(([^)\s]+)\)")
TICKED = re.compile(r"`([^`\n]+)`")
IMPORT = re.compile(r"(?m)^\s*@([^\s`]+)")


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            yield os.path.relpath(os.path.join(d, f), root)


def tokens(text):
    return (len(text.encode("utf-8")) + 3) // 4


def frontmatter(text):
    m = re.match(r"---\n([\s\S]*?)\n---\n?", text)
    if not m:
        return {}, text
    meta, key = {}, None
    for line in m.group(1).split("\n"):
        k = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if k and not line.startswith(" "):
            key = k.group(1)
            meta[key] = k.group(2).strip().lstrip(">|-").strip().strip("\"'")
        elif key and line.strip():
            meta[key] = (meta[key] + " " + line.strip()).strip()
    return meta, text[m.end():]


def resolve_imports(root, rel, seen=None, depth=0):
    """Files pulled in by @path lines, following up to four hops as Claude Code does."""
    seen = seen if seen is not None else set()
    out = []
    if depth >= 4:
        return out
    for target in IMPORT.findall(read(os.path.join(root, rel))):
        p = os.path.normpath(os.path.join(os.path.dirname(rel), os.path.expanduser(target)))
        if p in seen or not os.path.isfile(os.path.join(root, p)):
            continue
        seen.add(p)
        out.append(p)
        out.extend(resolve_imports(root, p, seen, depth + 1))
    return out


def looks_like_path(s):
    if " " in s or len(s) > 120 or len(s) < 4 or "/" not in s:
        return False
    if re.search(r"[<>{}*$|=:@#]|\.\.\.|^(https?|git|ssh)\b|^[~/]|^-|^\.$", s):
        return False
    return bool(re.search(r"\.[A-Za-z0-9]{1,5}$", s)) or s.endswith("/")


def missing_paths(root, rel, text):
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        for tick in TICKED.findall(line):
            cand = tick.strip().split()[0] if tick.strip() else ""
            if not looks_like_path(cand):
                continue
            here = os.path.join(root, os.path.dirname(rel), cand)
            if not (os.path.exists(os.path.join(root, cand)) or os.path.exists(here)):
                out.append((n, cand))
    return out


def broken_links(root, rel, text):
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        for target in LINK.findall(line):
            t = target.split("#")[0]
            if not t or re.match(r"[a-z][a-z0-9+.-]*:", t, re.I):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(root, os.path.dirname(rel), t))):
                out.append((n, target))
    return out


def session_hooks(root):
    out = []
    for cfg in (".claude/settings.json", ".claude/settings.local.json", ".codex/hooks.json"):
        try:
            data = json.loads(read(os.path.join(root, cfg)) or "{}")
        except ValueError:
            continue
        hooks = data.get("hooks", data) if isinstance(data, dict) else {}
        for event in ("SessionStart", "UserPromptSubmit"):
            for group in hooks.get(event, []) if isinstance(hooks, dict) else []:
                for h in group.get("hooks", [group]) if isinstance(group, dict) else []:
                    cmd = h.get("command") if isinstance(h, dict) else None
                    if cmd:
                        out.append({"config": cfg, "event": event, "command": cmd[:200]})
    return out

SKILL_ROOTS = (".claude/skills", ".agents/skills", ".codex/skills", "skills")
STOP = set("this that with from when what your into over then than they them have will only also each uses used using user users skill skills agent agents not for the and use any ask asks asked make makes need needs want wants about should does page pages file files".split())


def linked_skills(root, seen_real):
    """Skills reached through a link folder. os.walk does not follow symlinked folders, so look here too."""
    rows = []
    for base in SKILL_ROOTS:
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            f = os.path.join(d, name, "SKILL.md")
            if not os.path.isfile(f):
                continue
            real = os.path.realpath(f)
            if real in seen_real:
                seen_real[real]["links"] += 1
                continue
            text = read(f)
            meta, body = frontmatter(text)
            row = {"path": os.path.join(base, name, "SKILL.md"), "bytes": len(text.encode("utf-8")), "lines": text.count("\n") + 1,
                   "tokens": tokens(text), "name": meta.get("name", ""), "description": meta.get("description", ""),
                   "description_chars": len(meta.get("description", "")), "body_lines": body.count("\n") + 1, "links": 1,
                   "outside_repo": not real.startswith(os.path.realpath(root) + os.sep)}
            seen_real[real] = row
            rows.append(row)
    return rows


def word_set(text):
    return {re.sub(r"(ing|ed|es|s)$", "", w) for w in re.findall(r"[a-z][a-z0-9-]{3,}", text.lower()) if w not in STOP}


def numbered_runs(text):
    """Longest run of numbered steps in a file: a task procedure sitting in an always-loaded manual."""
    best, start, count, first = (0, 0), 0, 0, 0
    for n, line in enumerate(text.split("\n"), 1):
        if re.match(r"\s*\d+[.)]\s+\S", line):
            if count == 0:
                first = n
            count += 1
            if count > best[0]:
                best = (count, first)
        elif line.strip() and not re.match(r"\s+\S", line):
            count = 0
    return best


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def state_path(root):
    d = git(root, "rev-parse", "--absolute-git-dir")
    return os.path.join(d, "repo-cleanup.json") if d else None


def since_last_pass(root, agent_files):
    """What changed in the agent-facing surface since the pass recorded by --mark."""
    sp = state_path(root)
    if sp is None:
        return {"status": "no git repository: treat this as a full pass"}
    try:
        with open(sp, encoding="utf-8") as fh:
            st = json.load(fh)
    except (OSError, ValueError):
        return {"status": "no earlier pass recorded: treat this as a full pass"}
    names = git(root, "diff", "--name-only", st.get("head", ""), "HEAD")
    if names is None:
        return {"status": "the earlier pass's commit is gone: treat this as a full pass", "last": st}
    dirty = git(root, "status", "--porcelain") or ""
    changed = set(n for n in names.split("\n") if n) | set(l[3:].split(" -> ")[-1].strip('"') for l in dirty.split("\n") if l.strip())
    surface = set(agent_files)
    hits = sorted(c for c in changed if c in surface or os.path.basename(c).lower() == "readme.md"
                  or c.startswith((".claude/", ".codex/", ".agents/", ".cursor/", ".github/copilot")))
    return {"status": "routine pass", "last": st, "changed_agent_facing": hits, "changed_total": len(changed)}


def mark(root, loaded_tokens):
    sp = state_path(root)
    if sp is None:
        return "not recorded (no git repository)"
    st = {"head": git(root, "rev-parse", "HEAD") or "", "date": time.strftime("%Y-%m-%d"), "always_loaded_tokens": loaded_tokens}
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(st, fh)
    return "recorded in %s" % sp


def survey(root):
    files = list(walk(root))
    md = [f for f in files if f.lower().endswith((".md", ".mdc")) or os.path.basename(f) in MANUAL_NAMES]
    manuals, skills, prompts, readmes = [], [], [], []
    for f in md:
        base = os.path.basename(f)
        text = read(os.path.join(root, f))
        row = {"path": f, "bytes": len(text.encode("utf-8")), "lines": text.count("\n") + 1, "tokens": tokens(text)}
        if base in MANUAL_NAMES or "/.claude/rules/" in "/" + f or "/.cursor/rules/" in "/" + f:
            row["imports"] = resolve_imports(root, f)
            row["symlink"] = os.path.islink(os.path.join(root, f))
            manuals.append(row)
        elif base == "SKILL.md":
            meta, body = frontmatter(text)
            row.update(name=meta.get("name", ""), description=meta.get("description", ""), description_chars=len(meta.get("description", "")),
                       body_lines=body.count("\n") + 1, links=1, outside_repo=False)
            skills.append(row)
        elif base.lower() == "readme.md":
            readmes.append(row)
        elif PROMPT_HINT.search(f):
            prompts.append(row)

    seen_real = {os.path.realpath(os.path.join(root, s["path"])): s for s in skills}
    skills.extend(linked_skills(root, seen_real))

    by_name = {}
    for sk in list(skills):
        first = by_name.setdefault(sk.get("name") or sk["path"], sk)
        if first is not sk and first.get("description") == sk.get("description"):
            first["links"] = first.get("links", 1) + 1
            skills.remove(sk)

    root_manuals = [m for m in manuals if "/" not in m["path"] or m["path"].startswith((".claude/CLAUDE.md", ".claude/rules/", ".github/"))]
    loaded, seen = [], set()
    for m in root_manuals:
        for p in [m["path"]] + m["imports"]:
            real = os.path.realpath(os.path.join(root, p))
            if real not in seen:
                seen.add(real)
                loaded.append({"path": p, "tokens": tokens(read(os.path.join(root, p)))})
    listing = sum(s["description_chars"] + len(s["name"]) for s in skills)

    findings = {"broken_links": [], "missing_paths": [], "emphasis": [], "older_model_phrasing": [], "dated_or_attributed": [],
                "duplicated_across_manuals": [], "procedure_in_root_manual": [], "folder_rules_in_root_manual": [],
                "overlapping_skill_descriptions": [], "oversize": [], "folders_without_index": [], "unlinked_from_index": []}
    agent_facing = [m["path"] for m in manuals] + [s["path"] for s in skills if not s.get("outside_repo")] + [p["path"] for p in prompts]
    tops = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and not d.startswith(".") and d not in SKIP_DIRS)
    for m in root_manuals:
        text = read(os.path.join(root, m["path"]))
        n, first = numbered_runs(text)
        if n >= 8:
            findings["procedure_in_root_manual"].append("%s:%d a %d-step procedure loads every session (a skill or a linked doc would load it on demand)" % (m["path"], first, n))
        for d in tops:
            hits = sum(1 for line in text.split("\n") if re.search(r"(^|[\s`(])%s/" % re.escape(d), line))
            if hits >= 4 and not os.path.exists(os.path.join(root, d, os.path.basename(m["path"]))):
                findings["folder_rules_in_root_manual"].append("%s: %d lines about `%s/` (a manual in that folder loads only when working there)" % (m["path"], hits, d))
    named = [s for s in skills if s.get("description")]
    for i, a in enumerate(named):
        for b in named[i + 1:]:
            wa, wb = word_set(a["description"]), word_set(b["description"])
            if wa and wb and len(wa & wb) / float(len(wa | wb)) >= 0.4:
                findings["overlapping_skill_descriptions"].append("%s and %s (%d%% of their words shared)" % (a["name"] or a["path"], b["name"] or b["path"], round(100.0 * len(wa & wb) / len(wa | wb))))
    for f in agent_facing + [r["path"] for r in readmes]:
        text = read(os.path.join(root, f))
        for n, t in broken_links(root, f, text):
            findings["broken_links"].append("%s:%d -> %s" % (f, n, t))
        for n, t in missing_paths(root, f, text):
            findings["missing_paths"].append("%s:%d `%s`" % (f, n, t))
    for f in agent_facing:
        text = read(os.path.join(root, f))
        hits = len(EMPHASIS.findall(text))
        words = max(1, len(text.split()))
        if hits >= 3 and hits * 100.0 / words >= 0.8:
            findings["emphasis"].append("%s: %d emphatic markers in %d words" % (f, hits, words))
        for n, line in enumerate(text.split("\n"), 1):
            for pat in OLD_PHRASES:
                if re.search(pat, line, re.I):
                    findings["older_model_phrasing"].append("%s:%d %s" % (f, n, line.strip()[:90]))
                    break
            if DATED.search(line) and os.path.basename(f) in MANUAL_NAMES:
                findings["dated_or_attributed"].append("%s:%d %s" % (f, n, line.strip()[:90]))
    lines_by_file = {}
    for m in manuals:
        if m["symlink"]:
            continue
        for line in read(os.path.join(root, m["path"])).split("\n"):
            norm = re.sub(r"\s+", " ", line.strip().lower())
            if len(norm) >= 40:
                lines_by_file.setdefault(norm, set()).add(m["path"])
    pairs = {}
    for norm, where in lines_by_file.items():
        if len(where) > 1:
            pairs[tuple(sorted(where))] = pairs.get(tuple(sorted(where)), 0) + 1
    for where, count in sorted(pairs.items(), key=lambda kv: -kv[1]):
        findings["duplicated_across_manuals"].append("%s share %d long lines" % (" + ".join(where), count))
    for m in manuals:
        if m["lines"] > 200:
            findings["oversize"].append("%s: %d lines (Claude Code suggests under 200 per manual)" % (m["path"], m["lines"]))
    total_manual_bytes = sum(m["bytes"] for m in root_manuals)
    if total_manual_bytes > 32 * 1024:
        findings["oversize"].append("root manuals total %d bytes (Codex stops reading at 32 KiB by default)" % total_manual_bytes)
    for s in skills:
        if s["description_chars"] > 1024:
            findings["oversize"].append("%s: description %d chars (spec limit 1024)" % (s["path"], s["description_chars"]))
        if s["body_lines"] > 500:
            findings["oversize"].append("%s: body %d lines (guides suggest under 500)" % (s["path"], s["body_lines"]))
    by_dir = {}
    for f in md:
        by_dir.setdefault(os.path.dirname(f), []).append(os.path.basename(f))
    for d, names in sorted(by_dir.items()):
        others = [n for n in names if n.lower() != "readme.md" and n not in MANUAL_NAMES and n != "SKILL.md"]
        index = next((n for n in names if n.lower() == "readme.md"), None)
        if len(others) >= 6 and not index:
            findings["folders_without_index"].append("%s/ (%d Markdown files, no README)" % (d or ".", len(others)))
        elif index and others:
            text = read(os.path.join(root, d, index))
            lost = [n for n in others if n not in text]
            if lost and len(lost) <= 12:
                findings["unlinked_from_index"].append("%s: %s" % (os.path.join(d, index), ", ".join(lost)))
    for sk in skills:
        sk.pop("description", None)
    return {"root": os.path.abspath(root), "since_last_pass": since_last_pass(root, agent_facing),
            "always_loaded": {"files": loaded, "tokens": sum(x["tokens"] for x in loaded),
            "skill_listing_chars": listing, "session_hooks": session_hooks(root)},
            "manuals": manuals, "skills": skills, "prompts_and_briefs": prompts, "readmes": readmes, "findings": findings}


def render(r):
    out = ["# Agent-facing survey: %s" % r["root"], "", "## Loaded into every session started at the root",
           "About %d tokens of manuals (bytes / 4), plus %d characters of skill names and descriptions."
           % (r["always_loaded"]["tokens"], r["always_loaded"]["skill_listing_chars"])]
    out += ["- %s (~%d tokens)" % (f["path"], f["tokens"]) for f in r["always_loaded"]["files"]]
    for h in r["always_loaded"]["session_hooks"]:
        out.append("- hook %s in %s: `%s` (its output is loaded too; run it to measure)" % (h["event"], h["config"], h["command"]))
    sl = r["since_last_pass"]
    out += ["", "## Since the last pass", sl["status"].capitalize() + "."]
    if sl.get("last"):
        out.append("Last pass %s at %s, when the manuals loaded ~%s tokens." % (sl["last"].get("date"), (sl["last"].get("head") or "")[:8], sl["last"].get("always_loaded_tokens")))
    if "changed_agent_facing" in sl:
        out.append("%d files changed since, %d of them agent-facing:" % (sl["changed_total"], len(sl["changed_agent_facing"])))
        out += ["- " + c for c in sl["changed_agent_facing"][:40]] or ["- none"]
    for title, key in (("Manuals", "manuals"), ("Skills", "skills"), ("Prompts, briefs and handoffs", "prompts_and_briefs"), ("READMEs", "readmes")):
        rows = r[key]
        out += ["", "## %s (%d)" % (title, len(rows))]
        for row in sorted(rows, key=lambda x: -x["bytes"])[:40]:
            extra = ""
            if row.get("imports"):
                extra += "; imports " + ", ".join(row["imports"])
            if row.get("symlink"):
                extra += "; symlink"
            if "description_chars" in row:
                extra += "; description %d chars" % row["description_chars"]
                if row.get("links", 1) > 1:
                    extra += "; linked from %d folders" % row["links"]
                if row.get("outside_repo"):
                    extra += "; lives outside this repository"
            out.append("- %s: %d lines, ~%d tokens%s" % (row["path"], row["lines"], row["tokens"], extra))
        if len(rows) > 40:
            out.append("- ... %d more (use --json for all)" % (len(rows) - 40))
    out += ["", "## Findings to check"]
    any_found = False
    for key, items in r["findings"].items():
        if items:
            any_found = True
            out.append("### %s (%d)" % (key.replace("_", " "), len(items)))
            out += ["- " + i for i in items[:30]]
            if len(items) > 30:
                out.append("- ... %d more (use --json for all)" % (len(items) - 30))
    if not any_found:
        out.append("None from the mechanical checks.")
    return "\n".join(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or not os.path.isdir(args[0]):
        sys.exit("usage: survey.py /path/to/repo [--json] [--mark]")
    result = survey(args[0])
    print(json.dumps(result, indent=1) if "--json" in sys.argv else render(result))
    if "--mark" in sys.argv:
        print("\nPass %s." % mark(args[0], result["always_loaded"]["tokens"]))
