---
name: uipack-design
description: >-
  Build, restyle or review a visual in the owner's UiPack design system: slides or a talk deck, a
  landing, product, docs or dashboard page, a diagram for a site or article, a motion explainer or
  a 3D hero, its copy, or a site's style spec. Use for "make slides", "landing page", "in our
  style", "on brand", "use uipack", "swap the style", "make it not look AI-generated", "new site",
  "review this page", or any visual in a repo that depends on uipack. Not for: data charts alone
  (dataviz), a UX audit alone (ux-design), Blender installs.
---

# UiPack design (router)

UiPack (`github:ong6/uipack`) is the design manager for every site that uses it. Its guidance
ships inside the package, versioned with the code: one skill per job in `skills/`, the rules in
`docs/`. This skill only finds the right one; it holds no design rules of its own. "Our style",
"house style" and "on brand" in this user's projects mean UiPack, even when it isn't named.

## 1. Find UiPack

In order: the repo's `node_modules/uipack/`, a local uipack clone (a `uipack` folder near the
user's other projects), or GitHub (`https://github.com/ong6/uipack`, raw files under
`https://raw.githubusercontent.com/ong6/uipack/main/`). Call that folder `UIPACK`. A project that
should use it but lacks it: `npm install github:ong6/uipack`.

## 2. Identify the site and its spec

- The repo's `STYLE.md` is the site's spec; else find the site in `UIPACK/docs/specs/registry.md`.
- No spec, or the registry marks it TODO: the job starts with the site spec (row d below) unless the
  user only wants a diagram, which needs no spec.
- Layers, most general first: core rules (`UIPACK/docs/system/`, every site) → the site spec
  (brand, its own layout and writing style) → component looks (`UIPACK/docs/components/`; a spec
  picks them, `fixed` looks such as the Blueprint diagrams are identical on every site).

## 3. Pick the job and read its skill

Read `UIPACK/docs/agents/README.md`, then the job's skill, and follow it:

| Job | Read |
| --- | --- |
| (a) A page or deck: landing, docs/article, deck, dashboard, 3D hero | `UIPACK/skills/uipack-page/SKILL.md` |
| (b) A diagram or figure | `UIPACK/skills/uipack-diagram/SKILL.md` |
| (c) Copy only: titles, notes, web copy, captions | `UIPACK/skills/uipack-copy/SKILL.md` |
| (d) A new site, or changing a site's look | `UIPACK/skills/uipack-spec/SKILL.md` |
| (e) Review, grade or self-check before hand-off | `UIPACK/skills/uipack-review/SKILL.md` |
| A whole site split across agents | `UIPACK/docs/agents/multi-agent-build.md` |

A request spanning jobs runs them in order: spec, copy, page or diagram, review.

If `UIPACK/skills/` is missing (an older pinned uipack), read `UIPACK/AGENTS.md` and
`UIPACK/docs/system/README.md`, and say the pin predates the skills.

## Executors

The uipack skill owns the design rules; these execute when it hands off: `system-diagram` for a
hand-authored SVG figure, `create-fde-deck` for customer field-engineering decks, `frontend-design`
and `ux-design` for web direction and the usability pass, `3d-design` then `blender-authoring` for
3D.

## Never

- Restate or work from memory of UiPack rules; read them from `UIPACK` for this version.
- Apply one site's values to another site, or the site's brand to a `fixed` component look.
- Invent an export, prop, command or path; check `UIPACK/dist/*.d.ts` and the docs.
- Report a render, grade or test you did not run.
