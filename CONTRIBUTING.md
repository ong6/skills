# Contributing

Bug fixes and small, reusable improvements are welcome. Open an issue before adding a new skill so
the trigger boundary, portability and overlap with existing skills can be agreed first.

Each skill lives in `skills/<name>/SKILL.md` (or `rarely-used/<name>/SKILL.md` once it has been idle
for a month; `bin/skills tidy` moves it). Add it to exactly one category in `catalog.yaml` and give
it a one-line entry under `skill_summaries`. Skills found elsewhere go under a category's `links`
(`repo` or `url`, a `note`, and optionally `name`, `by`, `tags`, `from` and `from_url`). Then run:

```sh
python3 scripts/build-catalog.py          # regenerate the README tables
python3 scripts/build-catalog.py --check
python3 scripts/test-catalog.py
python3 tests/test_skills_cli.py
bin/skills guard .
python3 skills/skillsmith/scripts/lint_skill.py skills/<name>   # when skillsmith is present
```

When you change a skill's `description`, add or update its trigger cases in
`evals/triggers/<skill>-*` (one request that should load it, one near-miss that shouldn't) and run
only that skill's cases, once each, with no baseline arm:

```sh
claude plugin eval . --tag <skill> --ablation none --runs 1 --no-publish --trust-plugin
```

Rules:

- Keep personal information out: no home paths, accounts, emails, phone numbers, prices or names.
  `bin/skills guard` enforces this in CI and before `bin/skills publish` pushes.
- Make skills location-independent. Refer to other skills by name. Find the working repo with
  `git rev-parse --show-toplevel`, and never resolve a script's own symlink to find siblings.
- Never shell out to another AI CLI (`claude -p`, `codex exec`) from a skill. Use the host's own
  subagents.
- `bin/skills` stays a single stdlib-only file that runs on Python 3.7.
- The plugin manifests set no `version` on purpose: a version pins installs until it is bumped, and
  this repo publishes continuously, so installs track the commit instead. `claude plugin validate .`
  warns about it; that warning is expected.
